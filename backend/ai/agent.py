import os
from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage

# Tes imports existants...
from backend.tools.basic import get_weather, web_search, get_time
from backend.tools.math import calculator, addition, division
from backend.tools.store import query_collection_tool
from backend.limiter.rate_limiter import RateLimiter

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or os.getenv("VITE_MISTRAL_KEY")
if MISTRAL_API_KEY:
    os.environ["MISTRAL_API_KEY"] = MISTRAL_API_KEY


# -----------------------------------------------------
# 1. SETUP DE L'AGENT PRINCIPAL (OLLAMA)
# -----------------------------------------------------


llm_ollama = ChatOllama(
    model="granite4:7b-a1b-h",
    temperature=0,
    timeout=10
)

TOOLS = [
    get_weather, web_search, get_time,
    addition, division, calculator,
    query_collection_tool
]

# Note: create_agent a été déprécié dans les versions récentes de LangChain,
# assure-toi d'utiliser une version compatible ou create_react_agent
agent_executor = create_agent(
    model=llm_ollama,
    tools=TOOLS,
    system_prompt="You are a professional assistant named Fana. Use tools if needed."
)

# -----------------------------------------------------
# 2. SETUP DU BACKUP SIMPLE (MISTRAL)
# -----------------------------------------------------

llm_backup = None
if MISTRAL_API_KEY:
    llm_backup = ChatMistralAI(
        model="mistral-large-latest",
        temperature=0,
        max_retries=2,
    )

# -----------------------------------------------------
# 3. MANAGER AVEC LOGIQUE DE BASCULE ET QUEUE
# -----------------------------------------------------


class AIProviderManager:
    """Gère la logique : Rate Limit -> Agent Local -> Fallback Cloud."""

    def __init__(self):
        # Initialise le limiteur à 10 requêtes / seconde
        self.limiter = RateLimiter(max_calls_per_second=10)

    def call(self, messages):
        # 1. On attend notre tour (Queueing logic)
        self.limiter.wait_for_slot()

        try:
            # TENTATIVE 1 : L'Agent Ollama
            print("🤖 Tentative avec Agent Ollama...")
            response = agent_executor.invoke({"messages": messages})
            return response['messages'][-1].content

        except Exception as e:
            if not llm_backup:
                raise e

            # TENTATIVE 2 : Fallback Mistral
            print(f"⚠️ Erreur Ollama ({e}). Bascule vers Mistral...")
            system_msg = SystemMessage(
                content="You are Fana, a helpful assistant. Provide a direct answer without using tools.")
            final_messages = [system_msg] + messages

            response = llm_backup.invoke(final_messages)
            return response.content

    def call_stream(self, messages):
        """Streaming avec la même logique de fallback et queue."""

        # 1. On attend notre tour avant de commencer le stream
        self.limiter.wait_for_slot()

        try:
            for token, metadata in agent_executor.stream(
                {"messages": messages},
                stream_mode="messages",
            ):
                yield token.content_blocks

        except Exception as e:
            if not llm_backup:
                yield f"Erreur critique : {str(e)}"
                return

            # TENTATIVE 2 : Stream du LLM simple
            system_msg = SystemMessage(content="You are Fana. Answer simply.")
            final_messages = [system_msg] + messages

            for chunk in llm_backup.stream(final_messages):
                yield chunk.content
