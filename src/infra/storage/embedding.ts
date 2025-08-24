import axios from "axios"; // You'll need to install axios or use another HTTP client

const app = import.meta.env.VITE_TITLE || "demo"
const url = import.meta.env.VITE_URL || ""


export class Embedding {
  constructor() {
    // No need to initialize the collection here
  }

  async initialize() {
    try {
      const response = await axios.post(url + "/initialize");
      if (response.status !== 200) {
        throw new Error("Failed to initialize collection");
      }
    } catch (error) {
      console.error("Initialize error:", error);
      throw error;
    }
  }

  async add(text: string, metadata?: object) {
    try {
      const response = await axios.post(url + "/documents", {
        documents: [text],
        ids: [`id-${Math.trunc(Math.random() * 1000)}`],
        metadatas: [{ ...metadata, app }]
      });
      if (response.status !== 200) {
        throw new Error("Failed to add document");
      }
    } catch (error) {
      console.error("Add error:", error);
      throw error;
    }
  }

  async search(text: string, metadatas?: object): Promise<{ documents: string[], metadatas: string[] }> {
    try {
      const response = await axios.post(url + "/query", {
        queryTexts: [text],
        nResults: 10,
        metadatas: { ...metadatas, app }
      });
      if (response.status !== 200) {
        throw new Error("Failed to search documents");
      }

      const metaResults: object[] = response.data.metadatas[0]
      return { documents: response.data.documents[0], metadatas: metaResults.map(value => Object.values(value)).flat() };
    } catch (error) {
      console.error("Search error:", error);
      throw error;
    }
  }

  async remove(id: string) {
    try {
      const response = await axios.delete(url + "/documents", {
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
