"""Validate traceability metadata at explicitly selected immutable Git baselines."""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

import check_requirements


REVISION = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
PATH = re.compile(r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*")
SCRIPT_ROOT = Path(__file__).resolve().parent
REVIEW_LIMITS = [
    "Normative inventory and semantic requirement coverage require human review.",
    "Evidence authenticity and agreement of selected content with manifest assertions require human review.",
    "Completeness, applicability, and issue closure/adoption sufficiency are review assertions, not mechanically verified facts.",
    "A valid metadata report does not establish runtime conformance, platform support, or field validation.",
]


def pointer(parts):
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in parts)


class ObjectPairs(list):
    """Keep member order and duplicates until their full pointers are known."""


class DecodeFailure(ValueError):
    def __init__(self, findings):
        self.findings = findings


def strict_json(raw):
    def constant(_):
        raise ValueError("non-JSON number")

    def number(value):
        result = float(value)
        if result in (float("inf"), float("-inf")):
            raise ValueError("unrepresentable JSON number")
        return result

    try:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        parsed = json.loads(raw, object_pairs_hook=ObjectPairs,
                            parse_constant=constant, parse_float=number)
        duplicates = []

        def inspect(value, parts):
            if isinstance(value, ObjectPairs):
                seen = set()
                for key, child in value:
                    key.encode("utf-8")  # Reject unpaired surrogate escapes.
                    if key in seen:
                        duplicates.append(("DUPLICATE_MEMBER", pointer(parts + [key]),
                                           "Duplicate decoded JSON member."))
                    seen.add(key)
                    inspect(child, parts + [key])
            elif isinstance(value, list):
                for i, child in enumerate(value):
                    inspect(child, parts + [i])
            elif isinstance(value, str):
                value.encode("utf-8")

        inspect(parsed, [])
        if duplicates:
            raise DecodeFailure(duplicates)

        def convert(value):
            if isinstance(value, ObjectPairs):
                return {key: convert(child) for key, child in value}
            if isinstance(value, list):
                return [convert(child) for child in value]
            return value

        return convert(parsed)
    except (ValueError, UnicodeError, RecursionError) as exc:
        if isinstance(exc, DecodeFailure):
            raise
        raise DecodeFailure([("MALFORMED", "", "Invalid UTF-8 JSON.")]) from exc


def valid_revision(value):
    return isinstance(value, str) and REVISION.fullmatch(value) is not None and set(value) != {"0"}


def valid_repository(value):
    if not isinstance(value, str) or not value.startswith("https://"):
        return False
    try:
        parsed = urlsplit(value)
        parsed.port  # Validate a present port without normalizing the URL.
        return (bool(parsed.hostname) and parsed.username is None and parsed.password is None
                and parsed.query == parsed.fragment == "" and "?" not in value and "#" not in value
                and not value.endswith("/") and parsed.path.startswith("/")
                and parsed.path != "/" and not any(c.isspace() for c in value)
                and "\\" not in value and all(p not in ("", ".", "..") for p in parsed.path[1:].split("/")))
    except ValueError:
        return False


def valid_path(value):
    return (isinstance(value, str) and PATH.fullmatch(value) is not None
            and all(part not in (".", "..") for part in value.split("/")))


def selector_syntax(value):
    if not isinstance(value, str) or value != value.strip():
        return False
    if value == "file":
        return True
    kind, sep, name = value.partition(":")
    return bool(sep and kind in ("anchor", "heading", "symbol") and name and name == name.strip())


class ReferenceFailure(ValueError):
    pass


