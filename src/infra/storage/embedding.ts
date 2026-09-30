import axios from "axios";
import { BACKEND_URL } from "../ai/config";

const app = import.meta.env.VITE_TITLE || "demo";
const url = BACKEND_URL;

/** Stable unique id. `Math.random()` over 1000 values collided and silently
 * overwrote documents in the collection. */
const newId = (): string =>
  typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `id-${Date.now()}-${Math.trunc(Math.random() * 1e9)}`;

export class Embedding {
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
        ids: [newId()],
        metadatas: [{ ...metadata, app }],
      });
      if (response.status !== 200) {
        throw new Error("Failed to add document");
      }
    } catch (error) {
      console.error("Add error:", error);
      throw error;
    }
  }

  async search(
    text: string,
    metadatas?: object,
  ): Promise<{ documents: string[]; metadatas: string[] }> {
    try {
      const response = await axios.post(url + "/query", {
        queryTexts: [text],
        nResults: 10,
        metadatas: { ...metadatas, app },
      });
      if (response.status !== 200) {
        throw new Error("Failed to search documents");
      }

      const metaResults = response.data.metadatas?.[0] ?? [];
      return {
        documents: response.data.documents?.[0] ?? [],
        metadatas: metaResults
          .map((value: Record<string, unknown>) => Object.values(value))
          .flat()
          .map((value: unknown) => String(value)),
      };
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
