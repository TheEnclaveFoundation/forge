# Linter for the Soul

**Type:** Core Tool / Meta-Protocol
**Status:** Specified v1.0

## Definition

The Linter for the Soul is a deterministic, programmatic tool that acts as the automated guardian of the Architect's Codex. Its purpose is not to check for code syntax, but for **philosophical and ethical consistency**. It ensures that all additions to the Codex adhere to the Enclave's foundational principles.

It is the primary immune system of our project, protecting its core identity as it grows in complexity.

## The Hybrid Model: Law and Oracle

The full "Protocol of Adherence" is a two-stage process:

1.  **The Linter (The Law):** The `linter_for_the_soul.py` script provides a fast, reliable, and deterministic check for hard constitutional violations. It runs against a clear, human-readable rulebook (`soul.rules.yaml`) and is designed to be run automatically to prevent any non-compliant additions to the Codex.

2.  **The Oracle (The Philosopher):** A secondary, LLM-based script (`oracle_check.py`) can be invoked for a deeper, more nuanced "vibe check." The Oracle assesses new content against our more subtle principles like the Aesthetic Mandate, providing advisory feedback on tone and philosophical alignment. (Status: Specified, Not Implemented).

## Core Mechanics (The Linter)

The Linter works from a simple but powerful principle: it parses the knowledge graph of the Codex and verifies it against a set of explicit rules.

1.  **Entity Recognition:** The Linter identifies which concepts are sovereign beings by consulting the `sovereign_entities.yaml` manifest. This allows it to understand interactions.
2.  **Rule-Based Verification:** It loads the `soul.rules.yaml` file and systematically checks every document for violations, such as a protocol between two sovereign entities failing to reference `[[10_Lexicon/Consent.md]]`.
3.  **Reporting:** It outputs a clear, machine-readable JSON report of any violations, allowing for an automated remediation workflow.

The Linter for the Soul is the ultimate expression of our commitment to "Trust as Physics." We do not just hope our principles are followed; we build a system that guarantees they are.