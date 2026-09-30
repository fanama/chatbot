import type { Input, Response } from "../../domain/entities/message";
import { AbortedError, BACKEND_URL, isAbortError } from "./config";

/**
 * The single entry point to every LLM.
 *
 * Mistral, Google, OpenRouter and Ollama used to be called straight from the
 * browser with `import.meta.env.VITE_*` keys, which inlined the secrets into the
 * built JS bundle. They now run in the Flask backend, which owns the
 * Ollama -> cloud failover, so this class only speaks to our own API.
 */
export class BackendAI {
  name = "backend";

  constructor(private backendEndpoint: string = BACKEND_URL) {}

  async chat({
    text,
    history = [],
    useVectorstore,
    signal,
    stream = () => {},
    onProvider = () => {},
  }: Input): Promise<Response> {
    if (!text || !text.trim()) {
      throw new Error("Empty message");
    }

    const url = `${this.backendEndpoint}/chat-sse`;
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal,
      body: JSON.stringify({
        query: text,
        history: history
          .filter((msg) => msg.text)
          .map((msg) => ({ role: msg.sender, content: msg.text })),
        nResults: 5,
        useVectorstore: useVectorstore ?? true,
      }),
    });

    if (signal?.aborted) {
      throw new AbortedError();
    }

    if (!response.ok || !response.body) {
      const detail = await response.text().catch(() => "");
      throw new Error(
        `Backend responded ${response.status} ${response.statusText}${
          detail ? `: ${detail.slice(0, 200)}` : ""
        }`,
      );
    }

    const { text: content, provider } = await this.readStream(
      response.body,
      stream,
      onProvider,
      signal,
    );

    if (!content.trim()) {
      throw new Error("The backend returned an empty response.");
    }

    return { text: content, provider };
  }

  /**
   * Reads the SSE stream produced by `/chat-sse`.
   *
   * The decoder is used in streaming mode and lines are buffered: a network
   * chunk can split a multi-byte character or an SSE frame in half, which
   * previously produced corrupted accents and dropped tokens.
   */
  private async readStream(
    body: ReadableStream<Uint8Array>,
    onToken: (text: string) => void,
    onProvider: (provider: string) => void,
    signal?: AbortSignal,
  ): Promise<{ text: string; provider: string }> {
    const reader = body.getReader();
    const decoder = new TextDecoder();

    let buffer = "";
    let result = "";
    // Empty until the stream announces which model answers: rendering
    // "backend" in the badge would tell the user nothing.
    let provider = "";

    const onAbort = () => {
      // Releases the connection and the worker thread on the Flask side.
      reader.cancel().catch(() => {});
    };
    signal?.addEventListener("abort", onAbort, { once: true });

    const handle = (line: string): boolean => {
      // Returns false when the stream is finished.
      if (!line.startsWith("data: ")) {
        return true;
      }

      const payload = line.slice("data: ".length).trim();
      if (!payload) {
        return true;
      }
      if (payload === "[DONE]") {
        return false;
      }

      let parsed: { type?: string; text?: string; provider?: string };
      try {
        parsed = JSON.parse(payload);
      } catch {
        // Tolerate a raw text frame.
        onToken(payload);
        result += payload;
        return true;
      }

      if (parsed.type === "error") {
        throw new Error(parsed.text || "The backend reported a generation error.");
      }
      if (parsed.type === "provider" && parsed.provider) {
        // Arrives before the first token: identifies the model that will answer.
        provider = parsed.provider;
        onProvider(parsed.provider);
        return true;
      }
      if (parsed.type === "text" && parsed.text) {
        onToken(parsed.text);
        result += parsed.text;
      }
      return true;
    };

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }
        if (signal?.aborted) {
          throw new AbortedError();
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        // The last element may be an incomplete frame: keep it buffered.
        buffer = lines.pop() ?? "";

        for (const raw of lines) {
          if (!handle(raw.trim())) {
            return { text: result, provider };
          }
        }
      }

      const tail = buffer.trim();
      if (tail && !handle(tail)) {
        return { text: result, provider };
      }

      buffer += decoder.decode();
      return { text: result, provider };
    } catch (error) {
      if (signal?.aborted || isAbortError(error)) {
        throw new AbortedError();
      }
      throw error;
    } finally {
      signal?.removeEventListener("abort", onAbort);
      reader.releaseLock();
    }
  }
}
