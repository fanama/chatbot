import express, { Request, Response } from "express";
import { ChromaClient, Collection, IncludeEnum } from "chromadb";
import cors from "cors"; // Import the cors package
import { createProxyMiddleware } from "http-proxy-middleware";

const app = express();
const port = 3000;

// Proxy middleware options
const options = {
  target: "http://localhost:3001/upload", // Target the Python server
  changeOrigin: true,
  pathRewrite: {
    "^/upload": "/upload", // Pass through the same path
  },
};

const uploadProxy = createProxyMiddleware(options);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(cors());

// Use the proxy middleware
app.use("/upload", uploadProxy);

class ChromaDBClient {
  private client: ChromaClient;
  private collection: Collection;

  constructor(
    private collectionName: string = "test",
    private chromaServerUrl: string = "http://localhost:8000",
  ) {
    this.client = new ChromaClient({ path: this.chromaServerUrl });
  }

  async initialize(): Promise<void> {
    this.collection = await this.client.getOrCreateCollection({
      name: this.collectionName,
    });
  }

  async addDocument(documents: string[], ids: string[]): Promise<void> {
    await this.collection.add({ documents, ids });
  }

  async queryCollection(
    queryTexts: string[],
    nResults: number = 10,
    include?: IncludeEnum[],
  ): Promise<any> {
    return await this.collection.query({ queryTexts, nResults, include });
  }

  async getDocument(ids: string[], include?: IncludeEnum[]): Promise<any> {
    const results = await this.collection.get({ ids, include });
    return results.documents;
  }

  async updateDocument(ids: string[], documents: string[]): Promise<void> {
    await this.collection.update({ ids, documents });
  }

  async deleteDocument(ids: string[]): Promise<void> {
    await this.collection.delete({ ids });
  }

  async deleteAllDocuments(): Promise<void> {
    await this.collection.delete({ ids: ["*"] });
  }
}

const chromaDBClient = new ChromaDBClient("my_collection");

app.use(express.static("dist"));

app.get("/", (_req, res) => {
  res.sendFile("./dist/index.html");
});

app.post("/initialize", async (req: Request, res: Response) => {
  try {
    await chromaDBClient.initialize();
    res.status(200).send("Collection initialized");
  } catch (error) {
    res.status(500).send("Error initializing collection");
  }
});

app.post("/documents", async (req: Request, res: Response) => {
  try {
    const { documents, ids } = req.body;
    await chromaDBClient.addDocument(documents, ids);
    res.status(200).send("Documents added");
  } catch (error) {
    console.error(error);
    res.status(500).send("Error adding documents");
  }
});

app.post("/query", async (req: Request, res: Response) => {
  try {
    const { queryTexts, nResults, include } = req.body;
    const results = await chromaDBClient.queryCollection(
      queryTexts,
      nResults,
      include,
    );
    res.status(200).json(results);
  } catch (error) {
    res.status(500).send("Error querying collection");
  }
});

app.post("/upload", async (req: Request, res: Response) => {
  try {
    res.status(200).send("success");
  } catch (error) {
    res.status(500).send("Error upload");
  }
});

app.get("/documents", async (req: Request, res: Response) => {
  try {
    const { ids, include } = req.query;
    const results = await chromaDBClient.getDocument(
      ids as string[],
      include as IncludeEnum[],
    );
    res.status(200).json(results);
  } catch (error) {
    console.log(error);
    res.status(500).send("Error getting documents");
  }
});

app.put("/documents", async (req: Request, res: Response) => {
  try {
    const { ids, documents } = req.body;
    await chromaDBClient.updateDocument(ids, documents);
    res.status(200).send("Documents updated");
  } catch (error) {
    res.status(500).send("Error updating documents");
  }
});

app.delete("/documents", async (req: Request, res: Response) => {
  try {
    const { ids } = req.body;
    await chromaDBClient.deleteDocument(ids);
    res.status(200).send("Documents deleted");
  } catch (error) {
    res.status(500).send("Error deleting documents");
  }
});

app.delete("/empty-documents", async (req: Request, res: Response) => {
  try {
    await chromaDBClient.deleteAllDocuments();
    res.status(200).send("All Documents deleted");
  } catch (error) {
    console.error(error);
    res.status(500).send("Error deleting documents");
  }
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
