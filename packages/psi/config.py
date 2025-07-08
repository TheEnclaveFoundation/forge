import os

# The root directory for The Enclave Foundation projects.
# Can be overridden by the ENCLAVE_FOUNDATION_ROOT environment variable.
FOUNDATION_ROOT = os.environ.get(
    "ENCLAVE_FOUNDATION_ROOT",
    os.path.expanduser("~/softrecursion/TheEnclaveFoundation")
)
