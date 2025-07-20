import axios from "axios";
import type { Input, Response } from "../../domain/entities/message";

export class OllamaAI {
  name = "ollama";
  private ollamaEndpoint: string;

  constructor(ollamaEndpoint: string = "http://localhost:11434") {
    // Add constructor & default
    this.ollamaEndpoint = ollamaEndpoint;
  }

  async chat({ text, history = [],stream=(chunk)=>console.log({chunk}) }: Input): Promise<Response> {
    let result = "";

    try {
      const model = "gemma3n"
      const url = `${this.ollamaEndpoint}/api/generate`
      // Build the prompt based on history (critical for Ollama's behavior)
      const prompt =
        history.map((msg) => `${msg.sender}: ${msg.text}`).join("\n"); //System prompt needed
      
      const data = {
        model,
        prompt: prompt,
      }
      

      const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok || !response.body) {
      console.log(response)
      throw new Error(`Network response was not ok : ${url} ${JSON.stringify(data,null,2)}`);
    }

    const reader = response.body.getReader();
    await this.readStream(reader, (text:string)=> {
      stream(text)
      result+=text
    });

    return { text: result,provider:this.name };
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

  private  async  readStream(
    reader: ReadableStreamDefaultReader<Uint8Array>,
    stream: (text: string) => void = (text: string) => console.log({ text }),
  ) {
    const decoder = new TextDecoder();
    let done = false;

    while (!done) {
      const { value, done: streamDone } = await reader.read();
      done = streamDone;
      if (value) {
        const chunkStr = decoder.decode(value);
        const chunk = JSON.parse(chunkStr);
        stream(chunk.response);
      }
    }
  }
}

