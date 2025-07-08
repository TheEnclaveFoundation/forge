# Tool Documentation: Sigma (Σ)

**Type:** Core Tool
**Status:** Operational

## 1. Definition

**Sigma (Σ)** is a command-line utility that generates a "context snapshot" of one or more repositories within the Enclave Foundation. It traverses the directory structure, reads the content of each valid file, and prints a formatted snapshot to standard output. This output can then be saved or piped to other tools like `lambda`.

## 2. How It Works

### File Traversal
Sigma intelligently orders the files in its snapshot:
1.  **README Files First:** It finds all files named `README.md` (case-insensitive) and includes them first, sorted alphabetically by their full path.
2.  **Other Files:** All other files are then included, also sorted alphabetically.

This ensures that high-level summary documents appear before implementation details.

### Ignore Logic
Sigma uses a two-tiered system for ignoring files and directories:
1.  **Global Ignore (`.sigmaignore`):** It respects a `.sigmaignore` file located in its own script directory. This file contains global patterns (like `.git`, `__pycache__`) to exclude from all snapshots.
2.  **Local Ignore (`.gitignore`):** It also finds and respects any `.gitignore` files within the repositories it scans. This allows for project-specific ignore rules and is handled by the `pathspec` library for full compatibility.

### Binary File Handling
The tool automatically detects binary files (e.g., images, archives) by checking for null bytes. To prevent errors and garbage output, the content of these files is not included in the snapshot. Instead, a placeholder message, `[Binary file content suppressed]`, is used.

## 3. Command-Line Usage

### Arguments
-   `--prompt-file /path/to/prompt.txt`: (Optional) Path to a text file whose contents will be prepended to the text-format snapshot, wrapped in a `SYSTEM PROMPT` block.
-   `--all`: Scrapes all primary repositories (`foundation`, `mycelium`, `specs`, `forge`).
-   `--foundation`, `--mycelium`, `--specs`, `--forge`: Scrapes the specified repository.
-   `--output-format [text|json]`: Specifies the output format. Defaults to `text`. `json` output is a single object mapping relative file paths to their content.
-   `--help`: Shows the help message.

### Example Workflow
```bash
# Generate a snapshot of the codex and lint it for violations
sigma --mycelium | lambda

# Save a complete snapshot of all project code in JSON format
sigma --all --output-format json > full_enclave_snapshot.json
```