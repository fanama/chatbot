"""Provider chain for chat answers.

Order: Mistral -> Google Gemini -> OpenRouter -> local Ollama. Every request
walks the chain and the first provider that produces text wins, so an answer
does not depend on what the host machine is able to run (Ollama is the last
resort, not the first choice). When every provider fails the caller still gets
a readable message instead of an exception.
"""

import logging
import os
from typing import Any, Iterator, List, Tuple

from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage

from backend.ai.providers import build_cloud_providers
from backend.limiter.rate_limiter import RateLimiter
from backend.tools.basic import get_time, get_weather, web_search
from backend.tools.math import addition, calculator, division
from backend.tools.store import query_collection_tool

logger = logging.getLogger(__name__)

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or os.getenv("VITE_MISTRAL_KEY")
if MISTRAL_API_KEY:
    os.environ["MISTRAL_API_KEY"] = MISTRAL_API_KEY

# -----------------------------------------------------
# 1. MODELS, PROMPTS AND TOOLS (shared by the agent providers)
# -----------------------------------------------------

# Single source of truth for the model identifiers: the badge sent to the client
# must not drift from what the constructor actually loads.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "granite4:7b-a1b-h")
# Overridable so a plan/credit change on la plateforme.mistral.ai does not
# need a code edit: `mistral-small-latest` was returning 429 (rate_limited,
# code 1300) on this key while the ministral tier answered fine.
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "ministral-14b-latest")

AGENT_SYSTEM_PROMPT = (
    "You are a professional assistant named Fana. Use tools if needed."
)
# Google and OpenRouter are called as plain chat completions: there is no tool
# loop on that path, so the prompt must not ask for tools that never get called.
CHAT_SYSTEM_PROMPT = (
    "You are a professional assistant named Fana. Provide a direct answer."
)

# Returned when the whole chain failed: a response the user can act on beats an
# opaque 500, and the badge simply stays hidden (no `provider` frame is sent).
NO_PROVIDER_MESSAGE = (
    "Je ne peux pas répondre pour le moment : Mistral, Google, OpenRouter et "
    "Ollama ont tous échoué. Vérifiez vos clés API, votre connexion réseau et "
    "qu'Ollama soit bien lancé (`ollama serve`), puis réessayez."
)

TOOLS = [
    get_weather,
    web_search,
    get_time,
    addition,
    division,
    calculator,
    query_collection_tool,
]

llm_ollama = ChatOllama(
    model=OLLAMA_MODEL,
    temperature=0,
    timeout=10,
    max_retries=1,
)

agent_executor = create_agent(
    model=llm_ollama,
    tools=TOOLS,
    system_prompt=AGENT_SYSTEM_PROMPT,
)

# -----------------------------------------------------
# 2. LE PREMIER CHOIX : MISTRAL (même agent, mêmes outils)
# -----------------------------------------------------

mistral_agent = None
if MISTRAL_API_KEY:
    llm_mistral = ChatMistralAI(
        model=MISTRAL_MODEL,
        temperature=0,
        max_retries=2,
        # Was unset: a stalled request could pin a worker thread for minutes.
        timeout=30,
    )
    try:
        mistral_agent = create_agent(
            model=llm_mistral,
            tools=TOOLS,
            system_prompt=AGENT_SYSTEM_PROMPT,
        )
    except Exception:
        # Never let a provider-construction problem break the whole app: the
        # chain simply starts at the next provider that is configured.
        logger.exception("Mistral agent could not be built, skipping Mistral")
        mistral_agent = None
else:
    logger.warning("Mistral disabled: no MISTRAL_API_KEY configured")


# -----------------------------------------------------
# 3. ADAPTATEURS : agent avec outils / chat simple
# -----------------------------------------------------

def _extract_text(message) -> Iterator[str]:
    """Yield only the text parts of a streamed LangChain message.

    The server serialised `token.content_blocks` directly, so the client used to
    receive a Python list repr and had to guess the format. Tool-call blocks are
    dropped: they are not displayable text.
    """
    blocks = getattr(message, "content_blocks", None)
    if isinstance(blocks, list):
        for block in blocks:
            if (
                isinstance(block, dict)
                and block.get("type") == "text"
                and block.get("text")
            ):
                yield block["text"]
        return

    content = getattr(message, "content", None)
    if isinstance(content, str) and content:
        yield content


def _provider_label(provider: Any) -> str:
    """Human-readable model name for the UI badge."""
    label = getattr(provider, "label", None)
    if isinstance(label, str) and label:
        return label
    return getattr(provider, "name", provider.__class__.__name__)


