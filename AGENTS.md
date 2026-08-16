# Agent notes for contributors and coding agents

- Prefer deterministic checks and receipt emission over subjective scoring.
- Do not weaken security cases to make agents look better.
- Keep proprietary company runtimes out of this repository.
- Cross-link persian-llm-reference when documenting Persian/ML evaluation context.
- Every scored run must write a receipt; `outcome=accepted` only when required checks pass.
- Prefer AST / schema checks when string predicates are ambiguous.
- Security logs that omit `tool_calls` for monitored tools fail closed on arg policies.
- CLI: `asb list`, `asb catalog`, `asb score`, `asb security`, `asb batch`, `asb validate-receipt`, `asb selftest`.
