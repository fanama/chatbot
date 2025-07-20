import type { Input, Response } from "../../domain/entities/message";

export class MistralAI {
  name = "mistral";
  private mistralEndpoint: string;

  constructor(mistralEndpoint: string = "https://api.mistral.ai/v1") {
    this.mistralEndpoint = mistralEndpoint;
  }

  async chat({
    text,
    history = [],
    stream = (chunk: string) => console.log({ chunk })
  }: Input): Promise<Response> {
    let result = "";

    try {
      console.log("mistral");
      const model = "mistral-small-latest";
      const url = `${this.mistralEndpoint}/chat/completions`;

      const messages = [
        ...history.map((message) => ({
          role: message.sender !== "user" ? "assistant" : message.sender,
          content: message.text,
        }))
      ];

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          Authorization: `Bearer ${import.meta.env.VITE_MISTRAL_KEY}`,
        },
        body: JSON.stringify({
          model,
          stream: true,
          messages,
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`Network response was not ok: ${url}`);
      }

      const reader = response.body.getReader();

      await this.readStream(reader, (text: string) => {
        stream(text);
        result += text;
      });

      return { text: result, provider: this.name };
    } catch (error) {
      console.error("Mistral API Error:", error);
      throw new Error(JSON.stringify(error));
    }
  }

  private async readStream(
    reader: ReadableStreamDefaultReader<Uint8Array>,
    stream: (text: string) => void
  ): Promise<void> {
    const decoder = new TextDecoder();
    let done = false;

    while (!done) {
      const { value, done: streamDone } = await reader.read();
      done = streamDone;

      if (value) {
        const chunkStr = decoder.decode(value);
        const lines = chunkStr.split('\n').filter(line => line.trim() !== '');

        for (const line of lines) {
          const message = line.replace(/^data: /, '');

          if (message === '[DONE]') {
            continue;
          }

          try {
            const parsed = JSON.parse(message);
            const content = parsed.choices[0].delta.content;

            if (content) {
              stream(content);
            }
          } catch (error) {
            console.error("Error parsing JSON:", error);
          }
        }
      }
    }
  }
}
