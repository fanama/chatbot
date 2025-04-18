import axios from "axios";
import type { Input, Response } from "../../domain/entities/message";

export class OllamaAI {
  name = "ollama";
  private ollamaEndpoint: string;

  constructor(ollamaEndpoint: string = "http://localhost:11434") {
    // Add constructor & default
    this.ollamaEndpoint = ollamaEndpoint;
  }

  async chat({ text, history = [] }: Input): Promise<Response> {
    try {
      console.log("ollama : gemma3:1b");
      // Build the prompt based on history (critical for Ollama's behavior)
      const prompt =
        history.map((msg) => `${msg.sender}: ${msg.text}`).join("\n") +
        "\nuser: " +
        text +
        "\n"; //System prompt needed

      const response = await axios.post(`${this.ollamaEndpoint}/api/generate`, {
        model: "gemma3:1b",
        prompt: prompt,
        stream: false, // crucial for simpler handling
      });

      if (!response.data.response) {
        throw new Error(`Ollama returned an empty response.`);
      }
      return {
        text: response.data.response,
        provider: this.name,
      };
    } catch (error) {
      console.error("Ollama API Error:", error);
      throw new Error(JSON.stringify(error));
    }
  }

  async models(): Promise<string[]> {
    try {
      const response = await axios.get(`${this.ollamaEndpoint}/api/models`);
      const models = response.data.models;
      return models; // No filtering needed; return all models
    } catch (error) {
      console.error("Error fetching models from Ollama:", error);
      return [];
    }
  }
}
