import type { Input, Response } from "../../domain/entities/message";
import { GoogleAI } from "./google";
import { MistralAI } from "./mistral";
import { OllamaAI } from "./ollama";
import { OpenRouterAI } from "./openRouter";

interface Provider {
  chat: (input: Input) => Promise<Response>;
}

export class AIProvider {
  private providers: Provider[];

  constructor() {
    this.providers = [
      new OpenRouterAI(),
      new MistralAI(),
      new GoogleAI(),
      new OllamaAI(),
    ];
  }

  async chat(input: Input): Promise<Response> {
    for (const provider of this.providers) {
      try {
        const response = await provider.chat(input);
        if (response.text.trim() === "") {
          throw new Error(
            "Provider returned an empty response." + response.provider,
          );
        }
        return response;
      } catch (error) {
        console.error(`Provider failed: ${error}`);
      }
    }
    throw new Error("All providers failed.");
  }
}
