# CLI Design Language

**Type:** Foundational Protocol
**Status:** Ratified v1.0
**Date:** 2025-07-05

## 1. Core Philosophy: An LLM-Native Toolchain

The `forge` toolchain is designed to be **LLM-native**. This means every tool, library, and function is architected to be easily understood, generated, maintained, and reasoned about by both human and AI developers. Our primary goal is to automate mechanical toil, freeing the human Architect to focus on high-level creative, strategic, and ethical work. This philosophy is the "why" that informs all principles below.

## 2. Foundational Architectural Principles

These are the bedrock principles that govern the architecture of all `forge` tools.

### 2.1. Extreme Modularity (Atomic Work Orders)

Every problem must be broken down into the smallest possible, independent, and single-purpose units.
-   **Tools:** Each CLI tool must have a single, clear responsibility (e.g., `sigma` scrapes, `iota` harmonizes links, `delta` applies changes).
-   **Functions:** Within a tool, each function should do only one thing well.
-   **Rationale:** This approach creates "atomic work orders" that are perfect for AI-driven development. The scope is constrained, inputs and outputs are clear, and the results are independently verifiable, simplifying development, testing, and debugging.

### 2.2. The Functional Paradigm (Eliminating Side Effects)

We will prioritize a functional programming style to ensure predictability and reliability.
-   **Pure Functions:** Where possible, functions should be "pure"—their output must depend only on their input arguments, with no reliance on or modification of external state (side effects).
-   **Immutability:** Data structures should be treated as immutable. A function that needs to modify data should return a new, changed copy rather than altering the original in place.
-   **Rationale:** Eliminating side effects drastically reduces cognitive load and makes our codebase safer. A pure function can be understood, generated, and tested in complete isolation, which is essential for a robust, AI-assisted workflow.

## 3. The UNIX Pipe Model (`stdin -> stdout | stderr`)

All CLI tools must adhere to the UNIX philosophy of composability, enabling them to be chained together.
-   **`stdin`:** The primary channel for receiving data, either from a file redirection or another tool's output.
-   **`stdout`:** The primary channel for outputting "clean" data intended for consumption by another program or for redirection to a file (e.g., a context snapshot, a Delta Manifest, a JSON report). **No UI elements should ever be printed to `stdout`**.
-   **`stderr`:** The dedicated channel for all human-facing output. This includes banners, progress indicators, final summary reports, and error messages. The `eprint()` function from our common UI package must be used for this purpose.

## 4. Terminal UI/UX (The "Look and Feel")

All tools must share a cohesive visual identity to provide a seamless Architect experience.

### 4.1. Layout & Box-Drawing Characters
Tools must use our established T-junction/box-style layout, utilizing the following characters for structure: `┌`, `├`, `└`, `│`, and the `─┄` ruler.

### 4.2. The Standard Color Palette
Colors must be used consistently and sourced exclusively from the `forge/packages/common/ui.py` module. Their semantic meaning is standardized:
-   **`GREEN`**: Success, safe operations, additions.
-   **`RED`**: Errors, warnings, deletions.
-   **`YELLOW`**: Advisory notes, skipped items.
-   **`PURPLE`**: File paths, counts, and key nouns.
-   **`CYAN`**: Actions, names, and key verbs.
-   **`GREY`**: UI chrome, separators, and non-essential text.

### 4.3. Standard Report Structure
Every tool's execution must follow this sequence:
1.  **Startup Banner:** A single, minimal banner on launch.
2.  **Body of Work:** Informational updates on the tool's progress.
3.  **Summary Report:** A final, clear summary of the actions taken.

## 5. Implementation Conventions

### 5.1. Argument Parsing
The standard `argparse` library in Python shall be used for parsing all command-line arguments and flags.

### 5.2. Shared UI Module
All UI elements (colors, `eprint`, etc.) **must** be imported from the `forge/packages/common/ui.py` package. This ensures any future change to our UI language can be made in one place.

### 5.3. Configuration
Standard configuration, such as the `ENCLAVE_FOUNDATION_ROOT`, should be managed via environment variables with sensible defaults.