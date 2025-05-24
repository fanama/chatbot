import axios from "axios";
import type { Input, Response } from "../../domain/entities/message";

export class MistralAI {
  name = "mistral";

  async chat({
    text,
    history = [],
    model = "mistral-small-latest",
  }: Input): Promise<Response> {
    try {
      console.log("mistral", model);
      const response = await axios.post(
        "https://api.mistral.ai/v1/chat/completions",
        {
          model: "mistral-small-latest",
          temperature: 0,
          messages: [
            ...history.map((message) => {
              return {
                role: message.sender !== "user" ? "assistant" : message.sender,
                content: message.text,
              };
            }),
            {
              role: "user",
              content: text,
            },
          ],
        },
        {
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: `Bearer ${import.meta.env.VITE_MISTRAL_KEY}`,
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
}
