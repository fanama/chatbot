import logging
import os
from typing import Any, Iterator, List, Optional, Tuple

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
# 1. SETUP DE L'AGENT PRINCIPAL (OLLAMA)
# -----------------------------------------------------

# Single source of truth for the model identifiers: the badge sent to the client
# must not drift from what the constructor actually loads.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "granite4:7b-a1b-h")
MISTRAL_MODEL = "mistral-small-latest"

llm_ollama = ChatOllama(
    model=OLLAMA_MODEL,
    temperature=0,
    timeout=10,
    max_retries=1,
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

agent_executor = create_agent(
    model=llm_ollama,
    tools=TOOLS,
    system_prompt="You are a professional assistant named Fana. Use tools if needed.",
)

# -----------------------------------------------------
# 2. SETUP DU BACKUP SIMPLE (MISTRAL)
# -----------------------------------------------------

llm_backup = None
if MISTRAL_API_KEY:
    llm_backup = ChatMistralAI(
        model=MISTRAL_MODEL,
        temperature=0,
        max_retries=2,
        # Was unset: a stalled request could pin a worker thread for minutes.
        timeout=30,
    )

# Errors that are clearly local (bad input, broken tool, programming mistake).
# Falling back to Mistral for those would pay twice and fail identically, since
# the backup model receives the same messages.
NO_FALLBACK_ERRORS = (
    ValueError,
    TypeError,
    KeyError,
    IndexError,
    AttributeError,
    AssertionError,
)
_NO_FALLBACK_NAMES = (
    "ToolException",
    "ToolExecutionException",
    "OutputParserException",
    "ValidationError",
    "ContextWindowExceeded",
    "MessageTooLong",
)


def _should_fallback(exc: BaseException) -> bool:
    """Only pay for the cloud backup when the local provider itself failed."""
    if isinstance(exc, NO_FALLBACK_ERRORS):
        return False
    return not any(marker in type(exc).__name__ for marker in _NO_FALLBACK_NAMES)


_FALLBACK_SYSTEM_PROMPT = (
    "You are Fana, a helpful assistant. Provide a direct answer without using tools."
)


class _MistralFallback:
    """Adapts LangChain's ChatMistralAI to the provider interface below."""

    name = "mistral"

    @property
    def label(self) -> str:
        """Shown to the user so they know which model actually answered."""
        return MISTRAL_MODEL

    def invoke(self, messages) -> str:
        return llm_backup.invoke(messages).content

    def stream(self, messages) -> Iterator[str]:
        for chunk in llm_backup.stream(messages):
            yield from _extract_text(chunk)


cloud_providers = build_cloud_providers()


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


def _chain(first: Optional[str], iterator: Iterator[str]) -> Iterator[str]:
    """Re-emit the eagerly fetched first token followed by the rest."""
    if first is not None:
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
    """Rate Limit -> local Ollama agent -> cloud fallbacks (Mistral, Google, OpenRouter)."""

    def __init__(self):
        self.limiter = RateLimiter(max_calls_per_second=10)
        # Ordered by preference; only the ones with a key are present.
        self.cloud = list(cloud_providers)
        if llm_backup:
            self.cloud.insert(0, _MistralFallback())

    def _cloud_fallbacks(self) -> List[Any]:
        return list(getattr(self, "cloud", []))

    def _run_cloud(self, messages, stream: bool):
        """Try each cloud provider in order, returning the first success.

        `stream` selects between the streaming and the buffered interface.
        Returns a generator for streams, a string otherwise. Raises the last
        error if every provider failed.
        """
        fallbacks = self._cloud_fallbacks()
        if not fallbacks:
            raise RuntimeError("No cloud provider configured")

        prepared = [SystemMessage(content=_FALLBACK_SYSTEM_PROMPT)] + messages
        last_error: Optional[BaseException] = None

        for provider in fallbacks:
            name = getattr(provider, "name", provider.__class__.__name__)
            try:
                if stream:
                    iterator = iter(provider.stream(prepared))
                    # Pull the first token here: a connection or auth error would
                    # otherwise surface after the response had started, outside
                    # this loop, and no provider would be left to fall back to.
                    first = next(iterator, None)
                    label = _provider_label(provider)
                    return _prepend(("provider", label), _chain(first, iterator))
                return provider.invoke(prepared)
            except Exception as exc:
                last_error = exc
                logger.warning("Cloud provider %s failed: %s", name, exc)

        raise last_error if last_error else RuntimeError("No cloud provider succeeded")

    def call(self, messages):
        self.limiter.wait_for_slot()

        try:
            logger.debug("Calling local Ollama agent")
            response = agent_executor.invoke({"messages": messages})
            return response["messages"][-1].content
        except Exception as exc:
            if not self._cloud_fallbacks() or not _should_fallback(exc):
                logger.error("Local agent failed without fallback", exc_info=True)
                raise
            logger.warning("Ollama agent failed (%s), falling back to cloud", exc)
            return self._run_cloud(messages, stream=False)

    def call_stream(self, messages) -> Iterator[Tuple[str, str]]:
        """Yield `(kind, text)` events: one `provider` then `text` tokens.

        The provider is announced *before* the first token so the client can
        label the answer even if the user stops the generation immediately.
        """
        self.limiter.wait_for_slot()

        try:
            yield ("provider", OLLAMA_MODEL)
            for token, _metadata in agent_executor.stream(
                {"messages": messages},
                stream_mode="messages",
            ):
                for text in _extract_text(token):
                    yield ("text", text)
            return
        except Exception as exc:
            if not self._cloud_fallbacks() or not _should_fallback(exc):
                logger.error("Local streaming failed without fallback", exc_info=True)
                raise
            logger.warning("Ollama stream failed (%s), falling back to cloud", exc)

        yield from self._run_cloud(messages, stream=True)
