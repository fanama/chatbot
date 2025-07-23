# Chatbot

## Installation

### Prerequisites

- Python 3.x
- chromadb
- Bun.js

### Steps

1. **Clone the repository:**

   ```bash
   git clone git@github.com:fanama/chatbot.git
   ```

- or
  ```bash
  git clone https://github.com/fanama/chatbot.git
  ```

2. **Install Bun.js dependencies:**

   ```bash
   bun install
   ```

3. **Set up the Python virtual environment:**

   ```bash
   uv pip install -r pyproject.toml
   ```

4. **Set up environment variables:**

   Create a `.env` file in the root directory and add your Google Studio and Mistral keys:

   ```env
   GOOGLE_STUDIO_KEY=your_google_studio_key
   MISTRAL_KEY=your_mistral_key
   ```

5. **Start the development server:**

   ```bash
   bun run dev
   ```

## Server bun

```bash
bun proxy.ts
```

## init chroma DB

- install

```sh
pip install chromadb
```

- launch

```sh
chroma run --path ./getting-started
```

## Lanch the whole app

To launch the app you will need 3 terminals. One to launch the bun server, one for the database and one for the python server

- bun

```sh
bun proxy.ts
```

- database

```sh
source .venv/bin/activate  # On Windows use `venv\Scripts\activate`
chroma run --path ./getting-started
```