class _AgentProvider:
    """A LangChain agent (model + tools) exposed as a provider.

    Used for Mistral and Ollama, the two models that can call the tools.
    """

    def __init__(self, name: str, label: str, agent: Any):
        self.name = name
        self.label = label
        self._agent = agent

    def invoke(self, messages) -> str:
        response = self._agent.invoke({"messages": list(messages)})
        last = response["messages"][-1].content
        return last if isinstance(last, str) else str(last or "")

    def stream(self, messages) -> Iterator[str]:
        for token, _metadata in self._agent.stream(
            {"messages": list(messages)},
            stream_mode="messages",
        ):
            yield from _extract_text(token)


class _PlainChatProvider:
    """A raw chat-completions provider (Google, OpenRouter).

    Those integrations carry no persona of their own, so the system message is
    prepended here; any RAG context system message from the request follows it
    and both are merged by `split_system_prompt`.
    """

    def __init__(self, inner: Any):
        self._inner = inner
        self.name = inner.name
        self.label = _provider_label(inner)

    def _prepared(self, messages):
        return [SystemMessage(content=CHAT_SYSTEM_PROMPT), *messages]

    def invoke(self, messages) -> str:
        return self._inner.invoke(self._prepared(messages))

    def stream(self, messages) -> Iterator[str]:
        yield from self._inner.stream(self._prepared(messages))


cloud_providers = build_cloud_providers()


def _build_chain() -> List[Any]:
    """Mistral first, then Google, OpenRouter, and local Ollama last."""
    chain: List[Any] = []
    if mistral_agent is not None:
        chain.append(_AgentProvider("mistral", MISTRAL_MODEL, mistral_agent))
    chain.extend(_PlainChatProvider(provider) for provider in cloud_providers)
    # Always present: an unavailable local model must not remove the last
    # resort, and its fast failure (timeout=10) keeps the promise of an answer.
    chain.append(_AgentProvider("ollama", OLLAMA_MODEL, agent_executor))
    return chain


def _chain(first: str, iterator: Iterator[str]) -> Iterator[str]:
    """Re-emit the eagerly fetched first token followed by the rest."""
    yield first
    yield from iterator


def _prepend(
    event: Tuple[str, str], iterator: Iterator[str]
) -> Iterator[Tuple[str, str]]:
    """Emit one metadata event before the text tokens it describes."""
    yield event
    for token in iterator:
        yield ("text", token)


class AIProviderManager:
    """Mistral -> Google -> OpenRouter -> Ollama, then a readable message."""

    def __init__(self):
        self.limiter = RateLimiter(max_calls_per_second=10)
        self.providers = _build_chain()
        logger.info(
            "Provider chain: %s",
            " -> ".join(_provider_label(p) for p in self.providers),
        )

    def _run(self, messages, stream: bool):
        """Return the first answer from the ordered chain.

        `stream` selects between the streaming and the buffered interface.
        Returns a generator for streams, a string otherwise. Raises the last
        error if every provider failed (or answered with nothing).
        """
        if not self.providers:
            raise RuntimeError("No provider configured")

        last_error: Exception = RuntimeError("No provider configured")

        for provider in self.providers:
            name = getattr(provider, "name", provider.__class__.__name__)
            try:
                if stream:
                    iterator = iter(provider.stream(messages))
                    # Pull the first token here: a connection or auth error would
                    # otherwise surface after the response had started, outside
                    # this loop, and no provider would be left to try. An empty
                    # stream counts as a failure for the same reason.
                    first = next(iterator, None)
                    if first is None:
                        raise RuntimeError("empty stream")
                    return _prepend(
                        ("provider", _provider_label(provider)),
                        _chain(first, iterator),
                    )

                answer = provider.invoke(messages)
                if not answer or not answer.strip():
                    raise RuntimeError("empty response")
                return answer
            except Exception as exc:
                last_error = exc
                logger.warning("Provider %s failed: %s", name, exc)

        raise last_error

    def call(self, messages):
        self.limiter.wait_for_slot()

        try:
            return self._run(messages, stream=False)
        except Exception:
            logger.error("Every provider failed", exc_info=True)
            return NO_PROVIDER_MESSAGE

    def call_stream(self, messages) -> Iterator[Tuple[str, str]]:
        """Yield `(kind, text)` events: one `provider` then `text` tokens.

        The provider is announced *before* the first token so the client can
        label the answer even if the user stops the generation immediately.
        """
        self.limiter.wait_for_slot()

        try:
            yield from self._run(messages, stream=True)
        except Exception:
            logger.error("Every provider failed", exc_info=True)
            # No `provider` frame: the client hides the badge for empty values.
            yield ("text", NO_PROVIDER_MESSAGE)
