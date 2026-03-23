"""Server info for prima.cpp/llama.cpp."""

from cli_anything.ollama.utils.ollama_backend import api_get


def server_status(base_url: str) -> dict:
    """Check if server is running via /health endpoint."""
    try:
        result = api_get(base_url, "/health")
        return {"status": "ok", "server": "prima.cpp/llama.cpp"}
    except Exception:
        return {"status": "error", "message": "Server not reachable"}


def version(base_url: str) -> dict:
    """Get server info via /v1/models."""
    try:
        result = api_get(base_url, "/v1/models")
        return {"server": "prima.cpp/llama.cpp", "models": result}
    except Exception:
        return {"server": "unknown"}
