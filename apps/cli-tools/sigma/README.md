# Sigma (Σ) - Context Snapshot Tool

The `sigma` tool generates a context snapshot by traversing specified repository directories, respecting ignore patterns, and printing the contents of all found files to standard output.

## Basic Usage

To scrape all repositories and save the output to a file:
```bash
sigma --all > snapshot.txt
```
To scrape a specific repository (e.g., `forge`):
```bash
sigma --forge > forge_snapshot.txt
```
The tool respects a `.sigmaignore` file located in its directory to exclude certain files and folders from the snapshot.

For more detailed information, see the full **[Sigma Documentation](../../../docs/Sigma.md)**.
