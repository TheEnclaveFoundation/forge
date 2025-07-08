# Delta

**Type:** Core Protocol / System
**Status:** Operational v2.7 (with Robust Code Block and Example Handling)

## Definition

Delta is a Python script that serves as the core mechanism for applying structured changes to the file system. It parses a structured text block called a **Delta Manifest** to perform precise, automated, and batch-capable modifications. Its purpose is to eliminate the tedious and error-prone process of manual file updates, making our collaborative workflow more robust, scalable, and efficient.

## The Delta Manifest Protocol (v2.7)

A Delta Manifest is a block of text containing one or more "Deltas." Each Delta is a self-contained instruction set for a single file operation, parsed by the `delta` script.

### Structure of a Delta

Each Delta must adhere to the following structure:

1.  **Start Marker:** Every Delta must begin with the line `=== DELTA::START ===`.
2.  **Header:** Defines the operation's core parameters, such as `PATH`, `ACTION`, `SOURCE_PATH`, etc.
3.  **Content Section:** If required by the action, provides the data for the operation, beginning with a `=== DELTA::CONTENT ===` marker.

---

### Action Reference

#### File Content Actions

* **`CREATE_FILE`**: Creates a new file.
    * Requires: `CONTENT` section.
* **`REPLACE_FILE`**: Overwrites an existing file.
    * Requires: `CONTENT` section.
* **`APPEND_TO_FILE`**: Adds content to the end of a file.
    * Requires: `CONTENT` section.
* **`PREPEND_TO_FILE`**: Adds content to the beginning of a file.
    * Requires: `CONTENT` section.
* **`DELETE_FILE`**: Deletes a file.
    * Requires: No content sections.

#### Directory Actions

* **`CREATE_DIRECTORY`**: Creates a new directory.
    * Requires: No content sections. The `PATH` specifies the directory to create.
* **`DELETE_DIRECTORY`**: Deletes a directory and its contents.
    * Requires: No content sections. The `PATH` specifies the directory to delete.

#### Path Actions

* **`MOVE_FILE`**: Moves or renames a file. This action is distinct in that it requires `SOURCE_PATH` and `DESTINATION_PATH` headers instead of the standard `PATH`.
    * Requires: `SOURCE_PATH`, `DESTINATION_PATH`. No content sections.
---

### Embedding Code Blocks within Delta Manifests (Special Syntax: `@@@`)

To prevent parsing conflicts when embedding standard Markdown code blocks (delimited by triple backticks ` ``` `) within the `CONTENT` section of a Delta Manifest, we use a special substitution:

* **Use `@@@` instead of ` ``` ` (three backticks).**
* The `delta` script will automatically convert `@@@` back to ` ``` ` just before writing the content to the file.

### Embedding Example Delta Manifests (Special Syntax: `#! DELTA_EXAMPLE`)

When you need to include a *full, syntactically correct example of a Delta Manifest* within the content of a document, you must enclose it within special literal markers. This prevents `delta` from attempting to parse and execute the *example* as a live Delta operation itself.

* Wrap the entire example Delta Manifest with `#! DELTA_EXAMPLE::START` and `#! DELTA_EXAMPLE::END` on their own lines.
* `delta` will strip these markers and include all content between them *literally* in the target file.
