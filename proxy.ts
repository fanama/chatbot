import express, { Request, Response } from "express";
import { ChromaClient, Collection, IncludeEnum } from "chromadb";
import cors from "cors"; // Import the cors package
import { createProxyMiddleware } from "http-proxy-middleware";
import { ChromaDBClient } from "./backend/vectoreStoreClient/chromaDBClient";

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

const chromaDBClient = new ChromaDBClient("my_collection");

app.use(express.static("dist"));
app.use(express.static("src"));

app.get("/", (_req, res) => {
  res.sendFile("./dist/index.html");
});

app.get("/assets/guide_utilisateur.pdf", (_req, res) => {
  res.sendFile("./src/assets/guide_utilisateur.pdf");
});

app.post("/initialize", async (_req: Request, res: Response) => {
  try {
    await chromaDBClient.initialize();
    res.status(200).send("Collection initialized");
  } catch (error) {
    res.status(500).send("Error initializing collection");
  }
});

app.post("/documents", async (req: Request, res: Response) => {
  try {
    const { documents, ids, metadatas } = req.body;
    await chromaDBClient.addDocument(documents, ids, metadatas);
    res.status(200).send("Documents added");
  } catch (error) {
    console.error(error);
    res.status(500).send("Error adding documents");
  }
});

app.post("/query", async (req: Request, res: Response) => {
  try {
    const { queryTexts, nResults, include, metadatas } = req.body;
    const results = await chromaDBClient.queryCollection({
      queryTexts,
      nResults,
      include,
      metadatas
    });
    res.status(200).json(results);
  } catch (error) {
    console.error(error)
    res.status(500).send("Error querying collection");
  }
});

app.get("/documents", async (req: Request, res: Response) => {
  try {
    const { ids, include, metadatas } = req.query;
    const parsedMetadatas = metadatas ? JSON.parse(metadatas as string) : undefined;

    const results = await chromaDBClient.getDocument(
      ids as string[],
      include as IncludeEnum[],
      parsedMetadatas
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
    const { ids, include, metadatas } = req.query;
    const parsedMetadatas = metadatas ? JSON.parse(metadatas as string) : undefined;

    await chromaDBClient.deleteAllDocuments(parsedMetadatas)

    res.status(200).send("success");
  } catch (error) {
    console.error(error);
    res.status(500).send("Error deleting documents");
  }
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
