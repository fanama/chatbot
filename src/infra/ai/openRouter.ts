import axios from "axios";
import type { MessageEntity } from "../../domain/entities/message";

interface Props {
  text: string;
  history?: MessageEntity[];
  model?: string;
}

export class OpenRouterAI {
  async chat({
    text,
    history = [],
    model = "meta-llama/llama-4-maverick:free",
  }: Props): Promise<string> {
    try {
      const response = await axios.post(
        "https://openrouter.ai/api/v1/chat/completions",
        {
          model,
          messages: [
            ...history.map((message) => {
              return { role: message.sender, content: message.text };
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
            Authorization: `Bearer ${import.meta.env.VITE_OPEN_ROUTER_KEY}`,
          },
        },
      );

      return response.data.choices[0].message.content;
    } catch (err) {
      console.error(err);
      return "error";
    }
  }
}
