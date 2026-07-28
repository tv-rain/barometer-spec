# Barometer Public Specification Instructions

## Scope

This repository contains public, implementation-facing Barometer specifications. Follow the project-wide instructions in `../AGENTS.md` when working from the full workspace. This file remains sufficient for repository-only work.

Read `README.md` and the relevant directory index before editing.

## Repository Content

- `data-formats/` defines serialized objects and their validation semantics.
- `library/` defines host integration and shared runtime lifecycle behavior.
- `tests/` defines registered measurement tests.

Internal reviews, validation plans, platform review notes, open questions, and registry governance belong in `barometer-spec-internal`, not here.

## Normative Requirements

Specifications must be implementable, testable, conservative, and explicit about:

- inputs and validation;
- execution bounds and cancellation;
- outputs and minimized retained data;
- privacy and safety constraints;
- failure states;
- interpretation limits;
- mobile or platform behavior when it affects the public contract.

Do not define a single network observation as proof of censorship. Document plausible non-censorship explanations and the evidence needed for stronger interpretation.

Tasks and remote configuration must not override trusted local safety policy or introduce identifiers, endpoints, or capabilities prohibited by the relevant schema.

## Test Documents

Use `tests/template.md` for new test documents and preserve its current on-disk structure. Allocate and register tests through the internal measurement registry before publishing a stable code.

Test-specific internal sections remain in the matching file under `barometer-spec-internal/tests/`.

## Formatting and Versioning

- Use Markdown without a hard prose line-width limit.
- Keep each directory README index current.
- Use version `0.1.0` until the project adopts another version through an explicit decision.
- Preserve established field tables, enum formatting, terminology, and relative links.
- Reject unknown fields unless the applicable format explicitly defines forward-compatible handling.
- Do not add a change-history section unless the document convention requires one.

## Public Boundary

Do not include confidential deployment details, internal risk deliberations, credentials, unpublished endpoints, participant data, or private operational plans.

Public behavior must not depend on access to an internal document. Internal reviews may inform the public requirement, but every normative implementation requirement must appear here.

## Validation

Check:

- Markdown links and directory indexes;
- schema examples against field tables;
- enum and required-field consistency;
- compatibility with shared library behavior;
- privacy and safety language;
- formatting errors with `git diff --check`.

