"""OpenAI-compatible REST API wrapper for prima.cpp/llama.cpp servers.

Provides the same interface as the original Ollama backend but uses
the standard OpenAI-compatible API endpoints that prima.cpp and llama.cpp expose.
"""

import requests
from typing import Any, Generator

DEFAULT_BASE_URL = "http://localhost:8080"


def api_get(
    base_url: str, endpoint: str, params: dict | None = None, timeout: int = 30
) -> Any:
    """Perform a GET request against the OpenAI-compatible API."""
    url = f"{base_url.rstrip('/')}{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        if resp.status_code == 204 or not resp.content:
            return {"status": "ok"}
        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            return resp.json()
        return {"status": "ok", "message": resp.text.strip()}
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Cannot connect to server at {base_url}. Is prima.cpp/llama.cpp running?"
        ) from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"API error {resp.status_code} on GET {endpoint}: {resp.text}"
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError(f"Request timed out: GET {endpoint}") from e


def api_post(
    base_url: str, endpoint: str, data: dict | None = None, timeout: int = 30
) -> Any:
    """Perform a POST request against the OpenAI-compatible API."""
    url = f"{base_url.rstrip('/')}{endpoint}"
    try:
        resp = requests.post(url, json=data, timeout=timeout)
        resp.raise_for_status()
        if resp.status_code == 204 or not resp.content:
            return {"status": "ok"}
        return resp.json()
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Cannot connect to server at {base_url}. Is prima.cpp/llama.cpp running?"
        ) from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"API error {resp.status_code} on POST {endpoint}: {resp.text}"
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError(f"Request timed out: POST {endpoint}") from e


def api_delete(
    base_url: str, endpoint: str, data: dict | None = None, timeout: int = 30
) -> Any:
    """Perform a DELETE request (stub — not supported by OpenAI-compatible API)."""
    return {
        "status": "not_supported",
        "message": "DELETE not available on OpenAI-compatible API",
    }


def api_post_stream(
    base_url: str, endpoint: str, data: dict | None = None, timeout: int = 300
) -> Generator[dict, None, None]:
    """Perform a POST request with streaming SSE response."""
    import json as json_mod

    url = f"{base_url.rstrip('/')}{endpoint}"
    if data is None:
        data = {}
    data["stream"] = True
    try:
        resp = requests.post(url, json=data, stream=True, timeout=timeout)
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                line_str = line.decode("utf-8", errors="replace")
                if line_str.startswith("data: "):
                    line_str = line_str[6:]
                if line_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json_mod.loads(line_str)
                    # Convert OpenAI SSE format to Ollama-compatible format
                    yield _convert_openai_chunk(chunk)
                except json_mod.JSONDecodeError:
                    continue
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Cannot connect to server at {base_url}. Is prima.cpp/llama.cpp running?"
        ) from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"API error {resp.status_code} on POST {endpoint}: {resp.text}"
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError(f"Request timed out: POST {endpoint}") from e


def _convert_openai_chunk(chunk: dict) -> dict:
    """Convert an OpenAI streaming chunk to Ollama-compatible format."""
    choices = chunk.get("choices", [])
    if not choices:
        return chunk
    choice = choices[0]
    delta = choice.get("delta", {})
    content = delta.get("content", "")
    finish_reason = choice.get("finish_reason")

    result = {}
    if content:
        result["response"] = content
        result["message"] = {"role": "assistant", "content": content}
    if finish_reason == "stop":
        result["done"] = True
    else:
        result["done"] = False
    return result


def is_available(base_url: str = DEFAULT_BASE_URL) -> bool:
    """Check if the server is reachable."""
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/health", timeout=5)
        return resp.status_code == 200
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False
