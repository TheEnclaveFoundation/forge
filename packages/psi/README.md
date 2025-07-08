# Psi (Ψ) - The Oracle

The `psi` package is a standardized, secure, and flexible interface for interacting with various high-capability Large Language Models (LLMs). It serves as the "Oracle" layer for our more advanced AI-driven tools, abstracting away the complexity of handling different API providers and secrets.

## Features

-   **Provider-Based Architecture**: Easily extensible to support new models from different providers (e.g., Google, OpenAI, local models).
-   **Secure Secret Management**: Loads API keys and endpoints from a `.env` file at the project root.
-   **Response Caching**: Automatically caches successful LLM responses to improve performance and reduce cost.
-   **Automatic Retries**: Automatically retries failed API calls with exponential backoff to handle transient network errors.
-   **Standardized Error Schema**: Returns detailed, consistent JSON objects for any errors.
-   **Structured Output Validation**: Can validate LLM responses against a Pydantic model and re-prompt the LLM on failure.

## Command-Line Usage

While `psi` is primarily a library, it can be invoked from the command line for testing and direct queries.

### Basic Invocation
```bash
echo "Content to analyze" | psi --model gemini-1.5-pro --prompt-file ./path/to/prompt.txt
```
### Flags
-   `--prompt-file`: (Required) Path to the system prompt file.
-   `--model`: (Required) The specific model to use (e.g., `gemini-1.5-pro`).
-   `--validate-with`: (Optional) The name of a Pydantic model (e.g., `SimpleResponse`) to validate the output against.
-   `--no-cache`: (Optional) Bypasses the cache and forces a live API call.
-   `--verbose`: (Optional) Outputs the full raw JSON response object to `stdout`.
-   `--response`: (Optional) Outputs only the LLM's text response to `stdout` (if piped) or as a UI report (if interactive).
-   `--metadata`: (Optional) Prints a formatted metadata report of the transaction to the screen.

## Configuration

`psi` requires a `.env` file in the `foundation` repository root for its API keys and endpoints.

**Example `.env` file:**
```
# .env
GOOGLE_API_KEY="your_google_api_key_here"
LOCAL_MODEL_ENDPOINT="http://localhost:11434/v1/chat/completions"
```