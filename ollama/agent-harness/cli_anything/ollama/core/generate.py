"""OpenAI-compatible text generation and chat for prima.cpp/llama.cpp."""

import sys
from cli_anything.ollama.utils.ollama_backend import api_post, api_post_stream


def generate(
    base_url: str,
    model: str,
    prompt: str,
    system: str | None = None,
    template: str | None = None,
    context: list | None = None,
    options: dict | None = None,
    stream: bool = True,
):
    """Generate a text completion via OpenAI-compatible /v1/completions."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    data = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }
    if options:
        if "temperature" in options:
            data["temperature"] = options["temperature"]
        if "top_p" in options:
            data["top_p"] = options["top_p"]
        if "num_predict" in options:
            data["max_tokens"] = options["num_predict"]

    if stream:
        return api_post_stream(base_url, "/v1/chat/completions", data)
    else:
        result = api_post(base_url, "/v1/chat/completions", data, timeout=300)
        # Convert OpenAI response to Ollama-compatible format
        choice = result.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        return {
            "response": content,
            "done": True,
            "message": {"role": "assistant", "content": content},
        }


def chat(
    base_url: str,
    model: str,
    messages: list[dict],
    options: dict | None = None,
    stream: bool = True,
):
    """Send a chat completion request via /v1/chat/completions."""
    data = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }
    if options:
        if "temperature" in options:
            data["temperature"] = options["temperature"]
        if "top_p" in options:
            data["top_p"] = options["top_p"]
        if "num_predict" in options:
            data["max_tokens"] = options["num_predict"]

    if stream:
        return api_post_stream(base_url, "/v1/chat/completions", data)
    else:
        result = api_post(base_url, "/v1/chat/completions", data, timeout=300)
        # Convert OpenAI response to Ollama-compatible format
        choice = result.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        return {
            "done": True,
            "message": {"role": "assistant", "content": content},
        }


def stream_to_stdout(chunks) -> dict:
    """Print streaming tokens to stdout and return the final response."""
    final = {}
    for chunk in chunks:
        if "response" in chunk:
            sys.stdout.write(chunk["response"])
            sys.stdout.flush()
        elif "message" in chunk and "content" in chunk["message"]:
            sys.stdout.write(chunk["message"]["content"])
            sys.stdout.flush()
        if chunk.get("done", False):
            final = chunk
    sys.stdout.write("\n")
    sys.stdout.flush()
    return final
