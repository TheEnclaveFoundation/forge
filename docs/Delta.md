# Tool Documentation: Delta (∆)

**Type:** Core Protocol / System
**Status:** Operational v3.0

## 1. Definition

**Delta (∆)** is a command-line utility that serves as the core mechanism for applying structured changes to the file system. It parses a structured text block called a **Delta Manifest** from standard input to perform precise, automated, and batch-capable modifications. Its purpose is to eliminate the tedious and error-prone process of manual file updates.

## 2. Usage

`delta` is designed to be used in a pipeline, reading a manifest from standard input.

### Command-Line Flags
-   `--dry-run`: Validate the manifest and show a diff of all proposed changes without applying them.
-   `--transaction`: Apply all approved changes as a single, atomic transaction. If any operation fails, the entire batch is rolled back.
-   `-y`, `--yes`: Automatically approve and apply all operations without an interactive prompt. Ideal for scripts.
-   `--strict`: Causes parser warnings to be treated as fatal errors.

### Example Invocations
```bash
# Interactively review a manifest from a file
cat my_changes.manifest | delta

# Silently apply a manifest from the clipboard in a transaction
ci | delta -y --transaction
```
---
## 3. The Delta Manifest Protocol

A Delta Manifest is a block of text containing one or more "Deltas." Each Delta is a self-contained instruction set for a single file operation.

### 3.1. Structure of a Delta

Each Delta must adhere to the following structure:

1.  **Start Marker:** Every Delta must begin with the line `=== DELTA::START ===`.
2.  **Header(s):** Defines the operation's core parameters (e.g., `PATH`, `ACTION`, `SOURCE_PATH`).
3.  **Content Section:** If required, provides the data for the action, starting with a `=== DELTA::CONTENT ===` marker.

### 3.2. Action Reference

#### File Content Actions
-   **`CREATE_FILE`**: Creates a new file with the provided `CONTENT`.
-   **`REPLACE_FILE`**: Overwrites an existing file with the provided `CONTENT`.
-   **`APPEND_TO_FILE`**: Adds `CONTENT` to the end of an existing file.
-   **`PREPEND_TO_FILE`**: Adds `CONTENT` to the beginning of an existing file.
-   **`DELETE_FILE`**: Deletes a file.

#### Directory Actions
-   **`CREATE_DIRECTORY`**: Creates a new directory.
-   **`DELETE_DIRECTORY`**: Deletes a directory and its contents recursively.

#### Path Actions
-   **`MOVE_FILE`**: Moves or renames a file. Requires `SOURCE_PATH` and `DESTINATION_PATH` headers.

---
## 4. Special Syntax

### 4.1. Embedding Code Blocks (`@@@`)
To embed a standard Markdown code block within the `CONTENT` section, use `@@@` instead of ` ``` `. The `delta` script will automatically convert it back to triple backticks before writing the file.

### 4.2. Embedding Example Manifests (`#! DELTA_EXAMPLE`)
To include a literal example of a Delta Manifest within a document (like this one), wrap the example block with `#! DELTA_EXAMPLE::START` and `#! DELTA_EXAMPLE::END` on their own lines. This prevents `delta` from trying to parse the example.
