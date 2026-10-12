# Specification Validation Tools

## Directory Index

- [`check_requirements.py`](check_requirements.py) — validates the public requirement catalog, explicit definitions, and optional consumer references.
- [`test_check_requirements.py`](test_check_requirements.py) — synthetic tests for valid editing, relocation, retirement, malformed metadata, and dangling references.

## Requirements and Commands

Use Python 3.9 or later with its standard library; no packages, network access, private repository, or Go toolchain are required. Run from the public specification repository:

```sh
python3 -B scripts/check_requirements.py
python3 -B -m unittest discover -s scripts -p 'test_*.py' -v
git diff --check
```

To check consumers in the coordinated workspace, supply only the intended checkouts explicitly:

```sh
python3 -B scripts/check_requirements.py --consumer ../barometer-spec-internal --consumer ../barometer-go
```

The checker scans `.md` and `.go` files under those roots, including new files, skipping hidden files/directories and fenced Markdown examples. It rejects document symlinks and directory symlinks, overlapping roots, and missing consumer directories. It does not automatically discover or read sibling repositories. Python test strings and unrelated file types are outside reference scanning. Use standalone comments in the [documented syntax](../requirements/README.md#consumer-references) for checked citations. Bare prose IDs and links alone are not machine-readable references.

## Allocation History

After initial catalog adoption, export the catalog from the reviewed base revision to a temporary file outside the repository and pass it with `--baseline`. For example, from a task branch whose base already includes the catalog:

```sh
git show origin/main:requirements/catalog.json > /tmp/barometer-requirements-base.json
python3 -B scripts/check_requirements.py --baseline /tmp/barometer-requirements-base.json --consumer ../barometer-spec-internal --consumer ../barometer-go
```

Verify that the export succeeds before running the comparison; a missing or malformed baseline fails validation. Record the actual base commit in review evidence, because `origin/main` can move. The initial adoption has no prior catalog; run the structural check and report that history was not checked. History checking rejects deletion, retired-ID reactivation, and new allocation into a previously skipped number below the prior maximum. Human review must still detect semantic reuse, unauthorized ownership changes, and hidden changes to an obligation.

Exit status is `0` for a passing check and `1` for invalid input or detected integrity errors. Diagnostics identify the source file and line where available; those locations are navigation aids, not requirement identity. The check validates only supplied checkouts and marked references. It does not fetch repositories, verify historical citation prose, parse Go syntax, check arbitrary Markdown URLs, infer normative coverage, or run conformance tests.
