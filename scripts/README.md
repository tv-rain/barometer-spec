# Specification Validation Tools

## Directory Index

- [`check_requirements.py`](check_requirements.py) — validates the public requirement catalog, explicit definitions, and optional consumer references.
- [`test_check_requirements.py`](test_check_requirements.py) — synthetic tests for valid editing, relocation, retirement, malformed metadata, and dangling references.
- [`check_traceability.py`](check_traceability.py) — deterministic text/JSON traceability reports against explicitly mapped immutable Git baselines.
- [`test_check_traceability.py`](test_check_traceability.py) — offline temporary Git repositories exercising positive claims, the public invalid scenarios, and reference/evidence/claim boundaries.
- [`go_selector.go`](go_selector.go) — standard-library parser for Go declaration selectors; does not compile or execute the inspected code.
- [`requirements.txt`](requirements.txt) — pinned Python dependencies for the traceability checker only.

## Requirements and Commands

Use Python 3.9 or later with its standard library; no packages, network access, private repository, or Go toolchain are required. Run from the public specification repository:

```sh
python3 -B scripts/check_requirements.py
python3 -B -m unittest discover -s scripts -p 'test_check_requirements.py' -v
git diff --check
```

To check consumers in the coordinated workspace, supply only the intended checkouts explicitly:

```sh
python3 -B scripts/check_requirements.py --consumer ../barometer-spec-internal --consumer ../barometer-go
```

