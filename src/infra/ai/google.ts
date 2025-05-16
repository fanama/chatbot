import { GoogleGenAI } from "@google/genai";
import type { Input, Response } from "../../domain/entities/message";

export class GoogleAI {
  name = "google";

  async chat({
    text,
    history = [],
    model = "gemini-2.0-flash",
  }: Input): Promise<Response> {
    try {
      const ai = new GoogleGenAI({
        apiKey: `${import.meta.env.VITE_GOOGLE_KEY}`,
      });

      const config = {
        responseMimeType: "text/plain",
      };

      const contents = [
        ...history.map((message) => {
          return {
            role: message.sender !== "user" ? "model" : message.sender,
            parts: [{ text: message.text }],
          };
        }),
        {
          role: "user",
          parts: [
            {
              text: text,
            },
          ],
        },
      ];

      const response = await ai.models.generateContent({
        model,
        config,
        contents,
      });

      if (!response.text) {
        throw "error";
      }

      return {
        text: response.text,
        provider: this.name,
      };
    } catch (err) {
      console.error(err, model);
      throw new Error(
        `Provider ${this.name}/${model} returned an empty response.`,
      );
    }
  }
}
