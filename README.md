# The Enclave Foundation: `forge`

This repository is the **Internal Tooling & Automation Workshop** for The Enclave Foundation.
It is a **monorepo** containing the source code, tests, and documentation for all the tools we use to build, test, and maintain our projects.

## Mandate

This repository houses the "scaffolding"—the powerful toolchain that enables our AI-driven development workflow. Everything needed to support the development process lives here.

## Documentation

This project uses a hybrid documentation strategy:
-   **Quick Start `README.md` files**: Each application (in `apps/`) and package (in `packages/`) has its own `README.md` file with a brief summary and basic usage instructions.
-   **Central `/docs` Directory**: The `docs/` directory contains detailed, high-level, and conceptual documentation, including tool specifications and core protocols.

This approach provides immediate, context-specific help while maintaining a centralized source of truth for deep documentation.

## Structure

This is a managed monorepo.
-   **`apps/`**: Contains runnable applications, such as our CLI tools (`delta`, `sigma`).
-   **`packages/`**: Contains shared libraries and utilities used by the applications, such as the `linter` or `common/ui`.
-   **`docs/`**: Contains high-level documentation about the tools themselves.

This monorepo structure allows for atomic refactoring, simplified dependency management, and a unified development environment. It is the heart of our productivity.
