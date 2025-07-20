import axios from "axios";
import type { Input, Response } from "../../domain/entities/message";

export class OpenRouterAI {
  name = "openRouter";

  async chat({
    text,
    history = [],
    model = "google/gemma-3-27b-it:free",
  }: Input): Promise<Response> {
    try {
      console.log("openrouter", model);
      const response = await axios.post(
        "https://openrouter.ai/api/v1/chat/completions",
        {
          model,
          messages: [
            ...history.map((message) => {
              return { role: message.sender, content: message.text };
            })
          ],
        },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${import.meta.env.VITE_OPEN_ROUTER_KEY}`,
          },
        },
      );

      return {
        text: response.data.choices[0].message.content,
        provider: this.name,
      };
    } catch (err) {
      console.error(err);
      throw new Error(
        `Provider ${this.name}/${model} returned an empty response.`,
      );
    }
  }

  async models() {
    try {
      const response = await axios.get("https://openrouter.ai/api/v1/models");
      const models = response.data.data;
      console.log({ models });
      return models
        .map((m: any) => m.id)
        .filter((m: string) => m.includes("free"));
    } catch (err) {
      console.log({ err });
      return [];
    }
  }
}
