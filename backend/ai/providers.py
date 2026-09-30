"""Server-side cloud LLM providers.

The browser used to call Mistral, Google and OpenRouter directly with the keys
inlined in the bundle (`import.meta.env.VITE_*`), which shipped the secrets to
every visitor. Those three providers now live here: the keys stay in the
process environment and the browser only ever talks to this Flask API.

Implemented with `requests` (already a dependency) to avoid pulling another
provider SDK into the backend.
"""

import json
import logging
import os
from collections.abc import Mapping
from typing import Any, Dict, Iterator, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30
GOOGLE_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


def _content_to_text(content: Any) -> str:
    """Flatten a LangChain message content into plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts)
    return "" if content is None else str(content)


def split_system_prompt(messages: List[Any]) -> Tuple[str, List[Dict[str, str]]]:
    """Return `(system_prompt, chat_messages)` from a LangChain message list.

    Google only accepts a single system instruction and rejects assistant-first
    conversations, so the roles are normalised here once for every provider.
    """
    system_parts: List[str] = []
    turns: List[Dict[str, str]] = []

    for message in messages:
        # Flask hands over plain dicts (`{"role": ..., "content": ...}`) while
        # the LangChain path passes message objects. `getattr` silently returned
        # the default on a dict, so every message was treated as assistant.
        if isinstance(message, Mapping):
            role = message.get("type") or message.get("role")
            text = _content_to_text(message.get("content"))
        else:
            role = getattr(message, "type", None) or getattr(message, "role", None)
            text = _content_to_text(getattr(message, "content", message))
        if not text:
            continue

        if role == "system":
            system_parts.append(text)
        elif role in ("user", "human"):
            turns.append({"role": "user", "content": text})
        else:
            turns.append({"role": "assistant", "content": text})

    return "\n\n".join(system_parts), turns


def _sse_lines(response: requests.Response) -> Iterator[dict]:
    """Yield the decoded payloads of an SSE response."""
    for raw in response.iter_lines():
        if not raw:
            continue
        line = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if not payload or payload == "[DONE]":
            continue
        try:
            yield json.loads(payload)
        except json.JSONDecodeError:
            logger.debug("Ignoring malformed SSE payload: %.80s", payload)


class GoogleProvider:
    """Gemini via the REST streaming endpoint."""

    name = "google"

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.model = model or os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("VITE_GOOGLE_KEY")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    @property
    def label(self) -> str:
        """Shown to the user so they know which model actually answered."""
        return self.model

    def _request(self, messages: List[Any]):
        system_prompt, turns = split_system_prompt(messages)
        if not turns:
            raise ValueError("No user message to send")

        contents = [
            {
                "role": "model" if turn["role"] == "assistant" else "user",
                "parts": [{"text": turn["content"]}],
            }
            for turn in turns
        ]
        body: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"temperature": 0},
        }
        if system_prompt:
            body["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        return requests.post(
            f"{GOOGLE_ENDPOINT}/{self.model}:streamGenerateContent",
            params={"alt": "sse", "key": self.api_key},
            headers={"Content-Type": "application/json"},
            json=body,
            timeout=REQUEST_TIMEOUT,
            stream=True,
        )

    def stream(self, messages: List[Any]) -> Iterator[str]:
        response = self._request(messages)
        response.raise_for_status()
        try:
            for event in _sse_lines(response):
                for candidate in event.get("candidates") or []:
                    for part in (candidate.get("content") or {}).get("parts") or []:
                        text = part.get("text")
                        if text:
                            yield text
        finally:
            response.close()

    def invoke(self, messages: List[Any]) -> str:
        return "".join(self.stream(messages))


class OpenRouterProvider:
    """OpenRouter via the OpenAI-compatible chat completions endpoint."""

    name = "openRouter"

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.model = model or os.getenv(
            "OPENROUTER_MODEL", "google/gemma-3-27b-it:free"
        )
        self.api_key = (
            api_key
            or os.getenv("OPEN_ROUTER_API_KEY")
            or os.getenv("OPENROUTER_API_KEY")
            or os.getenv("VITE_OPEN_ROUTER_KEY")
        )

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    @property
    def label(self) -> str:
        """Shown to the user so they know which model actually answered."""
        return self.model

    def _request(self, messages: List[Any]):
        system_prompt, turns = split_system_prompt(messages)
        if not turns:
            raise ValueError("No user message to send")

        payload = [turn for turn in turns]
        if system_prompt:
            payload = [{"role": "system", "content": system_prompt}] + payload

        return requests.post(
            OPENROUTER_ENDPOINT,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            json={
                "model": self.model,
                "temperature": 0,
                "stream": True,
                "messages": payload,
            },
            timeout=REQUEST_TIMEOUT,
            stream=True,
        )

    def stream(self, messages: List[Any]) -> Iterator[str]:
        response = self._request(messages)
        response.raise_for_status()
        try:
            for event in _sse_lines(response):
                for choice in event.get("choices") or []:
                    text = (choice.get("delta") or {}).get("content")
                    if text:
                        yield text
        finally:
            response.close()

    def invoke(self, messages: List[Any]) -> str:
        return "".join(self.stream(messages))


def build_cloud_providers() -> List[Any]:
    """Instantiate the cloud providers that have a key configured."""
    providers = [GoogleProvider(), OpenRouterProvider()]
    available = [p for p in providers if p.available]
    for provider in providers:
        if not provider.available:
            logger.info("Provider %s disabled: no API key configured", provider.name)
        else:
            logger.info("Provider %s enabled (%s)", provider.name, provider.model)
    return available
