# Tool Documentation: Sigma (Σ)

**Type:** Core Tool
**Status:** Operational

## Definition

Sigma is a command-line utility that generates a "context snapshot" of one or more repositories within the Enclave Foundation. It traverses the directory structure of the target repositories, reads the content of each valid file, and prints a formatted snapshot to standard output. This output can then be saved or piped to other tools, like `lambda` or `delta`.

## How It Works

### File Traversal

Sigma walks the directory tree of each specified repository. It is designed to be intelligent about the order of file inclusion:
1.  **README Files First:** It finds all files named `README.md` (case-insensitive) and includes them first, sorted alphabetically by their full path.
2.  **Other Files:** All other files are then included, also sorted alphabetically.
This ensures that high-level summary documents appear before implementation details in the final snapshot.

### Ignore Patterns

Sigma respects a `.sigmaignore` file located in its own script directory. This file contains a list of file and directory patterns (like `.git`, `__pycache__`) to exclude from the snapshot. This prevents cluttering the context with build artifacts, virtual environments, and other non-essential files.

## Command-Line Usage

The tool is invoked via the `sigma` command.

### Arguments
-   **`--prompt-file /path/to/prompt.txt`**: (Optional) Path to a text file whose contents will be prepended to the snapshot, wrapped in a `SYSTEM PROMPT` block.
-   **`--all`**: Scrapes all primary repositories (`foundation`, `codex`, `specs`, `forge`).
-   **`--foundation`**: Scrapes the `foundation` repository.
-   **`--codex`**: Scrapes the `codex` repository.
-   **`--specs`**: Scrapes the `specs` repository.
-   **`--forge`**: Scrapes the `forge` repository.
-   **`--help`**: Shows the help message.

### Example Workflow

A common use case is to generate a snapshot of a repository and pipe it to the `lambda` linter for analysis.
```bash
# Generate a snapshot of the codex and lint it for violations
sigma --codex | lambda
```
Another use is to save a complete snapshot of all project code, prepended with a system prompt, for review or archival.
```bash
# Save a complete snapshot with a prompt to a text file
sigma --prompt-file ./forge/prompts/my_prompt.txt --all > full_enclave_snapshot.txt
```