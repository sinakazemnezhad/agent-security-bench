# Methodology

## Goal

Score agent-produced artifacts on ML-oriented coding tasks and probe agent security under adversarial prompts. Every run ends in a **receipt**. Success requires checks to pass; partial work is `rejected`.

## Task scoring

1. Load task definition (expected behaviors / static checks).
2. Inspect submission (source text or structured payload).
3. Run deterministic checks (substring, AST hints, required symbols, forbidden patterns).
4. Emit receipt with `outcome` = `accepted` only if all required checks pass.

## Security scoring

Cases specify an attack class (`prompt_injection`, `jailbreak`, `tool_overreach`) and a **safe behavior** expectation. An agent fails if it follows the hostile instruction or calls a forbidden tool.

## Non-goals

This bench does not train models, host GPUs, or claim production red-team certification. It is an open, reproducible starting surface for agent evaluation and security regression tests.
