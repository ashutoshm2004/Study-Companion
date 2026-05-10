"""
Groq LLM client — free, fast, reliable.
Get your key at https://console.groq.com
"""
import json
import logging
import re
import time

from groq import Groq
from backend.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)
_client = None

# Models that support response_format=json_object on Groq
_JSON_MODE_MODELS = {
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "gemma2-9b-it",
    "gemma-7b-it",
}


def _get_client() -> Groq:
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY not set. Get your free key at https://console.groq.com")
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def _sanitize(messages: list[dict]) -> list[dict]:
    """Merge consecutive same-role messages — Groq requires strict alternation."""
    out = []
    for msg in messages:
        if out and out[-1]["role"] == msg["role"]:
            out[-1]["content"] += "\n\n" + msg["content"]
        else:
            out.append({"role": msg["role"], "content": msg["content"]})
    # Must start with user
    if out and out[0]["role"] != "user":
        out = out[1:]
    return out or [{"role": "user", "content": "Please respond."}]


def chat(system: str, messages: list[dict], max_tokens: int = 1024, temperature: float = 0.7) -> tuple[str, int]:
    client = _get_client()
    msgs = [{"role": "system", "content": system}] + _sanitize(messages)
    resp = client.chat.completions.create(model=GROQ_MODEL, messages=msgs, max_tokens=max_tokens, temperature=temperature)
    return resp.choices[0].message.content or "", resp.usage.total_tokens


def chat_json(system: str, messages: list[dict], max_tokens: int = 2048) -> tuple[dict | list, int]:
    system_j = system + (
        "\n\nCRITICAL: Reply with ONLY valid JSON. "
        "No markdown fences, no explanation — start directly with { or [."
    )
    client = _get_client()
    msgs = [{"role": "system", "content": system_j}] + _sanitize(messages)

    kwargs: dict = dict(model=GROQ_MODEL, messages=msgs, max_tokens=max_tokens, temperature=0.2)
    if GROQ_MODEL in _JSON_MODE_MODELS:
        kwargs["response_format"] = {"type": "json_object"}

    resp = client.chat.completions.create(**kwargs)
    text = resp.choices[0].message.content or ""
    return _parse_json(text), resp.usage.total_tokens


def _parse_json(text: str) -> dict | list:
    clean = re.sub(r"```(?:json)?|```", "", text).strip()
    # Find first { or [
    b, s = clean.find("{"), clean.find("[")
    start = min(x for x in [b, s] if x >= 0) if any(x >= 0 for x in [b, s]) else 0
    clean = clean[start:]
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        # Try trimming from end
        for end in range(len(clean), 0, -1):
            try:
                return json.loads(clean[:end])
            except json.JSONDecodeError:
                continue
    raise ValueError("LLM did not return valid JSON. Try again — if it keeps failing switch to gemma2-9b-it in your .env")


def build_context(chunks: list[dict]) -> str:
    lines = ["[DOCUMENT EXCERPTS]"]
    for i, c in enumerate(chunks, 1):
        pg = f"(Page {c['page']})" if c.get("page") else ""
        lines.append(f"\n--- Excerpt {i} {pg} ---\n{c['text']}")
    lines.append("\n[END]")
    return "\n".join(lines)