The checker scans `.md` and `.go` files under those roots, including new files, skipping hidden files/directories and fenced Markdown examples. It rejects document symlinks and directory symlinks, overlapping roots, and missing consumer directories. It does not automatically discover or read sibling repositories. Python test strings and unrelated file types are outside reference scanning. Use standalone comments in the [documented syntax](../requirements/README.md#consumer-references) for checked citations. Bare prose IDs and links alone are not machine-readable references.

## Traceability Checker

The [manifest contract](../traceability/README.md) defines the diagnostic codes, gap levels, and claim gates. This tooling changes no runtime behavior, specification maturity, or support status. It requires Python 3.10 or later, the pinned packages, and Git. The declaration helper and the full automated suite require Go 1.18 or later. CI uses Python 3.11/3.14 and Go 1.26.0. The requirement-ID checker above retains its Python standard-library-only workflow.

Prepare an isolated environment and build the trusted helper outside the checkout:

```sh
python3 -m venv /tmp/barometer-traceability-venv
/tmp/barometer-traceability-venv/bin/python -m pip install -r scripts/requirements.txt
go build -o /tmp/barometer-go-selector scripts/go_selector.go
/tmp/barometer-traceability-venv/bin/python -B -m unittest discover -s scripts -p 'test_*.py' -v
git diff --check
```

Dependency installation may need network access. The checker and tests never fetch repositories or schemas, use a private repository, or perform network measurements. `file` and Markdown selectors require no helper. Existing Go `symbol:` selectors require `--go-selector`; a missing resolver or unsupported language fails explicitly. Planned locations only receive path/selector syntax checks and need not exist.

For the illustrative historical example in a coordinated workspace, supply exactly the two intended checkouts:

```sh
/tmp/barometer-traceability-venv/bin/python -B scripts/check_traceability.py traceability/example.partial.json \
  --repository https://github.com/tv-rain/barometer-spec=. \
  --repository https://github.com/tv-rain/barometer-go=../barometer-go \
  --expected-specification 72bbc985280b072e80de65ee9dc13ba600ea2ba4 \
  --expected-implementation d808f1b94e713a5f3970f8c780e0aef5b22a391d \
  --mode historical \
  --schema traceability/manifest.schema.json \
  --go-selector /tmp/barometer-go-selector \
  --format json --output /tmp/barometer-traceability-report.json
```

These commits must already be present in the supplied local repositories. Git reads commit trees/blobs, never the working-tree source/catalog, and refuses lazy fetching and replacement objects. Checkout paths are invocation inputs and do not appear in reports. Repeated `--repository URL=CHECKOUT` arguments map every referenced public repository explicitly; references never choose a local path or executable. `--go-selector` selects trusted tooling, not a manifest-controlled command. The schema is a trusted tooling input (default: the schema beside this checker); preserve its reported SHA-256 and the checker/tooling commit for reproducibility. To use a schema from another reviewed revision, export that revision's schema and supply its path explicitly. Remote schema references are rejected.

Use `--mode current` with independently selected expected specification and implementation commits when checking a current claim. Historical mode also requires explicit expected commits and labels the report historical; neither mode guesses from `HEAD`, a version label, or the manifest itself. A mismatch reports `STALE_BASELINE`. Additional evidence revisions may be later than the implementation they describe, but their declared tested baselines must match the root.

Markdown selectors match literal ATX or Setext heading text or standalone explicit `<a id="literal"></a>` anchors outside fences/comments/indented code. They require exactly one match. Go selectors use parsed file-level function, type, constant, or variable names, `Type.Method` for methods, and `Type.Field`/`Interface.Method` for named type members. Generic receivers retain the containing type name. Local variables, comments, string contents, inferred line numbers, regex patterns, and substring matches do not resolve declarations.

Exit `0` means valid metadata with permitted gaps visible; `1` means invalid metadata/unjustified claims; `2` means invalid invocation or unavailable checker/schema setup. Text is the default; `--format json` returns report version `1`. Both formats identify selected/expected baselines, mode, schema digest, findings, skipped dependent checks, review assertions, and review limits. Findings contain `code`, `level`, `pointer`, `related_id`, and `explanation`, sorted and deduplicated by UTF-8 `(code, pointer, related_id)`. Explanations are not a stable API. Decode/schema failures stop semantics; unavailable prerequisites skip dependent checks while independent findings continue. Partial coverage does not fail merely because obligations or evidence remain missing; catalog-complete mode turns omitted active IDs into errors. Inventory-review/unallocated gaps remain visible in both modes.

Evidence files and issue references are resolved; explicit IDs, scopes, kinds, results, back-references, and tested baselines are compared mechanically. The checker does not infer results from arbitrary prose or authenticate reports. Selected evidence content, complete applicable coverage, public issue disposition/adoption, inventory completeness, and review sufficiency remain human review assertions, printed even when metadata passes. An exit `0` is not a statement of runtime conformance, device/platform support, or field validation.

The [CI workflow](../.github/workflows/validation.yml) runs both tooling suites using only synthetic local repositories. The public invalid scenarios are applied with their original mutations and required diagnostics; their public/Go baseline references are remapped to synthetic fixture commits so CI needs no sibling checkout. Separately, the historical example can be checked against the actual commits using the command above. CI integration here establishes tooling regression checks, not a production implementation manifest or conformance gate for a consumer repository.

## Allocation History

After initial catalog adoption, export the catalog from the reviewed base revision to a temporary file outside the repository and pass it with `--baseline`. For example, from a task branch whose base already includes the catalog:

```sh
git show origin/main:requirements/catalog.json > /tmp/barometer-requirements-base.json
python3 -B scripts/check_requirements.py --baseline /tmp/barometer-requirements-base.json --consumer ../barometer-spec-internal --consumer ../barometer-go
```

Verify that the export succeeds before running the comparison; a missing or malformed baseline fails validation. Record the actual base commit in review evidence, because `origin/main` can move. The initial adoption has no prior catalog; run the structural check and report that history was not checked. History checking rejects deletion, retired-ID reactivation, and new allocation into a previously skipped number below the prior maximum. Human review must still detect semantic reuse, unauthorized ownership changes, and hidden changes to an obligation.

Exit status is `0` for a passing check and `1` for invalid input or detected integrity errors. Diagnostics identify the source file and line where available; those locations are navigation aids, not requirement identity. The check validates only supplied checkouts and marked references. It does not fetch repositories, verify historical citation prose, parse Go syntax, check arbitrary Markdown URLs, infer normative coverage, or run conformance tests.
