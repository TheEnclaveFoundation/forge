# Iota (Ι/ι) - The Link Harmonizer

`iota` is a CLI tool that acts as the guardian of our knowledge graph's integrity. It is designed to be run as part of our development workflow to automatically enforce linking standards across all repositories.

It works by:
1.  Building an index of all linkable concepts from filenames.
2.  Scanning documents to find the first mention of a concept and ensuring it is correctly linked.
3.  Stylizing all subsequent mentions of that concept as subtle, backticked text.
4.  Generating a `REPLACE_FILE` Delta Manifest for any file that required changes.

Its output is designed to be piped directly into the `delta` tool for safe, reviewable application of changes.

## Features

-   **Automated Link Consistency**: Enforces the "one concept, one primary link" standard across thousands of files automatically.
-   **Multi-Format Support**: Uses a provider-based architecture to support different knowledge graph linking syntaxes (e.g., Obsidian, Standard Markdown). See the full **[Knowledge Graph Formats Specification](../../../docs/Knowledge-Graph-Formats.md)** for more details.
-   **Safe, Reviewable Changes**: Outputs a `delta` manifest to `stdout`, ensuring all proposed changes can be reviewed before application.

## Command-Line Usage

### Basic Invocation
```bash
# Check the mycelium repo for linking errors using the default obsidian format
iota --mycelium --check

# Generate a manifest to fix the specs repo and apply it with delta
iota --specs | delta -y
```
### Flags
-   `--mycelium`, `--specs`, etc.: Specifies the repository to scan.
-   `--all`: Scans all primary repositories.
-   `--check`: Runs a dry run, reporting files that need changes without generating a manifest.
-   `--format [obsidian|...]`: (Default: `obsidian`) Specifies which knowledge graph link format provider to use.
