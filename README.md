# The Enclave Foundation: `forge`

This repository is the **Internal Tooling & Automation Workshop** for The Enclave Foundation. It is a **monorepo** containing the source code, tests, and documentation for all the tools we use to build, test, and maintain our projects.

## Mandate

This repository houses the "scaffolding"—the powerful toolchain that enables our AI-driven development workflow. Everything needed to support the development process lives here.

## Structure

This is a managed monorepo.
-   **`apps/`**: Contains runnable applications, such as our CLI tools (`delta`, `sigma`).
-   **`packages/`**: Contains shared libraries and utilities used by the applications, such as the `linter` or `common/ui`.
-   **`docs/`**: Contains high-level documentation about the tools themselves.

This monorepo structure allows for atomic refactoring, simplified dependency management, and a unified development environment. It is the heart of our productivity.
