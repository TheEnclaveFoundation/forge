# Specification: Knowledge Graph Formats

**Type:** Core Protocol / System Specification
**Status:** Scoped v1.0

## 1. Definition

This document specifies the different plain-text knowledge graph formats that the `forge` toolchain, particularly the `iota` tool, must be aware of and eventually support. It also defines the architectural approach for implementing this support in a modular and extensible way.

## 2. The `--format` Flag Architecture

To ensure `iota` can adapt to different linking conventions, it will implement a `--format=<format_name>` command-line argument. The core logic of `iota` will remain agnostic to the specific link syntax. It will delegate all parsing and formatting tasks to a dedicated "format provider" module based on the flag.

**Example Invocation:**
```bash
# Use the Obsidian wikilink provider
iota --mycelium --format=obsidian

# Use the standard Markdown link provider
iota --mycelium --format=markdown
```
This architecture ensures that adding support for a new format in the future only requires adding a new provider module, not refactoring the entire tool.

## 3. Supported Formats

The following formats are recognized as part of the `forge`'s long-term roadmap.

### 3.1. Obsidian (Default)
-   **Syntax**: `[[My Note]]` or `[[My Note|display text]]`
-   **Description**: A simple and widely used format that links directly to filenames. It is the default format for the Enclave project.
-   **Status**: Currently implemented (to be refactored into its own provider).

### 3.2. Standard Markdown
-   **Syntax**: `[My Note](./path/to/my-note.md)`
-   **Description**: The most universal and portable format, compatible with any standard Markdown viewer (e.g., GitHub). This is a high-priority format for interoperability.
-   **Status**: To be implemented.

### 3.3. Zettelkasten ID
-   **Syntax**: `[[20250708111541]]`
-   **Description**: Links to a unique, immutable ID (typically a timestamp) rather than a filename. This ensures links never break, even if files are renamed. It is a core pattern for long-term knowledge durability.
-   **Status**: To be implemented.

### 3.4. Roam/Logseq Block References
-   **Syntax**: `((block-uuid-1234))`
-   **Description**: Links directly to a specific paragraph or "block" within a file, rather than the file itself. This enables a highly granular and networked approach to knowledge management.
-   **Status**: To be implemented.
