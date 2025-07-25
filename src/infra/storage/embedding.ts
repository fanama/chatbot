import axios from "axios"; // You'll need to install axios or use another HTTP client

export class Embedding {
  constructor() {
    // No need to initialize the collection here
  }

  async initialize() {
    try {
      const response = await axios.post("/initialize");
      if (response.status !== 200) {
        throw new Error("Failed to initialize collection");
      }
    } catch (error) {
      console.error("Initialize error:", error);
      throw error;
    }
  }

  async add(text: string, metadata?: Record<string, object>) {
    try {
      const response = await axios.post("/documents", {
        documents: [text],
        ids: [`id-${Math.trunc(Math.random() * 1000)}`],
        metadatas: [metadata]
      });
      if (response.status !== 200) {
        throw new Error("Failed to add document");
      }
    } catch (error) {
      console.error("Add error:", error);
      throw error;
    }
  }

  async search(text: string, metadatas?: object): Promise<string[]> {
    try {
      const response = await axios.post("/query", {
        queryTexts: [text],
        nResults: 10,
        metadatas
      });
      if (response.status !== 200) {
        throw new Error("Failed to search documents");
      }
      return response.data.documents[0];
    } catch (error) {
      console.error("Search error:", error);
      throw error;
    }
  }

  async remove(id: string) {
    try {
      const response = await axios.delete("/documents", {
        data: { ids: [id] },
      });
      if (response.status !== 200) {
        throw new Error("Failed to delete document");
      }
    } catch (error) {
      console.error("Remove error:", error);
      throw error;
    }
  }
}
