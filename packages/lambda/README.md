# Lambda (Λ) - The Deterministic Linter

The `lambda` package is a deterministic linter that checks for **philosophical and ethical consistency** in the Architect's Codex, not code syntax. It operates based on a set of explicit rules defined in a `.yaml` file.

`lambda` is the implementation of "The Law" stage in the **[Integrated Adherence Protocol](../../../docs/Integrated-Adherence-Protocol.md)**.

## Basic Usage

`lambda` is designed to be chained with `sigma`. To lint the `codex` repository:
```bash
sigma --codex | lambda
```
## Configuration
-   **Rules:** Linter rules are defined in `soul.rules.yaml`.
-   **Entities:** Sovereign entities for rule checking are defined in `sovereign_entities.yaml`.

For more detailed information, see the full **[Lambda Documentation](../../../docs/Lambda.md)**.
