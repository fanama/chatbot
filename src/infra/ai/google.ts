import axios from "axios";
import type { MessageEntity } from "../../domain/entities/message";

interface Props {
  text: string;
  history?: MessageEntity[];
  model?: string;
}

export class GoogleAI {
  async chat({
    text,
    history = [],
    model = "gemini-2.0-flash",
  }: Props): Promise<string> {
    try {
      const response = await axios.post(
        `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${import.meta.env.VITE_GOOGLE_API_KEY}`,
        {
          contents: [
            history.map((message) => {
              return { role: message.sender, parts: [{ text: message.text }] };
            }),
            {
              role: "user",
              parts: [{ text }],
            },
          ],
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        },
      );

      return response.data.candidates[0].content.parts[0].text;
    } catch (err) {
      console.error(err);
      return "error";
    }
  }
}
