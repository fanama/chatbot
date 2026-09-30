import { randomUUID } from "crypto";
import { ChromaDBClient } from "./backend/vectoreStoreClient/chromaDBClient";
import data from './data/ragData.json'

const chromaDBClient = new ChromaDBClient("test");

function generateData() {
    // Define documents and their corresponding metadata

    // Generate unique IDs for each document
    const ids = data.map(() => randomUUID());

    // Extract documents and metadata into separate arrays
    const documents = data.map((item) => item.document);
    const metadatas = data.map((item) => item.metadata);

    return [ids, documents, metadatas];
}

(async () => {
    const question = "quele est le meilleur manga de tous les temps ?"
    console.log("Démarrage du test...");

    const [ids, documents, metadatas] = generateData();

    console.log("Données initialisées !");

    // Initialiser le client ChromaDB
    await chromaDBClient.initialize();

    // Ajouter les documents avec leurs métadonnées
    await chromaDBClient.addDocument(documents as any, ids as any, metadatas as any);

    console.log("Données insérées !");

    // Requête d'exemple
    console.log("Requête d'exemple...");
    const results = await chromaDBClient.queryCollection({ queryTexts: [question], nResults: 3 });

    // Extract and display both "document" and "perfect" response
    const perfectResponses = results.metadatas
        .flat() // Flatten the nested array
        .map((metadata: any, index: number) => {
            const document = results.documents.flat()[index]; // Match the document with the metadata
            return { document, perfect: metadata?.perfect };
        })
        .filter((item) => item.perfect); // Ensure only valid "perfect" responses are included


    const prompt = `
## Question

${question}

## Examples

${perfectResponses
            .map(
                (item) =>
                    `input: ${item.document}\noutput:{réponse parfaite :"${item.perfect}"}`
            )
            .join("\n\n")}


    `

    console.log(prompt)

    //fetch Data through metadata
    // console.log("Filtrage des data ....")
    // const filterResults = await chromaDBClient.queryCollection({ queryTexts: [question], nResults: 3, metadatas: { "anime": "One Piece" } });
    // console.log(filterResults.metadatas
    //     .flat() // Flatten the nested array
    //     .map((metadata: any, index: number) => {
    //         const document = results.documents.flat()[index]; // Match the document with the metadata
    //         return document;
    //     }))

    // Supprimer tous les documents
    await chromaDBClient.deleteAllDocuments();
    console.log("Tous les documents ont été supprimés !");
})();