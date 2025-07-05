# Tool Specification: The Context Forge (`forge-context.sh`)

**Location:** `foundry/apps/cli-tools/forge-context/`
**Version:** 4.0
**Status:** Specified

## 1. Overview

The Context Forge is a command-line utility that architects and generates a context snapshot from The Enclave Foundation's ecosystem. It intelligently orders information and prepends a system prompt to create a high-fidelity input for LLM interaction.

## 2. Core Features

-   **System Prompt Injection:** Allows a user-defined prompt to be placed at the top of the context file.
-   **Hierarchical Ordering:** Scrapes repositories in a fixed, logical order (`foundation` -> `codex` -> `specs` -> `foundry`) to optimize LLM comprehension.
-   **Targeted Scoping & Filtering:** Uses flags to select repositories and a `.contextignore` file to exclude noise.
-   **Fixed-Root Execution & CLI Alias:** Provides a simple and reliable user experience.

## 3. Command-Line Interface (CLI)

```bash
USAGE: context [FLAGS] "[SYSTEM_PROMPT]"

FLAGS:
  --all              Scrape foundation, codex, specs, and foundry.
  --foundation       Include the 'foundation' repository.
  --codex            Include the 'codex' repository.
  --specs            Include the 'specs' repository.
  --foundry          Include the 'foundry' repository.

  --output <file>    Specify the output file path. (Default: ./context_snapshot.txt)
  --help             Display this help message.

ARGUMENTS:
  [SYSTEM_PROMPT]    (Optional) A string to be used as the system prompt at the top of the file.