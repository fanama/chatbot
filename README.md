# Chatbot

RAG chatbot with a Svelte frontend and a Flask backend. Conversations are answered by a local Ollama model, with Google Gemini, OpenRouter and Mistral as ordered fallbacks. Documents (text, code, PDF) can be uploaded, chunked into a Chroma collection and retrieved as context.

## Features

- Streaming responses over SSE with a working **Stop** button (real `AbortController`, partial answer kept)
- RAG over a local Chroma collection: upload, chunk, search, delete
- Answer resilience: if Ollama is down, the next configured cloud provider takes over
- Markdown rendering with code-block copy buttons, sanitized with DOMPurify
- Text-to-speech for answers, speech-to-text for input
- Lazy-loaded PDF viewer and tutorial video (not in the initial bundle)

## Stack

| Layer | Tech |
| --- | --- |
| Frontend | Svelte 5 (legacy syntax), TypeScript, Vite, Tailwind |
| Backend | Flask, LangChain, ChromaDB, `requests` |
| Local model | Ollama (`granite4:7b-a1b-h` by default) |
| Cloud | Google Gemini, OpenRouter, Mistral |

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- [Bun](https://bun.sh) (or npm)
- [Ollama](https://ollama.com) running locally, with the model pulled:
  ```bash
  ollama pull granite4:7b-a1b-h
  ```
  Ollama is optional: without it, a cloud provider is used directly.

## Installation

1. **Clone the repository**

   ```bash
   git clone git@github.com:fanama/chatbot.git
   ```

2. **Install frontend dependencies**

   ```bash
   bun install
   ```

3. **Set up the Python environment**

   ```bash
   uv sync
   ```

   This creates `.venv` from `pyproject.toml` and the pinned `uv.lock`, so every
   contributor and CI run gets the exact same versions. Use `uv sync --frozen`
   to fail instead of updating the lockfile.

4. **Configure the environment**

   Create a `.env` file in the repository root:

   ```env
   # --- Frontend ---
   VITE_TITLE=MyApp
   # Leave empty to call the backend on the same origin (proxied by Vite).
   VITE_URL=http://127.0.0.1:3000

   # --- Backend ---
   HOST=127.0.0.1
   PORT=3000
   FLASK_DEBUG=1
   LOG_LEVEL=INFO

   # --- Cloud fallbacks (optional, order matters) ---
   MISTRAL_API_KEY=
   GOOGLE_API_KEY=
   GOOGLE_MODEL=gemini-2.0-flash
   OPENROUTER_API_KEY=
   ```

   **Keep API keys out of `VITE_*` variables.** Anything prefixed with `VITE_` is
   inlined into the JavaScript bundle and is readable by every visitor. The
   backend still reads the legacy `VITE_MISTRAL_KEY`, `VITE_GOOGLE_KEY` and
   `VITE_OPEN_ROUTER_KEY` names as a fallback, but you should migrate them to
   the `*_API_KEY` names above.

5. **Start both servers**

   Backend, in a first terminal:

   ```bash
   uv run server.py
   ```

   Frontend, in a second terminal:

   ```bash
   bun run dev
   ```

   `uv run` uses `.venv` without activating it, so no `source .venv/bin/activate`
   is needed. In development, `vite.config.ts` proxies `/chat-sse`, `/chat`,
   `/query`, `/documents`, `/empty-documents` and `/initialize` to
   `127.0.0.1:3000`, so leaving `VITE_URL` empty works out of the box.

## Production build

```bash
bun run build      # outputs dist/
bun run preview    # serves the built frontend
```

The backend serves the built frontend from `dist/`, so deploying means copying
`dist/` next to `server.py`.

## API

| Method | Route | Description |
| --- | --- | --- |
| `POST` | `/chat-sse` | Streaming answer. Body: `query`, `history`, `useVectorstore`, `stream` |
| `POST` | `/chat` | Non-streaming answer |
| `POST` | `/query` | Search the collection |
| `GET` | `/documents` | List documents |
| `POST` | `/documents` | Add documents |
| `PUT` | `/documents` | Update a document |
| `DELETE` | `/documents` | Delete by ids |
| `DELETE` | `/empty-documents` | Clear the collection |
| `POST` | `/initialize` | Create the collection |

`/chat-sse` emits Server-Sent Events where every payload is a JSON object
followed by a final `data: [DONE]` sentinel:

```
data: {"type": "provider", "provider": "mistral-large-latest"}
data: {"type": "text", "text": "Hello"}
data: {"type": "text", "text": " world"}
data: {"type": "error", "text": "Erreur interne pendant la génération."}
data: [DONE]
```

The `provider` frame always comes first and names the model that actually
answered, which is what the UI badge displays. It is emitted by the server
rather than derived from the requested `providerName`, so it stays correct when
a provider is skipped or a fallback kicks in.

## Configuration notes

- **Provider order**: Ollama first, then Mistral, Google and OpenRouter. Only
  the providers with a configured key are tried.
- **RAG**: when `useVectorstore` is enabled the retrieved chunks are merged into
  a single system prompt before the call.
- **CORS is currently open** (`CORS(app)` in `server.py`). This is fine for local
  development but should be restricted to the frontend origin before deploying.

## Development

```bash
bun run check    # svelte-check + tsc
bun run dev      # vite dev server

uv run python server.py   # backend
uv sync                   # add or update a Python dependency
```

Python dependencies are declared in `pyproject.toml` and pinned in `uv.lock`.
Do not `pip install` into `.venv`: the next `uv sync` would silently remove the
package. Use `uv add <package>`, which updates both files.

The backend has no test suite yet. The checks that exist are:

```bash
uv run python -m compileall -q server.py backend/
bun run check
bun run build
```

## Contribution

Contributions are welcome! Please open an issue to discuss significant changes before submitting a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contact

For any questions or suggestions, please contact:

- Email: f.rakotoasimbola@gmail.com
- LinkedIn: [Fana Rakotoasimbola](https://www.linkedin.com/in/fanama/)
