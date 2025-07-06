# Sigma (Σ) - Context Snapshot Tool

The `sigma` tool generates a context snapshot by traversing specified repository directories, respecting ignore patterns, and printing the contents of all found files to standard output.

## Basic Usage

To scrape all repositories and save the output to a file:
```bash
sigma --all > snapshot.txt
```
To prepend a system prompt from a file and scrape a specific repository (e.g., `codex`):
```bash
sigma --prompt-file ./path/to/my_prompt.txt --codex > codex_snapshot_with_prompt.txt
```
The tool respects a `.sigmaignore` file located in its directory to exclude certain files and folders from the snapshot.
For more detailed information, see the full **[Sigma Documentation](../../../docs/Sigma.md)**.