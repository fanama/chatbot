import type { Input } from "../../domain/entities/message";
import { GoogleAI } from "./google";
import { MistralAI } from "./mistral";
import { OpenRouterAI } from "./openRouter";

interface Provider {
  chat: (input: Input) => Promise<string>;
}

export class AIProvider {
  private providers: Provider[];

  constructor(
    providers: Provider[] = [
      new OpenRouterAI(),
      new MistralAI(),
      new GoogleAI(),
    ],
  ) {
    this.providers = providers;
  }

  async chat(input: Input): Promise<string> {
    for (const provider of this.providers) {
      try {
        const response = await provider.chat(input);
        if (response.trim() === "") {
          throw new Error("Provider returned an empty response.");
        }
        return response;
      } catch (error) {
        console.error(`Provider failed: ${error}`);
      }
    }
    throw new Error("All providers failed.");
  }
}
