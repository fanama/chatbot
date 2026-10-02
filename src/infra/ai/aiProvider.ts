import type { Input, Response } from "../../domain/entities/message";
import { BackendAI } from "./backend";
import { isAbortError } from "./config";

interface Provider {
  chat: (input: Input) => Promise<Response>;
  name: string;
}

// Never imported elsewhere: it only marks failures raised inside this registry.
class ProviderError extends Error {
  constructor(
    message: string,
    readonly cause?: unknown,
  ) {
    super(message);
    this.name = "ProviderError";
  }
}

/**
 * Registry of the available providers.
 *
 * The failover that used to live here (loop over 5 browser-side providers,
 * which meant retrying every request against Mistral, Google then OpenRouter
 * and billing each attempt) is now performed server-side by `AIProviderManager`,
 * where it is logged and guarded against pointless retries.
 */
export class AIProvider {
  private providers: Provider[];

  constructor() {
    this.providers = [new BackendAI()];
  }

  getAll(): string[] {
    return this.providers.map((p) => p.name);
  }

  async chat(input: Input): Promise<Response> {
    const name = input.providerName;

    if (name) {
      const provider = this.providers.find((p) => p.name === name);
      if (!provider) {
        throw new ProviderError(
          `Unknown provider "${name}". Available: ${this.getAll().join(", ")}`,
        );
      }
      return provider.chat(input);
    }

    return this.providers[0].chat(input);
  }
}

export { isAbortError };
