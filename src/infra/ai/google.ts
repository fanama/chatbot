import axios from "axios";
import type { Input } from "../../domain/entities/message";

export class GoogleAI {
  name = "google";
  async chat({
    text,
    history = [],
    model = "gemini-2.0-flash",
  }: Input): Promise<string> {
    try {
      const response = await axios.post(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${import.meta.env.VITE_GOOGLE_API_KEY}`,
        {
          contents: [
            history.map((message) => {
              return {
                role: message.sender !== "user" ? "model" : message.sender,
                parts: [{ text: message.text }],
              };
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
      console.error(err, model);
      throw new Error(
        `Provider ${this.name}/${model} returned an empty response.`,
      );
    }
  }
}
