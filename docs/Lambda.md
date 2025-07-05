# Tool Documentation: Lambda (Λ)

**Type:** Core Tool / Linter
**Status:** Operational

## Definition

Lambda is a deterministic linter that checks the Architect's Codex for **philosophical and ethical consistency**. Unlike typical linters that check for code style or syntax errors, Lambda checks for adherence to the Enclave's foundational principles as defined in a ruleset. It is the "Law" component of the **[Integrated Adherence Protocol](./Integrated-Adherence-Protocol.md)**.

## Configuration Files

Lambda's behavior is driven by two key YAML files:

### 1. `soul.rules.yaml`

This file contains the list of rules the linter will check. Each rule has several properties:
-   **`name`**: A human-readable identifier for the rule.
-   **`severity`**: Can be `ERROR`, `STYLE`, or `STRUCTURE`. This is used for reporting and filtering.
-   **`description`**: A detailed explanation of what the rule checks for and why.
-   **`check`**: An object defining the logic.
    -   **`type`**: The type of check to perform (e.g., `contains_text`, `must_start_with`, `lacks_link_on_entity_interaction`).
    -   **`scope`**: (Optional) Restricts the check to a specific directory (e.g., `10_Lexicon`).
    -   **`params`**: A dictionary of parameters required by the check type, such as a list of forbidden words or a required prefix.

### 2. `sovereign_entities.yaml`

This file is a simple list of concepts that are considered "sovereign entities". It is used by the `lacks_link_on_entity_interaction` check to identify when a document describes an interaction between these entities, which may trigger rules requiring that `[[10_Lexicon/Consent.md]]` be referenced.

## Output Formats

Lambda can produce output in two formats, controlled by the `--output-format` argument.

1.  **`text` (Default)**: A human-readable summary of violations, grouped by rule. The `--verbose` flag can be used to show a detailed report for each violation.
2.  **`json`**: A machine-readable JSON object containing a detailed list of every violation found. This is ideal for piping to other scripts or for automated processing.

### Example JSON Output Snippet
```json
{
  "lambda_version": "1.3",
  "violations_found": 1,
  "violations": [
    {
      "file_path": "./30_Mechanica/Some-Protocol.md",
      "line_number": 25,
      "rule_name": "Tool-Making Fallacy Check",
      "severity": "STYLE",
      "error_type": "contains_text",
      "details": {
        "forbidden_word": "user",
        "full_line_content": "The user then performs an action."
      }
    }
  ]
}
```