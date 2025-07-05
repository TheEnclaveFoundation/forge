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
2.  **Header:** Defines the operation's core parameters:
    -   `PATH: ./path/to/target/file_or_directory`
    -   `ACTION: [ACTION_TYPE]`

3.  **Content Sections:** Provides the data for the action (e.g., `CONTENT`, `TARGET_BLOCK`). Each section begins with a `=== DELTA::[SECTION_NAME] ===` marker.

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

#### Block-Based Actions

These actions operate on a `TARGET_BLOCK` within a file.
* **`REPLACE_BLOCK`**: Replaces the `TARGET_BLOCK` with `REPLACEMENT_CONTENT`.
    * Requires: `TARGET_BLOCK`, `REPLACEMENT_CONTENT`.
* **`INSERT_AFTER_BLOCK`**: Inserts `REPLACEMENT_CONTENT` immediately after the `TARGET_BLOCK`.
    * Requires: `TARGET_BLOCK`, `REPLACEMENT_CONTENT`.
* **`INSERT_BEFORE_BLOCK`**: Inserts `REPLACEMENT_CONTENT` immediately before the `TARGET_BLOCK`.
    * Requires: `TARGET_BLOCK`, `REPLACEMENT_CONTENT`.

#### Directory Actions

* **`CREATE_DIRECTORY`**: Creates a new directory.
    * Requires: No content sections. The `PATH` specifies the directory to create.

---

### Embedding Code Blocks within Delta Manifests (Special Syntax: `@@@`)

To prevent parsing conflicts when embedding standard Markdown code blocks (delimited by triple backticks ```` `) within the `CONTENT`, `TARGET_BLOCK`, or `REPLACEMENT_CONTENT` sections of a Delta Manifest, we use a special substitution:

* **Use `@@@` instead of ```` (three backticks).**
* The `delta` script will automatically convert `@@@` back to ```` just before writing the content to the file.

**Examples of `@@@` Usage:**

-   To start a generic code block: `@@@`
-   To start a language-specific code block: `@@@python`, `@@@mermaid`, `@@@bash`
-   To end a code block: `@@@` (on its own line)

### Embedding Example Delta Manifests (Special Syntax: `#! DELTA_EXAMPLE`)

When you need to include a *full, syntactically correct example of a Delta Manifest* within the content of a document (e.g., in this `Delta.md` file), you must enclose it within special literal markers. This prevents `delta` from attempting to parse and execute the *example* as a live Delta operation itself.

* Wrap the entire example Delta Manifest with `#! DELTA_EXAMPLE::START` and `#! DELTA_EXAMPLE::END` on their own lines.
* `delta` will strip these markers and include all content between them *literally* in the target file.
* Any `@@@` markers *within* the example will still be converted to backticks by `delta`.

**Example Delta Manifest:**

The following is a valid example of a Delta Manifest demonstrating the internal `@@@` code block syntax.
=== DELTA::START ===
PATH: ./new-document.md
ACTION: CREATE_FILE
=== DELTA::CONTENT ===
# My New Document

This is some regular markdown text.

Here's an example Python code block:

@@@ python
def hello_enclave():
    print("Hello, Enclave!")
@@@

And another generic code block:

@@@
Some raw text that might look like code.
This is line 2.
@@@


This is the end of the document.

This comprehensive protocol ensures that Delta Manifests can be reliably transmitted, parsed, and executed, even when containing complex embedded code or example manifests themselves.
