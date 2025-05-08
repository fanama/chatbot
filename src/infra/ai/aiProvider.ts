import type { Input, Response } from "../../domain/entities/message";
import { GoogleAI } from "./google";
import { MistralAI } from "./mistral";
import { OllamaAI } from "./ollama";
import { OpenRouterAI } from "./openRouter";

interface Provider {
  chat: (input: Input) => Promise<Response>;
  name: string;
}

export class AIProvider {
  private providers: Provider[];

  constructor() {
    this.providers = [
      new MistralAI(),
      new GoogleAI(),
      new OpenRouterAI(),
      new OllamaAI(),
    ];
  }

  getAll() {
    return this.providers.map((p) => p.name);
  }

  async chat(input: Input): Promise<Response> {
    try {
      const provider = this.providers.find(
        (p) => p.name === input.providerName,
      );
      if (provider) {
        const response = await provider.chat(input);
        if (response.text.trim() === "") {
          throw new Error(
            "Provider returned an empty response." + response.provider,
          );
        }
        return response;
      }
    } catch (err) {
      console.log(input.providerName + " does not exist");
    }
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
