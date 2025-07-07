# Tool Specification: Psi (Ψ) v2

**Type:** Core Tool / System Specification
**Status:** Scoped v2.0

## 1. Definition

The `psi` package is the standardized, secure, and flexible interface for interacting with various high-capability Large Language Models (LLMs). It serves as the "Oracle" layer for advanced AI-driven tools within the `forge` toolchain. Version 2 introduces significant enhancements in resource management, reliability, and data integrity.

---
## 2. v2 Architecture & Features

### 2.1. Resource Management Engine

This engine provides mechanisms for tracking and conserving computational resources (`The Deepglow`).

-   **Cost & Token Tracking**:
    -   For each API call, `psi` will count the input and output tokens.
    -   This data, along with the model used, will be logged to a structured log file for budget analysis.
    -   The `providers.yaml` file may be extended to include cost-per-token information to allow for direct cost estimation in the logs.

-   **Request Caching**:
    -   **Mechanism**: Before making an API call, `psi` will generate an SHA-256 hash from the combined `(content + system_prompt + model_name)`.
    -   **Storage**: This hash will be used as a key in a local file-based cache (e.g., in a `.cache/psi/` directory).
    -   **Behavior**: If a valid, non-expired cache entry exists for the key, the cached response is returned immediately, bypassing the API call. The cache entry will include a timestamp to allow for a configurable Time-to-Live (TTL).

---
### 2.2. Reliability Layer

This layer ensures the tool is robust and resilient, especially in automated workflows.

-   **Automatic Retries**:
    -   **Strategy**: For transient HTTP errors (e.g., 5xx server errors, network timeouts), providers will automatically retry the request up to 3 times.
    -   **Backoff**: The delay between retries will follow an exponential backoff strategy (e.g., 1s, 2s, 4s) to avoid overwhelming the remote API.

-   **Standardized Error Schema**:
    -   All errors returned by any provider will conform to a single, unified JSON schema.
    -   **Example Error Schema**:
```json
        {
          "error": true,
          "error_type": "API_AUTH_ERROR",
          "message": "Authentication failed. Please check your API key.",
          "provider": "google",
          "details": "The API key is invalid or has expired."
        }
```
---
### 2.3. Structured Output Validation

This is a key feature for ensuring predictable, high-quality output from the LLM Oracle.

-   **Workflow**:
    1.  A calling tool (e.g., `Weaver`) can optionally pass a Pydantic model class to the `psi.get_response()` function.
    2.  `psi` makes the initial API call to the LLM.
    3.  `psi` attempts to parse the LLM's text response into an instance of the provided Pydantic model.

-   **Validation & Re-Prompting**:
    -   **On Success**: If parsing is successful, the validated Pydantic object is returned.
    -   **On Failure**: If parsing fails due to a `ValidationError`, `psi` will automatically trigger a single re-prompt. It will construct a new prompt containing the original request, the desired schema, and the specific validation error from Pydantic, asking the LLM to correct its previous output.
    -   **Final Attempt**: The response from the re-prompt is then validated. If it still fails, the validation error is returned to the user. This prevents infinite loops.