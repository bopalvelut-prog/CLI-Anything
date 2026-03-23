"""OpenAI-compatible model listing for prima.cpp/llama.cpp."""

from cli_anything.ollama.utils.ollama_backend import api_get


def list_models(base_url: str) -> dict:
    """List available models on the server.

    Returns:
        Dict with 'models' key containing list of model info dicts.
    """
    try:
        result = api_get(base_url, "/v1/models")
        # Convert OpenAI format to Ollama-compatible format
        openai_models = result.get("data", [])
        models = []
        for m in openai_models:
            models.append(
                {
                    "name": m.get("id", ""),
                    "size": 0,
                    "modified_at": m.get("created", ""),
                }
            )
        return {"models": models}
    except Exception:
        return {"models": []}


def show_model(base_url: str, name: str) -> dict:
    """Show model details (stub — limited on OpenAI-compatible API)."""
    return {"name": name, "details": "Model info available via /v1/models endpoint"}


def pull_model(base_url: str, name: str, stream: bool = True):
    """Load a model (stub — model loading is server-side for llama.cpp)."""
    if stream:
        yield {"status": f"Model '{name}' is served by prima.cpp/llama.cpp server"}
    else:
        return {"status": f"Model '{name}' is served by prima.cpp/llama.cpp server"}


def delete_model(base_url: str, name: str) -> dict:
    """Delete model (not supported on OpenAI-compatible API)."""
    return {
        "status": "not_supported",
        "message": "Model deletion not available via OpenAI-compatible API",
    }


def copy_model(base_url: str, source: str, destination: str) -> dict:
    """Copy model (not supported on OpenAI-compatible API)."""
    return {
        "status": "not_supported",
        "message": "Model copying not available via OpenAI-compatible API",
    }


def running_models(base_url: str) -> dict:
    """List loaded models."""
    try:
        result = api_get(base_url, "/v1/models")
        openai_models = result.get("data", [])
        models = []
        for m in openai_models:
            models.append(
                {
                    "name": m.get("id", ""),
                    "size": 0,
                }
            )
        return {"models": models}
    except Exception:
        return {"models": []}
