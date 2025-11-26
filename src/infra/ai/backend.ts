
import type { Input, Response } from "../../domain/entities/message";

const url = import.meta.env.VITE_URL || ""
export class BackendAI {
  name = "backend";
  private backendEndpoint: string;

  constructor(backendEndpoint: string = url) {
    this.backendEndpoint = backendEndpoint;
  }

  async chat({
    text,
    history = [],
    stream = (chunk) => console.log({ chunk }),
  }: Input): Promise<Response> {
    let result = "";

    try {
      const url = `${this.backendEndpoint}/chat-sse`;

      // Construire le payload attendu par ton endpoint Flask
      const payload = {
        query: text,
        history: history.map(msg => { return { role: msg.sender, content: msg.text } }),
        nResults: 5,
        include: [],
        metadatas: null,
      };

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok || !response.body) {
        throw new Error(
          `SSE connection failed: ${response.status} ${response.statusText}`
        );
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let bracketNumber = 0
      // Lecture du flux SSE
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const textChunk = decoder.decode(value, { stream: true });

        // Chaque ligne contient :  data: <token>
        for (const line of textChunk.split("\n")) {
          if (line.startsWith("data: ")) {
            const token = line.replace("data: ", "").trim();
            if (token == "[]") bracketNumber++;
            console.log(bracketNumber)
            if (token && token != '[]') {
              let text = ""

              try {
                // Convert python-like list/dict format to JSON
                const fixed = token
                  .replace(/'/g, '"');   // replace single quotes with double quotes
                const fixesArr = JSON.parse(fixed)
                const parsed = JSON.parse(fixed)[fixesArr.length - 1]
                text = parsed.text || '';
                if (parsed.type != 'text') {
                  continue
                }
              } catch (err) {
                text = token;
                continue
              }

              stream(text);
              result += text;
            }
          }
        }
      }

      return { text: result, provider: this.name };
    } catch (error) {
      console.error("SSE Chat Error:", error);
      throw new Error(String(error));
    }
  }

  /** La méthode models() reste inchangée ou peut être retirée si inutile */
  async models(): Promise<string[]> {
    return [];
  }
}

