"""Offline fixtures exercise metadata claims, not Barometer runtime conformance."""

import copy
from contextlib import redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import check_traceability as checker


SPEC = "https://example.test/barometer-spec"
IMPL = "https://example.test/barometer-go"
REQ = "REQ-TASK-0001"
OTHER = "REQ-TASK-0002"
RETIRED = "REQ-TASK-0003"
SCOPE = "Synthetic Go task decoding"
PUBLIC_ROOT = Path(__file__).resolve().parents[1]


def git(root, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="Synthetic Fixture", GIT_AUTHOR_EMAIL="fixture@example.test",
               GIT_COMMITTER_NAME="Synthetic Fixture", GIT_COMMITTER_EMAIL="fixture@example.test",
               GIT_AUTHOR_DATE="2026-01-01T00:00:00Z", GIT_COMMITTER_DATE="2026-01-01T00:00:00Z")
    return subprocess.run(["git", "-C", str(root), *args], env=env, check=True,
                          capture_output=True).stdout.decode().strip()


def write(root, path, content):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def commit(root):
    git(root, "add", "--all")
    git(root, "-c", "commit.gpgsign=false", "commit", "-m", "Synthetic validation fixture")
    return git(root, "rev-parse", "HEAD")


def reference(repository, revision, path, selector="file"):
    return {"repository": repository, "revision": revision, "path": path, "selector": selector}


class TraceabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared = tempfile.TemporaryDirectory(prefix="barometer-checker-tests-")
        cls.helper = Path(cls.shared.name) / "go-selector"
        go = shutil.which("go")
        if go is None:
            raise RuntimeError("Go is required for the selector acceptance tests")
        subprocess.run([go, "build", "-o", str(cls.helper), str(PUBLIC_ROOT / "scripts/go_selector.go")],
                       check=True, capture_output=True, env=dict(os.environ, GOTOOLCHAIN="local"))

    @classmethod
    def tearDownClass(cls):
        cls.shared.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="barometer-checker-case-")
        self.addCleanup(self.temp.cleanup)
        self.spec = Path(self.temp.name) / "spec"
        self.impl = Path(self.temp.name) / "impl"
        for root in (self.spec, self.impl):
            root.mkdir()
            git(root, "init", "--quiet")
        catalog = {"format_version": 1, "namespaces": {"TASK": {"owner": "Public maintainers", "scope": "Synthetic"}},
                   "requirements": [
                       {"id": identity, "status": status, "source": "data-formats/task.md",
                        "successors": [], "reason": "Synthetic retirement" if status == "retired" else ""}
                       for identity, status in ((REQ, "active"), (OTHER, "active"), (RETIRED, "retired"))]}
        write(self.spec, "requirements/catalog.json", json.dumps(catalog))
        write(self.spec, "data-formats/task.md", "# Task\n\n**Version:** 0.1.0\n\n" + "\n".join(
            f'<a id="{r["id"]}"></a>\n\n**{r["id"]}{" (retired)" if r["status"] == "retired" else ""}:**\n\nSynthetic obligation.\n'
            for r in catalog["requirements"]))
        write(self.spec, "resolution.md", "# Public disposition\n\nSynthetic reviewed closure.\n")
        self.spec_rev = commit(self.spec)
        write(self.impl, "decode.go", "package fixture\n\nfunc Decode() {}\n")
        write(self.impl, "decode_test.go", "package fixture\n\nfunc TestDecode() {}\n")
        write(self.impl, "doc.go", "package fixture\n")
        write(self.impl, "docs/specification-issues.md", "# Findings\n\nSynthetic finding.\n")
        self.impl_rev = commit(self.impl)
        # Reports can be committed after the implementation baseline they describe.
        write(self.impl, "evidence.md", "# Synthetic evidence\n\nSanitized assertions for review.\n")
        self.evidence_rev = commit(self.impl)
        self.repos = {SPEC: self.spec, IMPL: self.impl}
        self.manifest = {
            "format_version": 1,
            "specification": {"repository": SPEC, "revision": self.spec_rev, "version": "0.1.0"},
            "implementation": {"repository": IMPL, "revision": self.impl_rev},
            "coverage": {"mode": "partial", "unallocated_sources": ["data-formats/task.md"], "notes": "Synthetic inventory boundary."},
            "requirements": [{"id": REQ, "implementation_status": "planned",
                              "implementation_locations": [{"path": "planned.go", "selector": "symbol:Decode", "state": "planned"}],
                              "case_ids": ["CASE-TASK"], "issue_ids": [], "review_evidence_ids": [],
                              "support": [], "notes": "Synthetic planning only."}],
            "cases": [{"id": "CASE-TASK", "location": {"path": "planned_test.go", "selector": "symbol:TestDecode", "state": "planned"},
                       "scope": SCOPE, "status": "planned", "evidence_ids": []}],
            "issues": [], "evidence": []}

    def report(self, manifest=None, **kwargs):
        return checker.check(json.dumps(manifest or self.manifest), self.repos, self.spec_rev, self.impl_rev,
                             go_selector=self.helper, **kwargs)

    def finding(self, report, code, pointer=None, level=None):
        return any(f["code"] == code and (pointer is None or f["pointer"] == pointer)
                   and (level is None or f["level"] == level) for f in report["findings"])

    def evidence(self, identity, kind, scope=SCOPE, ids=None):
        return {"id": identity, "kind": kind, "reference": reference(IMPL, self.evidence_rev, "evidence.md"),
                "specification_revision": self.spec_rev, "implementation_revision": self.impl_rev,
                "requirement_ids": ids or [REQ], "scope": scope,
                "case_results": [{"case_id": "CASE-TASK", "result": "passed"}] if kind == "conformance" else []}

    def implemented(self):
        manifest = copy.deepcopy(self.manifest)
        r, case = manifest["requirements"][0], manifest["cases"][0]
        r.update(implementation_status="implemented", review_evidence_ids=["REVIEW"],
                 implementation_locations=[{"path": "decode.go", "selector": "symbol:Decode", "state": "existing"}])
        case.update(status="passed", evidence_ids=["RESULT"],
                    location={"path": "decode_test.go", "selector": "symbol:TestDecode", "state": "existing"})
        manifest["evidence"] = [self.evidence("RESULT", "conformance"), self.evidence("REVIEW", "review")]
        return manifest

    def test_partial_metadata_reports_exact_gap_classes(self):
        report = self.report()
        self.assertTrue(report["valid"])
        self.assertEqual({f["code"] for f in report["findings"]},
                         {"MISSING_REQUIREMENT", "MISSING_IMPLEMENTATION", "MISSING_CONFORMANCE", "UNALLOCATED_REQUIREMENTS"})
        self.assertEqual([f["related_id"] for f in report["findings"] if f["code"] == "MISSING_REQUIREMENT"], [OTHER])

    def test_implemented_metadata_with_later_evidence_revision(self):
        report = self.report(self.implemented())
        self.assertTrue(report["valid"], report["findings"])
        self.assertTrue(report["review_assertions"])
        self.assertTrue(report["review_limits"])

    def test_all_support_kinds(self):
        manifest = self.implemented()
        r = manifest["requirements"][0]
        manifest["evidence"] += [self.evidence("PLATFORM", "platform"), self.evidence("FIELD", "field")]
        r["support"] = [{"kind": kind, "scope": SCOPE, "status": "supported", "evidence_ids": ids}
                        for kind, ids in (("core", ["REVIEW"]), ("platform", ["PLATFORM"]), ("field", ["PLATFORM", "FIELD"]))]
        self.assertTrue(self.report(manifest)["valid"])

    def test_field_needs_platform_and_field_evidence(self):
        manifest = self.implemented()
        manifest["evidence"].append(self.evidence("FIELD", "field"))
        manifest["requirements"][0]["support"] = [{"kind": "field", "scope": SCOPE, "status": "supported", "evidence_ids": ["FIELD"]}]
        self.assertTrue(self.finding(self.report(manifest), "CLAIM_NOT_JUSTIFIED", "/requirements/0/support/0/status"))

    def test_support_requires_exact_scope(self):
        manifest = self.implemented()
        manifest["requirements"][0]["support"] = [{"kind": "core", "scope": "Broader scope", "status": "supported", "evidence_ids": ["REVIEW"]}]
        report = self.report(manifest)
        self.assertTrue(self.finding(report, "EVIDENCE_MISMATCH"))
        self.assertTrue(self.finding(report, "CLAIM_NOT_JUSTIFIED"))

    def test_shared_case_covers_all_owners(self):
        manifest = self.implemented()
        r = copy.deepcopy(manifest["requirements"][0])
        r["id"] = OTHER
        manifest["requirements"].append(r)
        for e in manifest["evidence"]:
            e["requirement_ids"].append(OTHER)
        manifest["coverage"]["mode"] = "catalog_complete"
        self.assertTrue(self.report(manifest)["valid"])
        manifest["evidence"][0]["requirement_ids"].remove(OTHER)
        self.assertTrue(self.finding(self.report(manifest), "EVIDENCE_MISMATCH", "/cases/0/evidence_ids/0"))

    def test_catalog_complete_does_not_hide_unallocated_gaps(self):
        manifest = self.implemented()
        r = copy.deepcopy(manifest["requirements"][0])
        r["id"] = OTHER
        manifest["requirements"].append(r)
        for e in manifest["evidence"]:
            e["requirement_ids"].append(OTHER)
        manifest["coverage"].update(mode="catalog_complete", unallocated_sources=[])
        report = self.report(manifest)
        self.assertTrue(report["valid"])
        self.assertTrue(self.finding(report, "UNALLOCATED_REQUIREMENTS", "/coverage/notes", "gap"))

    def test_existing_public_invalid_scenarios(self):
        scenarios = json.loads((PUBLIC_ROOT / "traceability/invalid-scenarios.json").read_text())["scenarios"]
        base = json.loads((PUBLIC_ROOT / "traceability/example.partial.json").read_text())
        original_spec, original_impl = base["specification"]["revision"], base["implementation"]["revision"]

        def remap(value):
            if isinstance(value, dict):
                return {k: remap(v) for k, v in value.items()}
            if isinstance(value, list):
                return [remap(v) for v in value]
            return {"https://github.com/tv-rain/barometer-spec": SPEC,
                    "https://github.com/tv-rain/barometer-go": IMPL,
                    original_spec: self.spec_rev, original_impl: self.impl_rev}.get(value, value)

        for scenario in scenarios:
            with self.subTest(scenario=scenario["name"]):
                manifest = copy.deepcopy(base)
                if "raw_json" in scenario:
                    raw = scenario["raw_json"]
                else:
                    for patch in scenario["patch"]:
                        parts = [p.replace("~1", "/").replace("~0", "~") for p in patch["path"].split("/")[1:]]
                        target = manifest
                        for p in parts[:-1]:
                            target = target[int(p)] if isinstance(target, list) else target[p]
                        last = parts[-1]
                        if isinstance(target, list):
                            if patch["op"] == "add":
                                target.insert(len(target) if last == "-" else int(last), copy.deepcopy(patch["value"]))
                            else:
                                target[int(last)] = copy.deepcopy(patch["value"])
                        else:
                            target[last] = copy.deepcopy(patch["value"])
                    raw = json.dumps(remap(manifest))
                report = checker.check(raw, self.repos, self.spec_rev, self.impl_rev, go_selector=self.helper)
                self.assertFalse(report["valid"])
                for expected in scenario["expected"]:
                    self.assertTrue(self.finding(report, expected["code"], expected["pointer"], expected["level"]), report["findings"])

    def test_decoded_duplicate_keys_at_all_depths_and_pointer_escaping(self):
        for raw, where in ((r'{"a":{"x":1,"\u0078":2}}', "/a/x"),
                           (r'{"a":[{"~/":1,"~/":2}]}', "/a/0/~0~1")):
            with self.subTest(raw=raw):
                report = checker.check(raw, {}, self.spec_rev, self.impl_rev)
                self.assertEqual([f["code"] for f in report["findings"]], ["DUPLICATE_MEMBER"])
                self.assertEqual(report["findings"][0]["pointer"], where)

    def test_invalid_encoding_numbers_and_types(self):
        for raw in (b'\xff', '{"x":NaN}', '{"x":1e999}', '{"x":"\\ud800"}', '[]', '{}'):
            with self.subTest(raw=raw):
                self.assertTrue(self.finding(checker.check(raw, {}, self.spec_rev, self.impl_rev), "MALFORMED"))
        for value in (True, 1.0, "1", 2):
            self.manifest["format_version"] = value
            self.assertTrue(self.finding(self.report(), "MALFORMED", "/format_version"))

    def test_structural_failures_stop_semantics(self):
        self.manifest["requirements"][0]["unexpected"] = True
        self.manifest["implementation"]["revision"] = "0" * 40
        report = self.report()
        self.assertEqual([f["code"] for f in report["findings"]], ["MALFORMED"])

    def test_missing_baseline_and_explicit_checkout_mapping(self):
        self.repos.pop(IMPL)
        report = self.report(self.implemented())
        self.assertTrue(self.finding(report, "BASELINE_UNAVAILABLE", "/implementation/repository"))
        self.assertTrue(report["skipped_checks"])

    def test_missing_git_commit(self):
        self.manifest["implementation"]["revision"] = "a" * 40
        self.assertTrue(self.finding(self.report(), "BASELINE_UNAVAILABLE", "/implementation/revision"))

    def test_current_and_historical_expected_baselines(self):
        for mode in ("current", "historical"):
            report = checker.check(json.dumps(self.manifest), self.repos, "a" * 40, self.impl_rev, mode=mode)
            self.assertEqual(report["validation_mode"], mode)
            self.assertTrue(self.finding(report, "STALE_BASELINE", "/specification/revision"))

    def test_versions_must_agree(self):
        self.manifest["specification"]["version"] = "0.2.0"
        self.assertTrue(self.finding(self.report(), "STALE_BASELINE", "/specification/version"))

    def test_unknown_and_retired_requirement_ids(self):
        for identity, code in (("REQ-TASK-9999", "UNKNOWN_REQUIREMENT"), (RETIRED, "RETIRED_REQUIREMENT")):
            self.manifest["requirements"][0]["id"] = identity
            self.assertTrue(self.finding(self.report(), code, "/requirements/0/id"))

    def test_catalog_anchor_integrity(self):
        write(self.spec, "duplicate.md", f'<a id="{REQ}"></a>\n\n**{REQ}:**\n\nDuplicate.\n')
        revision = commit(self.spec)
        self.manifest["specification"]["revision"] = revision
        report = checker.check(json.dumps(self.manifest), self.repos, revision, self.impl_rev)
        self.assertTrue(self.finding(report, "CATALOG_INVALID", "/specification"))

    def test_duplicate_ids_are_not_first_or_last_wins(self):
        r = copy.deepcopy(self.manifest["requirements"][0])
        r["notes"] = "Different duplicate"
        self.manifest["requirements"].append(r)
        self.assertTrue(self.finding(self.report(), "DUPLICATE_ID", "/requirements/1/id"))

    def test_duplicate_mapping_tuples(self):
        self.manifest["requirements"][0]["support"] = [
            {"kind": "core", "scope": SCOPE, "status": "unclaimed", "evidence_ids": []},
            {"kind": "core", "scope": SCOPE, "status": "unsupported", "evidence_ids": []}]
        self.assertTrue(self.finding(self.report(), "MALFORMED", "/requirements/0/support/1"))

    def test_dangling_and_unreferenced_records(self):
        self.manifest["requirements"][0]["case_ids"] = ["ABSENT"]
        report = self.report()
        self.assertTrue(self.finding(report, "DANGLING_REFERENCE", "/requirements/0/case_ids/0"))
        self.assertTrue(self.finding(report, "UNREFERENCED_RECORD", "/cases/0/id"))

    def test_orphan_evidence_cycles_do_not_create_reachability(self):
        manifest = self.implemented()
        manifest["requirements"][0]["case_ids"] = []
        manifest["requirements"][0].update(implementation_status="partial", review_evidence_ids=[])
        report = self.report(manifest)
        self.assertTrue(self.finding(report, "UNREFERENCED_RECORD", "/evidence/0/id"))

    def test_case_result_requires_back_reference(self):
        manifest = self.implemented()
        manifest["cases"][0]["evidence_ids"] = ["REVIEW"]
        self.assertTrue(self.finding(self.report(manifest), "EVIDENCE_MISMATCH", "/evidence/0/case_results/0"))

    def test_evidence_case_scope_kind_result_and_baselines(self):
        for change in ({"scope": "Other scope"}, {"implementation_revision": self.evidence_rev},
                       {"case_results": [{"case_id": "CASE-TASK", "result": "failed"}]}):
            manifest = self.implemented()
            manifest["evidence"][0].update(change)
            with self.subTest(change=change):
                report = self.report(manifest)
                self.assertTrue(self.finding(report, "EVIDENCE_MISMATCH"))
                self.assertTrue(self.finding(report, "CLAIM_NOT_JUSTIFIED"))

    def test_missing_evidence_paths_block_claims(self):
        manifest = self.implemented()
        manifest["evidence"][0]["reference"]["path"] = "absent.md"
        report = self.report(manifest)
        self.assertTrue(self.finding(report, "STALE_LOCATION", "/evidence/0/reference/path"))
        self.assertTrue(self.finding(report, "CLAIM_NOT_JUSTIFIED"))

    def test_unresolved_issue_blocks_implemented_claim(self):
        manifest = self.implemented()
        manifest["issues"] = [{"id": "ISSUE", "disposition": "open", "finding": reference(IMPL, self.impl_rev, "docs/specification-issues.md"),
                               "resolution_references": [], "notes": "Synthetic unresolved blocker."}]
        manifest["requirements"][0]["issue_ids"] = ["ISSUE"]
        self.assertTrue(self.finding(self.report(manifest), "CLAIM_NOT_JUSTIFIED", "/requirements/0/implementation_status"))
        manifest["issues"][0].update(disposition="closed", resolution_references=[reference(SPEC, self.spec_rev, "resolution.md")])
        self.assertTrue(self.report(manifest)["valid"])

    def test_failed_case_cannot_support_implemented_claim(self):
        manifest = self.implemented()
        manifest["cases"][0]["status"] = "failed"
        manifest["evidence"][0]["case_results"][0]["result"] = "failed"
        self.assertTrue(self.finding(self.report(manifest), "CLAIM_NOT_JUSTIFIED"))

    def test_planned_locations_need_not_exist(self):
        self.assertTrue(self.report()["valid"])
        self.manifest["requirements"][0]["implementation_locations"][0]["state"] = "existing"
        self.assertTrue(self.finding(self.report(), "STALE_LOCATION", "/requirements/0/implementation_locations/0/path"))

    def test_unsafe_paths_and_selectors(self):
        for path in ("../decode.go", "/decode.go", "a//b", "a/./b", "a\\b"):
            self.manifest["requirements"][0]["implementation_locations"][0]["path"] = path
            self.assertTrue(self.finding(self.report(), "MALFORMED"))
        self.manifest["requirements"][0]["implementation_locations"][0]["path"] = "decode.go"
        for selector in ("line:1", "symbol:", " file", "symbol: Decode"):
            self.manifest["requirements"][0]["implementation_locations"][0]["selector"] = selector
            self.assertTrue(self.finding(self.report(), "MALFORMED"))

    def test_symlink_and_submodule_are_not_files(self):
        (self.impl / "link.go").symlink_to("decode.go")
        revision = commit(self.impl)
        git(self.impl, "update-index", "--add", "--cacheinfo", f"160000,{self.impl_rev},module")
        git(self.impl, "-c", "commit.gpgsign=false", "commit", "-m", "Synthetic gitlink")
        revision = git(self.impl, "rev-parse", "HEAD")
        for path in ("link.go", "module", "module/decode.go", "decode.go/"):
            manifest = self.implemented()
            manifest["implementation"]["revision"] = revision
            manifest["requirements"][0]["implementation_locations"][0].update(path=path, selector="file")
            report = checker.check(json.dumps(manifest), self.repos, self.spec_rev, revision, go_selector=self.helper)
            self.assertFalse(report["valid"])

    def test_case_sensitive_paths_and_worktree_independence(self):
        manifest = self.implemented()
        write(self.impl, "decode.go", "INVALID UNCOMMITTED SOURCE")
        write(self.spec, "requirements/catalog.json", "INVALID UNCOMMITTED CATALOG")
        self.assertTrue(self.report(manifest)["valid"])
        manifest["requirements"][0]["implementation_locations"][0]["path"] = "Decode.go"
        self.assertTrue(self.finding(self.report(manifest), "STALE_LOCATION"))

    def test_go_resolves_declarations_not_comments_or_substrings(self):
        resolver = checker.Selectors(self.helper)
        source = b'package fixture\n// func Fake() {}\nvar Text = "Fake"\nfunc Decode() {}\ntype Box[T any] struct{ Value T }\nfunc (b *Box[T]) Run() {}\n'
        resolver.resolve("source.go", "symbol:Decode", source)
        resolver.resolve("source.go", "symbol:Box.Run", source)
        resolver.resolve("source.go", "symbol:Box.Value", source)
        for symbol in ("Fake", "Dec", "Run", "Value"):
            with self.subTest(symbol=symbol), self.assertRaises(checker.ReferenceFailure):
                resolver.resolve("source.go", "symbol:" + symbol, source)

    def test_go_missing_resolver_and_unsupported_language_fail(self):
        manifest = self.implemented()
        report = checker.check(json.dumps(manifest), self.repos, self.spec_rev, self.impl_rev)
        self.assertTrue(self.finding(report, "STALE_LOCATION", "/requirements/0/implementation_locations/0/selector"))
        with self.assertRaises(checker.ReferenceFailure):
            checker.Selectors(self.helper).resolve("source.py", "symbol:Decode", b"def Decode(): pass")

    def test_markdown_selectors_are_literal_and_unique(self):
        resolver = checker.Selectors()
        raw = b'# Exact title\n\n<a id="exact"></a>\n\n```md\n# Fake\n<a id="fake"></a>\n```\n<!--\n# Hidden\n-->\n'
        resolver.resolve("record.md", "heading:Exact title", raw)
        resolver.resolve("record.md", "anchor:exact", raw)
        for selector in ("heading:Exact", "heading:Fake", "heading:Hidden", "anchor:fake", "anchor:ex.*"):
            with self.subTest(selector=selector), self.assertRaises(checker.ReferenceFailure):
                resolver.resolve("record.md", selector, raw)
        with self.assertRaises(checker.ReferenceFailure):
            resolver.resolve("record.md", "heading:Exact title", raw + b"# Exact title\n")

    def test_public_urls_reject_credentials_query_fragment_and_traversal(self):
        for url in ("http://example.test/repo", "https://user:pass@example.test/repo", "https://example.test/repo?",
                    "https://example.test/repo#", "https://example.test/repo/", "https://example.test/a/../repo"):
            self.assertFalse(checker.valid_repository(url), url)

    def test_report_is_deterministic_and_sorted(self):
        report = self.report()
        reordered = json.dumps(self.manifest, sort_keys=True, indent=4)
        again = checker.check(reordered, dict(reversed(list(self.repos.items()))), self.spec_rev, self.impl_rev, go_selector=self.helper)
        self.assertEqual(report, again)
        keys = [(f["code"], f["pointer"], f["related_id"]) for f in report["findings"]]
        self.assertEqual(keys, sorted(set(keys), key=lambda key: tuple(v.encode("utf-8") for v in key)))
        self.assertEqual(checker.render_text(report), checker.render_text(again))

    def test_cli_exit_codes_formats_and_output(self):
        manifest = Path(self.temp.name) / "manifest.json"
        manifest.write_text(json.dumps(self.manifest))
        args = [str(manifest), "--repository", f"{SPEC}={self.spec}", "--repository", f"{IMPL}={self.impl}",
                "--expected-specification", self.spec_rev, "--expected-implementation", self.impl_rev, "--mode", "historical"]
        for fmt in ("json", "text"):
            stream = io.StringIO()
            with redirect_stdout(stream):
                self.assertEqual(checker.main(args + ["--format", fmt]), 0)
            self.assertTrue(stream.getvalue())
            if fmt == "json":
                self.assertTrue(json.loads(stream.getvalue())["valid"])
        output = Path(self.temp.name) / "report.json"
        self.assertEqual(checker.main(args + ["--format", "json", "--output", str(output)]), 0)
        self.manifest["coverage"]["mode"] = "catalog_complete"
        manifest.write_text(json.dumps(self.manifest))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(checker.main(args), 1)
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            checker.main([str(manifest)])
        self.assertEqual(caught.exception.code, 2)

    def test_schema_cannot_fetch_remote_references(self):
        schema = Path(self.temp.name) / "schema.json"
        schema.write_text('{"$ref":"https://example.test/schema"}')
        with self.assertRaises(ValueError):
            self.report(schema_path=schema)

    def test_case_ids_are_distinct_from_requirement_ids(self):
        self.manifest["cases"][0]["id"] = REQ
        self.manifest["requirements"][0]["case_ids"] = [REQ]
        self.assertTrue(self.finding(self.report(), "MALFORMED", "/cases/0/id"))

    def test_duplicate_arrays_point_to_later_item(self):
        self.manifest["requirements"][0]["case_ids"].append("CASE-TASK")
        self.assertTrue(self.finding(self.report(), "MALFORMED", "/requirements/0/case_ids/1"))

    def test_evidence_requirements_must_exist_and_be_mapped(self):
        manifest = self.implemented()
        manifest["evidence"][0]["requirement_ids"].append("REQ-TASK-9999")
        report = self.report(manifest)
        self.assertTrue(self.finding(report, "UNKNOWN_REQUIREMENT", "/evidence/0/requirement_ids/1"))
        self.assertTrue(self.finding(report, "DANGLING_REFERENCE", "/evidence/0/requirement_ids/1"))

    def test_duplicate_case_results_and_issue_reference_tuples(self):
        manifest = self.implemented()
        manifest["evidence"][0]["case_results"].append({"case_id": "CASE-TASK", "result": "failed"})
        self.assertTrue(self.finding(self.report(manifest), "MALFORMED", "/evidence/0/case_results/1"))
        manifest = self.implemented()
        ref = reference(SPEC, self.spec_rev, "resolution.md")
        manifest["issues"] = [{"id": "ISSUE", "disposition": "closed", "finding": ref,
                               "resolution_references": [ref, copy.deepcopy(ref)], "notes": "Synthetic closure."}]
        manifest["requirements"][0]["issue_ids"] = ["ISSUE"]
        self.assertTrue(self.finding(self.report(manifest), "MALFORMED", "/issues/0/resolution_references/1"))

    def test_closed_issue_requires_existing_resolution(self):
        manifest = self.implemented()
        manifest["issues"] = [{"id": "ISSUE", "disposition": "closed",
                               "finding": reference(IMPL, self.impl_rev, "docs/specification-issues.md"),
                               "resolution_references": [reference(SPEC, self.spec_rev, "absent.md")],
                               "notes": "Synthetic adoption assertion."}]
        manifest["requirements"][0]["issue_ids"] = ["ISSUE"]
        report = self.report(manifest)
        self.assertTrue(self.finding(report, "CLAIM_NOT_JUSTIFIED", "/issues/0/disposition"))
        self.assertTrue(self.finding(report, "CLAIM_NOT_JUSTIFIED", "/requirements/0/implementation_status"))

    def test_dangling_result_case_and_review_kind(self):
        manifest = self.implemented()
        manifest["evidence"][0]["case_results"][0]["case_id"] = "ABSENT"
        self.assertTrue(self.finding(self.report(manifest), "DANGLING_REFERENCE", "/evidence/0/case_results/0/case_id"))
        manifest = self.implemented()
        manifest["evidence"][1]["kind"] = "platform"
        self.assertTrue(self.finding(self.report(manifest), "EVIDENCE_MISMATCH", "/requirements/0/review_evidence_ids/0"))

    def test_blocked_case_evidence_cannot_assert_pass(self):
        manifest = self.implemented()
        manifest["requirements"][0]["implementation_status"] = "partial"
        manifest["cases"][0]["status"] = "blocked"
        report = self.report(manifest)
        self.assertTrue(self.finding(report, "EVIDENCE_MISMATCH"))
        self.assertTrue(self.finding(report, "MISSING_CONFORMANCE"))
        manifest["evidence"][0]["case_results"][0]["result"] = "blocked"
        self.assertTrue(self.report(manifest)["valid"])

    def test_unallocated_source_path_must_resolve(self):
        self.manifest["coverage"]["unallocated_sources"] = ["absent.md"]
        self.assertTrue(self.finding(self.report(), "STALE_LOCATION", "/coverage/unallocated_sources/0"))

    def test_go_ambiguous_and_invalid_source_fail(self):
        resolver = checker.Selectors(self.helper)
        for raw in (b"package fixture\nfunc Decode() {}\nfunc Decode() {}\n", b"NOT GO"):
            with self.assertRaises(checker.ReferenceFailure):
                resolver.resolve("source.go", "symbol:Decode", raw)

    def test_markdown_setext_and_fence_boundaries(self):
        resolver = checker.Selectors()
        resolver.resolve("record.md", "heading:Exact", b"Exact\n=====\n")
        with self.assertRaises(checker.ReferenceFailure):
            resolver.resolve("record.md", "heading:Fake", b"Fake\n```\nignored\n```\n=====\n")

    def test_setup_errors_have_invocation_exit_status(self):
        manifest = Path(self.temp.name) / "manifest.json"
        manifest.write_text(json.dumps(self.manifest))
        schema = Path(self.temp.name) / "schema.json"
        args = [str(manifest), "--repository", f"{SPEC}={self.spec}", "--expected-specification", self.spec_rev,
                "--expected-implementation", self.impl_rev, "--mode", "current", "--schema", str(schema)]
        for raw in ('{"$ref":"#/$defs/absent"}', '{"type":42}', '{"$ref":42}'):
            schema.write_text(raw)
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                checker.main(args)
            self.assertEqual(caught.exception.code, 2)

    def test_unavailable_evidence_skips_dependent_claims(self):
        manifest = self.implemented()
        manifest["evidence"][0]["reference"]["repository"] = "https://example.test/missing-evidence-repo"
        report = self.report(manifest)
        self.assertTrue(self.finding(report, "BASELINE_UNAVAILABLE", "/evidence/0/reference/repository"))
        self.assertFalse(self.finding(report, "EVIDENCE_MISMATCH"))
        self.assertFalse(self.finding(report, "CLAIM_NOT_JUSTIFIED", "/requirements/0/implementation_status"))
        self.assertTrue(report["skipped_checks"])


if __name__ == "__main__":
    unittest.main()
