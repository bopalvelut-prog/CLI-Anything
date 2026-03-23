"""OpenAI-compatible embeddings for prima.cpp/llama.cpp."""

from cli_anything.ollama.utils.ollama_backend import api_post


def embed(base_url: str, model: str, input_text: str | list[str]) -> dict:
    """Generate embeddings via /v1/embeddings."""
    data = {"model": model, "input": input_text}
    try:
        result = api_post(base_url, "/v1/embeddings", data, timeout=60)
        # Convert OpenAI format to Ollama-compatible format
        openai_data = result.get("data", [])
        embeddings = [item.get("embedding", []) for item in openai_data]
        return {"embeddings": embeddings}
    except Exception:
        return {"embeddings": []}
