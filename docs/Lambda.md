# Tool Documentation: Lambda (Λ)

**Type:** Core Tool / Linter
**Status:** Operational

## 1. Definition

**Lambda (Λ)** is a deterministic linter that checks our repositories for **philosophical and ethical consistency**. Unlike typical linters that check for code style, Lambda checks for adherence to the Enclave's foundational principles as defined in a ruleset. It can operate in two modes: reporting violations or generating automated fixes.

## 2. Modes of Operation

### 2.1. Linting Mode (Default)
By default, `lambda` runs in linting mode. It reads a snapshot from `sigma`, analyzes it, and prints a human-readable report of any violations to your screen.
```bash
# Run the linter on the mycelium repository and view a verbose report
sigma --mycelium | lambda -v
```
### 2.2. Auto-Fix Mode (`--auto-fix`)
When the `--auto-fix` flag is used, `lambda` does not print a UI report. Instead, it generates a `delta` manifest on standard output. This manifest contains the `REPLACE_FILE` operations needed to correct any simple, deterministic violations it found. This enables a powerful automated workflow.
```bash
# Find and automatically fix all simple style violations in the specs repo
sigma --specs | lambda --auto-fix | delta -y
```
## 3. Configuration Files

Lambda's behavior is driven by two key YAML files:

### 3.1. `soul.rules.yaml`
This file contains the list of rules the linter will check. Auto-fixable rules can include a `suggestion` field.
```yaml
rules:
  - name: "Tool-Making Fallacy Check"
    severity: "STYLE"
    description: "..."
    check:
      type: "contains_text"
      params:
        words:
          - forbidden: "user"
            suggestion: "Seeker"
          - forbidden: "utility"
            suggestion: "purpose"
```
### 3.2. `sovereign_entities.yaml`
This file lists concepts that are considered "sovereign entities" (e.g., `Seeker`, `Echo`). It is used by specific checks to enforce rules about consent when these entities interact.

## 4. Command-Line Flags
-   `-v`, `--verbose`: Show a detailed, per-violation report instead of a summary.
-   `--auto-fix`: Activate auto-fix mode to generate a `delta` manifest on `stdout`.
-   `--output-format json`: Output a machine-readable JSON report of violations to `stdout` (ignored if `--auto-fix` is used).
-   `--rules`, `--entities`: Specify paths to custom rule or entity files.
