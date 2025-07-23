import { ChromaClient, Collection, IncludeEnum } from "chromadb";

export class ChromaDBClient {
    private client: ChromaClient;
    private collection: Collection;

    constructor(
        private collectionName: string = "test",
        private chromaServerUrl: string = "http://localhost:8000",
    ) {
        this.client = new ChromaClient({ path: this.chromaServerUrl });
        this.initialize()
    }

    async initialize(): Promise<void> {
        this.collection = await this.client.getOrCreateCollection({
            name: this.collectionName,
        });
    }

    async addDocument(documents: string[], ids: string[], metadatas: { [x: string]: string | number | boolean; }[]): Promise<void> {
        await this.collection.add({ documents, ids, metadatas });
    }

    async queryCollection(
        queryTexts: string[],
        nResults: number = 10,
        include?: IncludeEnum[],
    ) {
        return await this.collection.query({ queryTexts, nResults, include });
    }

    async getDocument(ids: string[], include?: IncludeEnum[]): Promise<any> {
        const results = await this.collection.get({ ids, include });
        return results.documents;
    }

    async getFullDocument(ids?: string[], include?: IncludeEnum[]): Promise<any> {
        const results = await this.collection.get({ ids, include });
        return [results.ids, results.documents, results.metadatas];
    }

    async getDocumentId(ids: string | string[], include?: IncludeEnum[]): Promise<any> {
        const results = await this.collection.get({ ids, include });
        return results.ids;
    }

    async updateDocument(ids: string[], documents: string[]): Promise<void> {
        await this.collection.update({ ids, documents });
    }

    async deleteDocument(ids: string[]): Promise<void> {
        await this.collection.delete({ ids });
    }

    async deleteAllDocuments(): Promise<void> {
        const newIds = await this.getDocumentId("")
        await this.deleteDocument(newIds);

    }
}