# Delta (∆) - Filesystem Patching Tool

The `delta` script is the core mechanism for applying structured, automated changes to the file system. It works by parsing a **Delta Manifest** from standard input.

## Basic Usage

To apply changes from a manifest file:
```bash
cat my_changes.manifest | delta
```
To perform a "dry run" that shows a diff of the proposed changes without applying them:
```bash
cat my_changes.manifest | delta --dry-run
```
The full specification for writing manifests, including all available actions and special syntax, is available in the main documentation.

For a detailed explanation of the protocol, see the full **[Delta Manifest Protocol Documentation](../../../docs/Delta.md)**.
