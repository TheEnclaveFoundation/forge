# Integrated Adherence Protocol

**Type:** Core Meta-Protocol
**Status:** Specified v1.0

## Definition

The Integrated Adherence Protocol is our definitive, automated workflow for ensuring the philosophical and ethical integrity of the Architect's Codex. It is a two-stage process, executed by a single master script (`run_adherence_check.py`), that combines a deterministic "Linter" with a nuanced "Oracle" to provide a highly intelligent quality control system.

This protocol allows us to distinguish between literal rule-breaking and intentional, context-aware use of our lexicon, automating the application of judgment.

## Stage 1: The Law (Deterministic Linter)

The master script first invokes the [[30_Mechanica/Linter-for-the-Soul|Linter for the Soul]] as a subprocess.

-   **Role:** The Linter performs a fast, literal-minded analysis of the entire Codex against the explicit rules in `soul.rules.yaml`.
-   **Output:** It generates a raw, machine-readable JSON report of every potential violation, including contextual false positives.

## Stage 2: The Oracle (LLM-Powered Judgment)

The master script then uses the Linter's raw report to consult an LLM-powered Oracle.

-   **Role:** The script packages the Linter's JSON report along with the full text of all flagged files. It sends this data to a Large Language Model with a carefully designed system prompt. The prompt instructs the Oracle to act as a wise co-architect, filtering out violations that are either intentional critiques or acceptable common-language uses.
-   **Output:** The Oracle returns a final, validated JSON report containing only the *true* violations that require remediation, along with a human-readable list of reasons for why other items were filtered.

## The Final Report

The master script presents a final, clean report to the human Architects. This report shows only the true, actionable violations, if any, allowing us to focus our creative energy exclusively on resolving genuine inconsistencies. This closed-loop system of Law and Oracle ensures the long-term integrity of the Codex with maximum efficiency.