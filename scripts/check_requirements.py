"""Check explicit requirement allocations, definitions, and consumer references."""

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys


NAMESPACE = re.compile(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*")
IDENTIFIER = re.compile(r"REQ-([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*)-([0-9]{4})")
ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
REFERENCE = re.compile(r"(?:<!-- requirement-(ref|history): (\S+) -->|// requirement-(ref|history): (\S+))")
FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse_id(value):
    match = IDENTIFIER.fullmatch(value) if isinstance(value, str) else None
    require(match is not None and match[2] != "0000", f"malformed ID: {value!r}")
    return match[1], int(match[2])


def load_catalog(path):
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    require(isinstance(data, dict) and set(data) == {"format_version", "namespaces", "requirements"}, "invalid catalog fields")
    require(type(data["format_version"]) is int and data["format_version"] == 1, "unsupported catalog format_version")
    namespaces = data["namespaces"]
    require(isinstance(namespaces, dict) and namespaces, "namespaces must be a nonempty object")
    for name, owner in namespaces.items():
        require(NAMESPACE.fullmatch(name) is not None, f"malformed namespace: {name}")
        require(isinstance(owner, dict) and set(owner) == {"owner", "scope"}, f"invalid namespace fields: {name}")
        require(all(isinstance(v, str) and v.strip() for v in owner.values()), f"empty namespace owner/scope: {name}")
    require(isinstance(data["requirements"], list), "requirements must be an array")
    records = {}
    for record in data["requirements"]:
        require(isinstance(record, dict) and set(record) == {"id", "status", "source", "successors", "reason"}, "invalid requirement fields")
        identity = record["id"]
        namespace, _ = parse_id(identity)
        require(namespace in namespaces, f"undeclared namespace: {identity}")
        require(identity not in records, f"duplicate catalog ID: {identity}")
        require(record["status"] in ("active", "retired"), f"invalid status: {identity}")
        source = record["source"]
        require(isinstance(source, str) and source, f"invalid source: {identity}")
        parts = PurePosixPath(source)
        require(not parts.is_absolute() and ".." not in parts.parts and not any(p.startswith(".") for p in parts.parts)
                and str(parts) == source and "\\" not in source and parts.suffix == ".md", f"unsafe source path: {identity}")
        successors = record["successors"]
        require(isinstance(successors, list), f"successors must be an array: {identity}")
        for successor in successors:
            parse_id(successor)
        require(len(set(successors)) == len(successors) and identity not in successors, f"invalid successors: {identity}")
        require(isinstance(record["reason"], str), f"invalid reason: {identity}")
        if record["status"] == "active":
            require(not successors and record["reason"] == "", f"active ID has retirement metadata: {identity}")
        else:
            require(bool(record["reason"].strip()), f"retired ID needs a reason: {identity}")
        records[identity] = record
    for identity, record in records.items():
        require(all(s in records for s in record["successors"]), f"unknown successor: {identity}")
    # Topological traversal handles long split/merge histories in linear time.
    incoming = dict.fromkeys(records, 0)
    for record in records.values():
        for successor in record["successors"]:
            incoming[successor] += 1
    pending = [identity for identity, count in incoming.items() if count == 0]
    visited = 0
    while pending:
        current = pending.pop()
        visited += 1
        for successor in records[current]["successors"]:
            incoming[successor] -= 1
            if incoming[successor] == 0:
                pending.append(successor)
    require(visited == len(records), "successor cycle in catalog")
    return records


def visible_lines(path):
    """Ignore fenced Markdown examples; Go comments are read as ordinary lines."""
    fence = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if path.suffix == ".md":
            match = FENCE.fullmatch(line)
            if match:
                delimiter, suffix = match.groups()
                if fence is None:
                    fence = delimiter
                elif delimiter[0] == fence[0] and len(delimiter) >= len(fence) and not suffix.strip():
                    fence = None
                continue
            if fence is not None:
                continue
        yield number, line
    require(fence is None, f"unclosed Markdown fence: {path.name}")


def documents(root):
    """Only explicitly selected roots; skip hidden trees and never follow links."""
    require(root.is_dir(), f"scan root is not a directory: {root.name}")
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if path.is_symlink():
            require(not path.is_dir() and path.suffix not in (".md", ".go"), f"symlink in scan scope: {relative}")
            continue
        if path.is_file() and path.suffix in (".md", ".go"):
            yield path


def check(spec_root, consumers=(), baseline=None):
    spec_root = spec_root.resolve()
    records = load_catalog(spec_root / "requirements/catalog.json")
    errors = []
    definitions = {}
    if baseline is not None:
        previous = load_catalog(baseline)
        highest = {}
        for identity, record in previous.items():
            namespace, number = parse_id(identity)
            highest[namespace] = max(number, highest.get(namespace, 0))
            if identity not in records:
                errors.append(f"deleted allocation: {identity}")
            elif record["status"] == "retired" and records[identity]["status"] != "retired":
                errors.append(f"reactivated retired ID: {identity}")
        for identity in records.keys() - previous.keys():
            namespace, number = parse_id(identity)
            if number <= highest.get(namespace, 0):
                errors.append(f"reused allocation gap: {identity}")

    roots = [spec_root] + [p.resolve() for p in consumers]
    for i, root in enumerate(roots):
        require(not any(root == earlier or root in earlier.parents or earlier in root.parents for earlier in roots[:i]), "scan roots must be distinct and non-overlapping")
        for path in documents(root):
            lines = list(visible_lines(path))
            relative = path.relative_to(root).as_posix()
            for index, (number, line) in enumerate(lines):
                stripped = line.strip()
                location = f"{root.name}/{relative}:{number}"
                # Reserve anchors beginning REQ- and standalone reference comments.
                if re.search(r"<a\s+id\s*=\s*['\"]req-", stripped, re.IGNORECASE):
                    match = ANCHOR.fullmatch(stripped)
                    if match is None:
                        errors.append(f"{location}: malformed requirement anchor")
                        continue
                    identity = match[1]
                    try:
                        parse_id(identity)
                    except ValueError as exc:
                        errors.append(f"{location}: {exc}")
                        continue
                    if root != spec_root:
                        errors.append(f"{location}: consumer cannot define {identity}")
                        continue
                    definitions.setdefault(identity, []).append(relative)
                    record = records.get(identity)
                    if record is None:
                        errors.append(f"{location}: uncataloged definition: {identity}")
                        continue
                    following = [text.strip() for _, text in lines[index + 1:] if text.strip()]
                    label = f"**{identity}{' (retired)' if record['status'] == 'retired' else ''}:**"
                    if not following or following[0] != label:
                        errors.append(f"{location}: missing or incorrect requirement label: {identity}")
                    if len(following) < 2 or following[1].startswith(("#", "<a ", "<!--", "**REQ-")):
                        errors.append(f"{location}: missing requirement text: {identity}")
                if re.match(r"(?:<!--|//)\s*requirement-(?:ref|history)\b", stripped, re.IGNORECASE):
                    match = REFERENCE.fullmatch(stripped)
                    if match is None or (path.suffix == ".go") != stripped.startswith("//"):
                        errors.append(f"{location}: malformed requirement reference")
                        continue
                    kind = match[1] or match[3]
                    identity = match[2] or match[4]
                    try:
                        parse_id(identity)
                    except ValueError as exc:
                        errors.append(f"{location}: {exc}")
                        continue
                    if identity not in records:
                        errors.append(f"{location}: unresolved reference: {identity}")
                    elif kind == "ref" and records[identity]["status"] != "active":
                        errors.append(f"{location}: current reference to retired ID: {identity}")
    for identity, record in records.items():
        locations = definitions.get(identity, [])
        if not locations:
            errors.append(f"orphaned catalog ID (missing anchor): {identity}")
        elif len(locations) > 1:
            errors.append(f"duplicate definition: {identity}")
        elif locations[0] != record["source"]:
            errors.append(f"source mismatch: {identity}: expected {record['source']}, found {locations[0]}")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--consumer", type=Path, action="append", default=[], help="explicit consumer checkout to scan; repeatable")
    parser.add_argument("--baseline", type=Path, help="prior catalog JSON, required for allocation-history validation after initial adoption")
    args = parser.parse_args(argv)
    try:
        errors = check(args.spec_root, args.consumer, args.baseline)
    except (ValueError, OSError) as exc:
        errors = [str(exc)]
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Requirement structure valid ({len(args.consumer)} consumer roots; "
          f"allocation history {'checked' if args.baseline else 'not checked'}). Coverage and conformance are not assessed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