class GitObjects:
    """Read committed blobs only; never checkout, execute source, or fetch."""

    def __init__(self, root, revision):
        self.root = Path(root)
        self.revision = revision
        self.entries = {}
        self.blobs = {}
        if not valid_revision(revision) or self.run("cat-file", "-t", revision).strip() != b"commit":
            raise ReferenceFailure("Full immutable commit is unavailable.")
        for entry in self.run("ls-tree", "-rz", "--full-tree", revision).split(b"\0"):
            if not entry:
                continue
            metadata, path = entry.split(b"\t", 1)
            mode, kind, object_id = metadata.decode("ascii").split(" ")
            self.entries[path.decode("utf-8")] = (mode, kind, object_id)

    def run(self, *args):
        env = {key: value for key, value in os.environ.items() if key not in {
            "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
            "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"}}
        env.update(GIT_NO_LAZY_FETCH="1", GIT_NO_REPLACE_OBJECTS="1", GIT_TERMINAL_PROMPT="0")
        try:
            result = subprocess.run(["git", "-C", str(self.root), *args], env=env,
                                    capture_output=True, timeout=30, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ReferenceFailure("Git object reader is unavailable.") from exc
        if result.returncode:
            raise ReferenceFailure("Required Git object is unavailable; supply a local complete checkout.")
        return result.stdout

    def read(self, path):
        if not valid_path(path):
            raise ReferenceFailure("Unsafe repository-relative path.")
        entry = self.entries.get(path)
        if entry is None or entry[0] not in ("100644", "100755") or entry[1] != "blob":
            raise ReferenceFailure("Path is missing or is not a regular committed file.")
        if path not in self.blobs:
            self.blobs[path] = self.run("cat-file", "blob", entry[2])
        return self.blobs[path]


def markdown_lines(content):
    """Literal Markdown headings/anchors outside fences, comments, and code indentation."""
    fence = None
    comment = False
    for line in content.splitlines():
        match = check_requirements.FENCE.fullmatch(line)
        if match and not comment:
            delimiter, suffix = match.groups()
            if fence is None:
                fence = delimiter
            elif delimiter[0] == fence[0] and len(delimiter) >= len(fence) and not suffix.strip():
                fence = None
            yield ""
            continue
        if fence is not None:
            yield ""
            continue
        if comment:
            if "-->" in line:
                comment = False
            yield ""
            continue
        if "<!--" in line:
            comment = "-->" not in line.split("<!--", 1)[1]
            yield ""
            continue
        if line.startswith(("    ", "\t")):
            yield ""
            continue
        yield line
    if fence is not None or comment:
        raise ReferenceFailure("Unclosed Markdown fence or comment.")


class Selectors:
    def __init__(self, go_selector=None):
        self.go_selector = go_selector
        self.cache = {}

    def resolve(self, path, selector, raw):
        if selector == "file":
            return
        kind, _, name = selector.partition(":")
        if kind in ("anchor", "heading") and path.endswith(".md"):
            try:
                lines = list(markdown_lines(raw.decode("utf-8")))
            except UnicodeError as exc:
                raise ReferenceFailure("Selected Markdown is not UTF-8.") from exc
            if kind == "anchor":
                matches = sum(line.strip() == f'<a id="{name}"></a>' for line in lines)
            else:
                headings = []
                for i, line in enumerate(lines):
                    match = re.fullmatch(r" {0,3}#{1,6}[ \t]+(.+?)\s*", line)
                    if match:
                        headings.append(re.sub(r"[ \t]+#+[ \t]*$", "", match[1]))
                    elif i and re.fullmatch(r" {0,3}(?:=+|-+)[ \t]*", line) and lines[i - 1].strip():
                        headings.append(lines[i - 1].strip())
                matches = headings.count(name)
        elif kind == "symbol" and path.endswith(".go"):
            if self.go_selector is None:
                raise ReferenceFailure("Go symbol resolver unavailable; supply --go-selector.")
            key = (raw, name)
            if key not in self.cache:
                try:
                    result = subprocess.run([str(self.go_selector)],
                                            input=json.dumps({"source": raw.decode("utf-8"), "symbol": name}).encode(),
                                            capture_output=True, timeout=30, check=False)
                    parsed = json.loads(result.stdout)
                    if result.returncode or parsed.get("error") or type(parsed.get("matches")) is not int:
                        raise ValueError("resolver failed")
                    self.cache[key] = parsed["matches"]
                except (OSError, ValueError, UnicodeError, subprocess.TimeoutExpired) as exc:
                    raise ReferenceFailure("Go source/selector could not be verified.") from exc
            matches = self.cache[key]
        else:
            raise ReferenceFailure("Unsupported language/selector.")
        if matches != 1:
            raise ReferenceFailure("Selector must resolve to exactly one literal declaration, anchor, or heading.")


class Checker:
    def __init__(self, repositories, expected_spec, expected_impl, mode, schema_path, go_selector):
        self.repositories = repositories
        self.expected = {"specification": expected_spec, "implementation": expected_impl}
        self.mode = mode
        self.schema_path = Path(schema_path)
        self.selectors = Selectors(go_selector)
        self.findings = {}
        self.views = {}
        self.baselines = None
        self.schema_digest = None
        self.skipped = set()
        self.review_assertions = []

    def add(self, code, where, message, related_id="", level="error"):
        key = (code, where, related_id)
        self.findings[key] = {"code": code, "level": level, "pointer": where,
                              "related_id": related_id, "explanation": message}

    def report(self):
        findings = [self.findings[key] for key in sorted(self.findings,
                    key=lambda key: tuple(value.encode("utf-8") for value in key))]
        return {"report_version": 1, "validation_mode": self.mode,
                "baselines": self.baselines, "expected_baselines": self.expected,
                "schema_sha256": self.schema_digest,
                "valid": not any(f["level"] == "error" for f in findings),
                "findings": findings, "skipped_checks": sorted(self.skipped),
                "review_assertions": sorted(set(self.review_assertions)),
                "review_limits": REVIEW_LIMITS}

    def schema(self, data):
        from jsonschema import Draft202012Validator, SchemaError, validators
        raw = self.schema_path.read_bytes()
        schema = strict_json(raw)
        self.schema_digest = hashlib.sha256(raw).hexdigest()

        def local_refs(value):
            if isinstance(value, dict):
                if "$ref" in value and (not isinstance(value["$ref"], str) or not value["$ref"].startswith("#/$defs/")):
                    raise ValueError("Schema must use local $defs only.")
                if "$ref" in value:
                    target = schema
                    try:
                        for part in value["$ref"][2:].split("/"):
                            target = target[part.replace("~1", "/").replace("~0", "~")]
                    except (KeyError, TypeError) as exc:
                        raise ValueError("Schema contains an unresolved local reference.") from exc
                if "$dynamicRef" in value or "$id" in value:
                    raise ValueError("Schema resource/redirection is unsupported.")
                for child in value.values():
                    local_refs(child)
            elif isinstance(value, list):
                for child in value:
                    local_refs(child)

        local_refs(schema)
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            raise ValueError("Invalid checker schema.") from exc
        types = Draft202012Validator.TYPE_CHECKER.redefine("integer", lambda _, value: type(value) is int)
        validator = validators.extend(Draft202012Validator, type_checker=types)(schema)
        for error in validator.iter_errors(data):
            parts = list(error.absolute_path)
            if error.validator == "additionalProperties" and isinstance(error.instance, dict):
                for key in sorted(set(error.instance) - set(error.schema.get("properties", {}))):
                    self.add("MALFORMED", pointer(parts + [key]), "Unknown property.")
            elif error.validator == "uniqueItems" and isinstance(error.instance, list):
                seen = set()
                for i, item in enumerate(error.instance):
                    key = json.dumps(item, sort_keys=True, ensure_ascii=True)
                    if key in seen:
                        self.add("MALFORMED", pointer(parts + [i]), "Duplicate array value.")
                    seen.add(key)
            else:
                self.add("MALFORMED", pointer(parts), "Schema rule violated: " + error.validator + ".")
                if error.validator == "minItems" and "then" in error.absolute_schema_path:
                    self.add("MALFORMED", pointer(parts[:-1]), "Conditional record requirements are not satisfied.")
        return not self.findings

    def baseline(self, record, where):
        repo, revision = record["repository"], record["revision"]
        if not valid_repository(repo):
            self.add("MALFORMED", where + "/repository", "Invalid canonical public HTTPS repository URL.")
            return None
        if not valid_revision(revision):
            self.add("BASELINE_UNAVAILABLE", where + "/revision", "Prohibited immutable revision.")
            return None
        if repo not in self.repositories:
            self.add("BASELINE_UNAVAILABLE", where + "/repository", "No explicit local checkout mapping.")
            return None
        key = (repo, revision)
        if key not in self.views:
            try:
                self.views[key] = GitObjects(self.repositories[repo], revision)
            except (ReferenceFailure, UnicodeError):
                self.views[key] = None
        if self.views[key] is None:
            self.add("BASELINE_UNAVAILABLE", where + "/revision", "Required Git commit/tree unavailable.")
        return self.views[key]

    def location(self, record, where, view, path_pointer=None):
        path_pointer = path_pointer or where + "/path"
        good = True
        if not valid_path(record["path"]):
            self.add("MALFORMED", path_pointer, "Unsafe repository-relative path.")
            good = False
        if not selector_syntax(record["selector"]):
            self.add("MALFORMED", where + "/selector", "Invalid literal selector syntax.")
            good = False
        if not good or record.get("state") == "planned":
            return good
        if view is None:
            self.skipped.add("locations at unavailable baselines")
            return None
        try:
            raw = view.read(record["path"])
        except ReferenceFailure as exc:
            self.add("STALE_LOCATION", path_pointer, str(exc))
            return False
        try:
            self.selectors.resolve(record["path"], record["selector"], raw)
        except ReferenceFailure as exc:
            self.add("STALE_LOCATION", where + "/selector", str(exc))
            return False
        return True

    def reference(self, record, where):
        view = self.baseline(record, where)
        return self.location(record, where, view)

    def catalog(self, view):
        if view is None:
            self.skipped.add("catalog identity, versions, and missing requirements")
            return None
        # Reuse the public catalog/definition authority on a synthetic snapshot.
        # Write only regular Markdown blobs and the catalog, never checkout links.
        try:
            with tempfile.TemporaryDirectory(prefix="barometer-catalog-") as folder:
                root = Path(folder)
                for path, (mode, kind, _) in view.entries.items():
                    if any(part.startswith(".") for part in path.split("/")):
                        continue
                    if path == "requirements/catalog.json" or path.endswith(".md"):
                        if mode not in ("100644", "100755") or kind != "blob" or not valid_path(path):
                            raise ReferenceFailure("Non-regular/unsafe file in catalog definition scope.")
                        target = root / path
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(view.read(path))
                errors = check_requirements.check(root)
                if errors:
                    raise ReferenceFailure("Public catalog allocation/source/anchor integrity failed.")
                return check_requirements.load_catalog(root / "requirements/catalog.json")
        except (OSError, ValueError, UnicodeError):
            self.add("CATALOG_INVALID", "/specification", "Public catalog allocation/source/anchor integrity failed.")
            self.skipped.add("requirement identity and missing requirements at invalid catalog")
            return None

    def duplicates(self, values, fields, where):
        seen = set()
        for i, item in enumerate(values):
            key = tuple(item[f] for f in fields)
            if key in seen:
                self.add("MALFORMED", where + "/" + str(i), "Duplicate mapping tuple.")
            seen.add(key)

    def records(self, data):
        maps = {}
        for name in ("requirements", "cases", "issues", "evidence"):
            counts = Counter(record["id"] for record in data[name])
            maps[name] = {record["id"]: (i, record) for i, record in enumerate(data[name])
                          if counts[record["id"]] == 1}
            seen = set()
            for i, record in enumerate(data[name]):
                if record["id"] in seen:
                    self.add("DUPLICATE_ID", f"/{name}/{i}/id", "Duplicate record ID; dependent checks skipped.", record["id"])
                seen.add(record["id"])
            if any(count > 1 for count in counts.values()):
                self.skipped.add("references and claims depending on ambiguous duplicate IDs")
        return maps

    def validate(self, raw):
        try:
            data = strict_json(raw)
        except DecodeFailure as exc:
            for code, where, message in exc.findings:
                self.add(code, where, message)
            self.skipped.add("schema and semantic checks after decoding failure")
            return self.report()
        if not self.schema(data):
            self.skipped.add("semantic checks after structural failure")
            return self.report()
        self.baselines = {name: data[name] for name in ("specification", "implementation")}
        roots = {name: self.baseline(data[name], "/" + name) for name in self.baselines}
        for name in roots:
            if data[name]["revision"] != self.expected[name]:
                self.add("STALE_BASELINE", "/" + name + "/revision", "Manifest differs from explicitly selected baseline.")
        catalog = self.catalog(roots["specification"])
        maps = self.records(data)
        edges = {}
        ambiguous = {name: {r["id"] for r in data[name]} - set(maps[name]) for name in maps}

        def link(kind, identity, where, owner):
            if identity in ambiguous[kind]:
                return None
            if identity not in maps[kind]:
                self.add("DANGLING_REFERENCE", where, "Reference has no target record.", identity)
                return None
            edges.setdefault(owner, set()).add((kind, identity))
            return maps[kind][identity][1]

        for i, r in enumerate(data["requirements"]):
            owner = ("requirements", r["id"])
            for field, kind in (("case_ids", "cases"), ("issue_ids", "issues"), ("review_evidence_ids", "evidence")):
                for j, identity in enumerate(r[field]):
                    link(kind, identity, f"/requirements/{i}/{field}/{j}", owner)
            for j, support in enumerate(r["support"]):
                for k, identity in enumerate(support["evidence_ids"]):
                    link("evidence", identity, f"/requirements/{i}/support/{j}/evidence_ids/{k}", owner)
            self.duplicates(r["implementation_locations"], ("path", "selector", "state"), f"/requirements/{i}/implementation_locations")
            self.duplicates(r["support"], ("kind", "scope"), f"/requirements/{i}/support")
        for i, case in enumerate(data["cases"]):
            for j, identity in enumerate(case["evidence_ids"]):
                link("evidence", identity, f"/cases/{i}/evidence_ids/{j}", ("cases", case["id"]))
        for i, evidence in enumerate(data["evidence"]):
            for j, identity in enumerate(evidence["requirement_ids"]):
                link("requirements", identity, f"/evidence/{i}/requirement_ids/{j}", ("evidence", evidence["id"]))
            for j, result in enumerate(evidence["case_results"]):
                # Back references validate identity but do not create reachability.
                if result["case_id"] not in maps["cases"] and result["case_id"] not in ambiguous["cases"]:
                    self.add("DANGLING_REFERENCE", f"/evidence/{i}/case_results/{j}/case_id", "Case result has no mapped case.", result["case_id"])
            self.duplicates(evidence["case_results"], ("case_id",), f"/evidence/{i}/case_results")
        reached = set()
        pending = [("requirements", r["id"]) for r in data["requirements"]]
        while pending:
            node = pending.pop()
            if node in reached:
                continue
            reached.add(node)
            pending.extend(edges.get(node, ()))
        for kind in ("cases", "issues", "evidence"):
            for identity, (i, _) in maps[kind].items():
                if (kind, identity) not in reached:
                    self.add("UNREFERENCED_RECORD", f"/{kind}/{i}/id", "Record is unreachable from requirements.", identity)

        versions = set()
        sources = {r["source"] for r in catalog.values() if r["status"] == "active"} if catalog is not None else set()
        sources.update(data["coverage"]["unallocated_sources"])
        source_view = roots["specification"]
        for path in sorted(sources):
            if source_view is not None:
                try:
                    text = source_view.read(path).decode("utf-8")
                    declarations = [m[1] for line in markdown_lines(text)
                                    if (m := re.fullmatch(r"\*\*(?:Specification )?[Vv]ersion:\*\*\s*`?([^`\s]+)`?\s*", line))]
                    if len(declarations) != 1:
                        self.add("STALE_BASELINE", "/specification/version", "Applicable source has no unique version declaration.", path)
                    versions.update(declarations)
                except (ReferenceFailure, UnicodeError):
                    self.skipped.add("version declarations at unavailable source paths")
        if versions and versions != {data["specification"]["version"]}:
            self.add("STALE_BASELINE", "/specification/version", "Specification version disagrees with applicable source declarations.")

        if catalog is not None:
            for kind, field in (("requirements", "id"), ("evidence", "requirement_ids")):
                for i, record in enumerate(data[kind]):
                    ids = [(record[field], f"/{kind}/{i}/{field}")] if kind == "requirements" else [
                        (identity, f"/{kind}/{i}/{field}/{j}") for j, identity in enumerate(record[field])]
                    for identity, where in ids:
                        if identity not in catalog:
                            self.add("UNKNOWN_REQUIREMENT", where, "Requirement absent from selected public catalog.", identity)
                        elif catalog[identity]["status"] != "active":
                            self.add("RETIRED_REQUIREMENT", where, "Requirement retired at selected baseline.", identity)
            present = {r["id"] for r in data["requirements"]}
            for identity, r in catalog.items():
                if r["status"] == "active" and identity not in present:
                    self.add("MISSING_REQUIREMENT", "/requirements", "Active public requirement is unmapped.", identity,
                             "gap" if data["coverage"]["mode"] == "partial" else "error")

        location_ok = {}
        for i, r in enumerate(data["requirements"]):
            results = [self.location(loc, f"/requirements/{i}/implementation_locations/{j}", roots["implementation"])
                       for j, loc in enumerate(r["implementation_locations"])]
            location_ok[("requirements", i)] = all(results)
        for i, case in enumerate(data["cases"]):
            if check_requirements.IDENTIFIER.fullmatch(case["id"]):
                self.add("MALFORMED", f"/cases/{i}/id", "Case IDs must be distinct from public requirement IDs.", case["id"])
            location_ok[("cases", i)] = self.location(case["location"], f"/cases/{i}/location", roots["implementation"])
        for i, issue in enumerate(data["issues"]):
            self.duplicates(issue["resolution_references"], ("repository", "revision", "path", "selector"), f"/issues/{i}/resolution_references")
            ok = self.reference(issue["finding"], f"/issues/{i}/finding")
            resolved = [self.reference(ref, f"/issues/{i}/resolution_references/{j}")
                        for j, ref in enumerate(issue["resolution_references"])]
            location_ok[("issues", i)] = None if ok is None or None in resolved else ok and all(resolved)
            if issue["disposition"] == "closed":
                if location_ok[("issues", i)] is None:
                    self.skipped.add("issue closure claims at unavailable reference baselines")
                elif not issue["resolution_references"] or not location_ok[("issues", i)]:
                    self.add("CLAIM_NOT_JUSTIFIED", f"/issues/{i}/disposition", "Closed issue lacks resolvable public resolution.", issue["id"])
                self.review_assertions.append("Issue " + issue["id"] + ": identity, public disposition, and applicable closure/adoption rationale require review.")
        for j, path in enumerate(data["coverage"]["unallocated_sources"]):
            self.location({"path": path, "selector": "file"}, f"/coverage/unallocated_sources/{j}",
                          roots["specification"], path_pointer=f"/coverage/unallocated_sources/{j}")
            self.add("UNALLOCATED_REQUIREMENTS", f"/coverage/unallocated_sources/{j}", "Listed source contains unallocated obligations.", path, "gap")
        self.add("UNALLOCATED_REQUIREMENTS", "/coverage/notes", "Normative inventory completeness remains unverified.", level="gap")

        def get(kind, identity):
            return maps[kind].get(identity, (None, None))

        evidence_ok = {}
        for i, e in enumerate(data["evidence"]):
            where = f"/evidence/{i}"
            good = self.reference(e["reference"], where + "/reference")
            for name in ("specification", "implementation"):
                if e[name + "_revision"] != data[name]["revision"]:
                    self.add("EVIDENCE_MISMATCH", where + "/" + name + "_revision", "Evidence baseline does not match root baseline.", e["id"])
                    good = False
            for j, result in enumerate(e["case_results"]):
                _, case = get("cases", result["case_id"])
                if case is not None and (e["id"] not in case["evidence_ids"] or result["result"] != case["status"]):
                    self.add("EVIDENCE_MISMATCH", where + f"/case_results/{j}", "Case result/back-reference disagrees with the mapped case.", result["case_id"])
                    good = False
            evidence_ok[e["id"]] = good
            self.review_assertions.append("Evidence " + e["id"] + ": selected content, authenticity, kind, IDs, baselines, scope, inputs/environment, and limits require review.")

        def matching_evidence(identity, kinds, requirements, scope=None):
            _, evidence = get("evidence", identity)
            if (evidence is None or evidence["kind"] not in kinds
                    or not set(requirements) <= set(evidence["requirement_ids"])
                    or (scope is not None and evidence["scope"] != scope)):
                return False
            return evidence_ok.get(identity, False)

        case_good = {}
        for i, case in enumerate(data["cases"]):
            owners = [r["id"] for r in data["requirements"] if case["id"] in r["case_ids"]]
            good = location_ok[("cases", i)]
            for j, identity in enumerate(case["evidence_ids"]):
                _, e = get("evidence", identity)
                if e is None:
                    good = False
                    continue
                matching = [r for r in e["case_results"] if r["case_id"] == case["id"]]
                matched = matching_evidence(identity, {"conformance"}, owners, case["scope"])
                if (matched is False or len(matching) != 1 or matching[0]["result"] != case["status"]):
                    self.add("EVIDENCE_MISMATCH", f"/cases/{i}/evidence_ids/{j}", "Evidence must match case kind, owners, scope, result, and baselines.", identity)
                    good = False
                elif matched is None:
                    self.skipped.add("case evidence at unavailable reference baselines")
                    good = False
            case_good[case["id"]] = good and case["status"] == "passed" and bool(case["evidence_ids"])

        for i, r in enumerate(data["requirements"]):
            where = f"/requirements/{i}"
            good = location_ok[("requirements", i)] and bool(r["implementation_locations"])
            good = good and all(loc["state"] == "existing" for loc in r["implementation_locations"])
            good = good and bool(r["case_ids"]) and all(case_good.get(identity, False) for identity in r["case_ids"])
            for j, identity in enumerate(r["review_evidence_ids"]):
                matched = matching_evidence(identity, {"review"}, [r["id"]])
                if matched is False:
                    if identity in maps["evidence"]:
                        self.add("EVIDENCE_MISMATCH", where + f"/review_evidence_ids/{j}", "Review evidence must cover this requirement and exact baselines.", identity)
                    good = False
                elif matched is None:
                    self.skipped.add("review evidence at unavailable reference baselines")
                    good = False
            good = good and bool(r["review_evidence_ids"])
            for identity in r["issue_ids"]:
                idx, issue = get("issues", identity)
                good = good and issue is not None and issue["disposition"] == "closed" and location_ok.get(("issues", idx), False)
            prerequisites = (roots["specification"] is not None and roots["implementation"] is not None
                             and catalog is not None and r["id"] not in ambiguous["requirements"])
            used_evidence = set(r["review_evidence_ids"])
            for identity in r["case_ids"]:
                _, case = get("cases", identity)
                if case is not None:
                    used_evidence.update(case["evidence_ids"])
            prerequisites = prerequisites and not any(identity in evidence_ok and evidence_ok[identity] is None for identity in used_evidence)
            prerequisites = prerequisites and not any(location_ok.get(("issues", get("issues", identity)[0])) is None
                                                       for identity in r["issue_ids"] if identity in maps["issues"])
            if r["implementation_status"] == "implemented":
                if prerequisites and not good:
                    self.add("CLAIM_NOT_JUSTIFIED", where + "/implementation_status", "Implementation lacks reviewed passing coverage or has unresolved blockers.", r["id"])
                elif not prerequisites:
                    self.skipped.add("implementation claims with unavailable prerequisites")
            else:
                if not any(loc["state"] == "existing" for loc in r["implementation_locations"]):
                    self.add("MISSING_IMPLEMENTATION", where + "/implementation_locations", "No existing implementation mapped.", r["id"], "gap")
                if not r["case_ids"] or not all(case_good.get(identity, False) for identity in r["case_ids"]):
                    self.add("MISSING_CONFORMANCE", where + "/case_ids", "Mapped conformance coverage lacks passing results.", r["id"], "gap")
            for j, support in enumerate(r["support"]):
                where_support = where + f"/support/{j}"
                required = {"core": {"review"}, "platform": {"platform"}, "field": {"platform", "field"}}[support["kind"]]
                kinds = set()
                for k, identity in enumerate(support["evidence_ids"]):
                    _, e = get("evidence", identity)
                    if e is None:
                        continue
                    matched = matching_evidence(identity, required, [r["id"]], support["scope"])
                    if matched is True:
                        kinds.add(e["kind"])
                    elif matched is False:
                        self.add("EVIDENCE_MISMATCH", where_support + f"/evidence_ids/{k}", "Support evidence must match kind, requirement, exact scope, and baselines.", identity)
                    else:
                        self.skipped.add("support evidence at unavailable reference baselines")
                support_prerequisites = prerequisites and not any(evidence_ok.get(identity, False) is None for identity in support["evidence_ids"])
                if support["status"] == "supported":
                    if support_prerequisites and (not good or r["implementation_status"] != "implemented" or not required <= kinds):
                        self.add("CLAIM_NOT_JUSTIFIED", where_support + "/status", "Support claim lacks implemented coverage and required scoped evidence.", r["id"])
                    elif not support_prerequisites:
                        self.skipped.add("support claims with unavailable prerequisites")
        return self.report()


def check(raw, repositories, expected_spec, expected_impl, mode="current", schema_path=None, go_selector=None):
    return Checker(repositories, expected_spec, expected_impl, mode,
                   schema_path or SCRIPT_ROOT.parent / "traceability/manifest.schema.json", go_selector).validate(raw)


def render_text(report):
    lines = [f"Traceability metadata {'valid' if report['valid'] else 'invalid'} ({report['validation_mode']})."]
    for name, revision in report["expected_baselines"].items():
        lines.append(f"expected {name}: {revision}")
    if report["baselines"] is not None:
        for name, baseline in report["baselines"].items():
            lines.append(f"{name}: {baseline['repository']} @ {baseline['revision']}")
    lines.append("schema SHA-256: " + str(report["schema_sha256"]))
    for f in report["findings"]:
        lines.append(f"{f['level']} {f['code']} {f['pointer'] or '<root>'} {f['related_id']}: {f['explanation']}")
    for skipped in report["skipped_checks"]:
        lines.append("Skipped: " + skipped)
    for assertion in report["review_assertions"]:
        lines.append("Review assertion: " + assertion)
    lines.extend("Review limit: " + value for value in report["review_limits"])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--repository", action="append", required=True, metavar="URL=CHECKOUT")
    parser.add_argument("--expected-specification", required=True)
    parser.add_argument("--expected-implementation", required=True)
    parser.add_argument("--mode", choices=("current", "historical"), required=True)
    parser.add_argument("--schema", type=Path, default=SCRIPT_ROOT.parent / "traceability/manifest.schema.json")
    parser.add_argument("--go-selector", type=Path, help="trusted compiled Go declaration resolver")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--output", type=Path, help="report file; default stdout")
    args = parser.parse_args(argv)
    repositories = {}
    for value in args.repository:
        url, sep, path = value.partition("=")
        if not sep or not valid_repository(url) or not path or url in repositories:
            parser.error("repository mappings must be distinct canonical URL=CHECKOUT pairs")
        repositories[url] = Path(path)
    if not all(valid_revision(v) for v in (args.expected_specification, args.expected_implementation)):
        parser.error("expected baselines must be full nonzero lowercase commit IDs")
    try:
        raw = args.manifest.read_bytes()
    except OSError:
        parser.error("manifest file is unavailable")
    try:
        report = check(raw, repositories, args.expected_specification, args.expected_implementation,
                       args.mode, args.schema, args.go_selector)
    except (ImportError, OSError, ValueError) as exc:
        parser.error("checker/schema setup failed: " + type(exc).__name__)
    rendered = json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2) + "\n" if args.format == "json" else render_text(report)
    try:
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    except OSError:
        parser.error("report output is unavailable")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
