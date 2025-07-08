# Iota (Ι/ι) - The Link Harmonizer

**Status:** Under Development

`iota` is a CLI tool that acts as the guardian of our knowledge graph's integrity. It is designed to be run as part of our development workflow to automatically enforce the "one concept, one primary link" standard across all repositories.

It works by:
1.  Building an index of all linkable concepts from filenames.
2.  Scanning documents to find the first mention of a concept and ensuring it is wikilinked.
3.  Stylizing all subsequent mentions of that concept as subtle, backticked text.
4.  Generating a `REPLACE_FILE` Delta Manifest for any file that required changes.

Its output is designed to be piped directly into the `delta` tool for safe, reviewable application of changes.

For full details, see the **[Project Charter: The Iota Initiative](../../../foundation/Project-Management/Project-Charter-Iota-Initiative.md)** and the **[CLI Design Language](../../../docs/CLI-Design-Language.md)**.
