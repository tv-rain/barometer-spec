"""Synthetic identifier-integrity tests; no runtime conformance claims."""

import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest

from check_requirements import check, main


class RequirementChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.spec = self.base / "spec"
        self.consumer = self.base / "consumer"
        self.consumer.mkdir()
        self.catalog = {
            "format_version": 1,
            "namespaces": {"TASK": {"owner": "Specification maintainers", "scope": "Task format"}},
            "requirements": [self.record("REQ-TASK-0001")],
        }
        self.write_catalog()
        self.write("task.md", self.definition("REQ-TASK-0001"))

    def record(self, identity, status="active", successors=None):
        return {"id": identity, "status": status, "source": "task.md",
                "successors": successors or [], "reason": "Superseded." if status == "retired" else ""}

    def definition(self, identity, retired=False):
        suffix = " (retired)" if retired else ""
        return f'<a id="{identity}"></a>\n\n**{identity}{suffix}:**\n\nReject unknown fields.\n'

    def write(self, name, text, root=None):
        path = (root or self.spec) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_catalog(self):
        self.write("requirements/catalog.json", json.dumps(self.catalog))

    def errors(self, baseline=None):
        try:
            return "\n".join(check(self.spec, [self.consumer], baseline))
        except ValueError as exc:
            return str(exc)

    def save_baseline(self):
        baseline = self.base / "baseline.json"
        baseline.write_text(json.dumps(self.catalog), encoding="utf-8")
        return baseline

    def test_valid_public_only_and_consumers(self):
        self.assertEqual([], check(self.spec))
        self.write("review.md", "<!-- requirement-ref: REQ-TASK-0001 -->\n", self.consumer)
        self.write("sample.go", "package sample\n// requirement-ref: REQ-TASK-0001\n", self.consumer)
        self.assertEqual("", self.errors())

    def test_edit_heading_reorder_and_move_preserve_identity(self):
        baseline = self.save_baseline()
        (self.spec / "task.md").rename(self.spec / "renamed.md")
        self.write("renamed.md", "# New title\n\nEditorial introduction.\n\n" + self.definition("REQ-TASK-0001"))
        self.catalog["requirements"][0]["source"] = "renamed.md"
        self.write_catalog()
        self.assertEqual("", self.errors(baseline))

    def test_duplicate_catalog_id(self):
        self.catalog["requirements"].append(copy.deepcopy(self.catalog["requirements"][0]))
        self.write_catalog()
        self.assertIn("duplicate catalog ID", self.errors())

    def test_duplicate_definition(self):
        self.write("extra.md", self.definition("REQ-TASK-0001"))
        self.assertIn("duplicate definition", self.errors())

    def test_malformed_catalog_ids(self):
        for identity in ("req-TASK-0001", "REQ-TASK-1", "REQ-TASK-0000", "REQ-TASK-00001", "REQ-TASK-０００１", 1):
            with self.subTest(identity=identity):
                self.catalog["requirements"][0]["id"] = identity
                self.write_catalog()
                self.assertIn("malformed ID", self.errors())

    def test_malformed_marker_syntax(self):
        for text in ('<a id="req-TASK-0001"></a>', '<a id="REQ-TASK-1"></a>', "<a id='REQ-TASK-0001'></a>",
                     "<!-- requirement-ref REQ-TASK-0001 -->", "<!-- requirement-ref: REQ-TASK-1 -->",
                     "<!-- requirement-ref: REQ-TASK-0001 REQ-TASK-0002 -->", "<!-- Requirement-ref: REQ-TASK-0001 -->"):
            with self.subTest(text=text):
                self.write("bad.md", text, self.consumer)
                self.assertIn("malformed", self.errors())

    def test_orphaned_missing_anchor_and_unknown_definition(self):
        self.write("task.md", self.definition("REQ-TASK-0002"))
        errors = self.errors()
        self.assertIn("orphaned catalog ID", errors)
        self.assertIn("uncataloged definition", errors)

    def test_source_mismatch(self):
        self.catalog["requirements"][0]["source"] = "missing.md"
        self.write_catalog()
        self.assertIn("source mismatch", self.errors())

    def test_unknown_and_malformed_references(self):
        self.write("review.md", "<!-- requirement-ref: REQ-TASK-0002 -->", self.consumer)
        self.assertIn("unresolved reference", self.errors())
        self.write("review.md", "// requirement-ref: REQ-TASK-0001", self.consumer)
        self.assertIn("malformed requirement reference", self.errors())

    def test_consumer_may_not_define_public_ids(self):
        self.write("review.md", self.definition("REQ-TASK-0001"), self.consumer)
        self.assertIn("consumer cannot define", self.errors())

    def test_fenced_examples_are_not_allocations_or_references(self):
        self.write("examples.md", '````markdown\n```\n' + self.definition("REQ-TASK-0001") +
                   "<!-- requirement-ref: REQ-TASK-9999 -->\n````\n~~~markdown\n" +
                   "<!-- requirement-ref: REQ-TASK-9998 -->\n~~~\n")
        self.assertEqual("", self.errors())

    def test_unclosed_fence_fails_instead_of_hiding_references(self):
        self.write("bad.md", "```markdown\n<!-- requirement-ref: REQ-TASK-9999 -->")
        self.assertIn("unclosed Markdown fence", self.errors())

    def test_retirement_and_history(self):
        baseline = self.save_baseline()
        self.catalog["requirements"] = [self.record("REQ-TASK-0001", "retired", ["REQ-TASK-0002"]), self.record("REQ-TASK-0002")]
        self.write_catalog()
        self.write("task.md", self.definition("REQ-TASK-0001", True) + self.definition("REQ-TASK-0002"))
        self.write("review.md", "<!-- requirement-history: REQ-TASK-0001 -->\n<!-- requirement-ref: REQ-TASK-0002 -->", self.consumer)
        self.assertEqual("", self.errors(baseline))
        self.write("review.md", "<!-- requirement-ref: REQ-TASK-0001 -->", self.consumer)
        self.assertIn("current reference to retired ID", self.errors())

    def test_removal_without_successor(self):
        self.catalog["requirements"] = [self.record("REQ-TASK-0001", "retired")]
        self.write_catalog()
        self.write("task.md", self.definition("REQ-TASK-0001", True))
        self.assertEqual("", self.errors())

    def test_unknown_successor_and_cycle(self):
        self.catalog["requirements"] = [self.record("REQ-TASK-0001", "retired", ["REQ-TASK-0002"])]
        self.write_catalog()
        self.assertIn("unknown successor", self.errors())
        self.catalog["requirements"].append(self.record("REQ-TASK-0002", "retired", ["REQ-TASK-0001"]))
        self.write_catalog()
        self.assertIn("successor cycle", self.errors())

    def test_split_and_merge_history(self):
        baseline = self.save_baseline()
        self.catalog["requirements"] = [
            self.record("REQ-TASK-0001", "retired", ["REQ-TASK-0002", "REQ-TASK-0003"]),
            self.record("REQ-TASK-0002", "retired", ["REQ-TASK-0004"]),
            self.record("REQ-TASK-0003", "retired", ["REQ-TASK-0004"]), self.record("REQ-TASK-0004")]
        self.write_catalog()
        self.write("task.md", "\n".join(self.definition(r["id"], r["status"] == "retired") for r in self.catalog["requirements"]))
        self.assertEqual("", self.errors(baseline))

    def test_deleted_allocation(self):
        baseline = self.save_baseline()
        self.catalog["requirements"] = []
        self.write_catalog()
        self.write("task.md", "# No definitions\n")
        self.assertIn("deleted allocation", self.errors(baseline))

    def test_reactivation_and_gap_reuse(self):
        self.catalog["requirements"] = [self.record("REQ-TASK-0003", "retired")]
        baseline = self.save_baseline()
        self.catalog["requirements"] = [self.record("REQ-TASK-0003"), self.record("REQ-TASK-0001")]
        self.write_catalog()
        errors = self.errors(baseline)
        self.assertIn("reactivated retired ID", errors)
        self.assertIn("reused allocation gap", errors)

    def test_invalid_catalog_metadata(self):
        original = copy.deepcopy(self.catalog)
        for key, value, expected in (("source", "../outside.md", "unsafe source"), ("source", "/tmp/outside.md", "unsafe source"),
                                     ("source", "./task.md", "unsafe source"), ("status", "draft", "invalid status"),
                                     ("successors", ["REQ-TASK-0001"], "invalid successors"), ("id", "REQ-MISSING-0001", "undeclared namespace")):
            with self.subTest(key=key, value=value):
                self.catalog = copy.deepcopy(original)
                self.catalog["requirements"][0][key] = value
                self.write_catalog()
                self.assertIn(expected, self.errors())

    def test_duplicate_json_keys(self):
        self.write("requirements/catalog.json", '{"format_version":1,"format_version":1}')
        self.assertIn("duplicate JSON key", self.errors())

    def test_missing_label_and_empty_unit(self):
        self.write("task.md", '<a id="REQ-TASK-0001"></a>\n# No unit\n')
        self.assertIn("missing or incorrect requirement label", self.errors())
        self.write("task.md", '<a id="REQ-TASK-0001"></a>\n**REQ-TASK-0001:**\n')
        self.assertIn("missing requirement text", self.errors())

    def test_missing_overlap_and_symlink_roots(self):
        with self.assertRaisesRegex(ValueError, "not a directory"):
            check(self.spec, [self.base / "absent"])
        with self.assertRaisesRegex(ValueError, "non-overlapping"):
            check(self.spec, [self.spec])
        (self.spec / "linked.md").symlink_to(self.consumer / "private.md")
        self.assertIn("symlink in scan scope", self.errors())

    def test_cli_failure_and_success_exit_status(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(0, main(["--spec-root", str(self.spec)]))
        self.assertIn("allocation history not checked", stdout.getvalue())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(1, main(["--spec-root", str(self.spec), "--baseline", str(self.base / "absent.json")]))
            self.write("bad.md", "<!-- requirement-ref: REQ-TASK-9999 -->")
            self.assertEqual(1, main(["--spec-root", str(self.spec)]))


if __name__ == "__main__":
    unittest.main()
