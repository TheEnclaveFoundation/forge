# Psi (Ψ) - The Oracle

The `psi` package is designed to interact with a high-capability LLM to provide nuanced, qualitative judgment on linter reports or other analysis tasks. It serves as the "Oracle" or "Philosopher" stage of the **[Integrated Adherence Protocol](../../../docs/Integrated-Adherence-Protocol.md)**.

**Status:** Operational (v1.0 - Mocked API)

## Basic Usage

`psi` is designed to be used as a library or within a shell pipe. To get a judgment on a piece of text:
```bash
cat some_text.txt | python3 -m forge.packages.psi.main --prompt-file ./path/to/prompt.txt
```