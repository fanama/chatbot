<script lang="ts">
  import Modal from "./atoms/Modal.svelte";
  import Chatbot from "./lib/Chatbot.svelte";
  import Document from "./lib/Document.svelte";
  import PromptManager from "./lib/PromptManager.svelte";
  import { Embedding } from "./infra/storage/embedding";
  import { onMount } from "svelte";
  import PdfViewer from "svelte-pdf";
  import Guide from "./assets/guide_utilisateur.pdf";

  let error: string | null = null;
  onMount(async () => {
    try {
      const store = new Embedding();
      await store.initialize(); // Ensure the store is initialized
    } catch (err) {
      error = "Failed to initialize the embedding store.";
      console.error(err);
    }
  });
</script>

<main
  class="h-screen bg-gradient-to-br from-blue-800 to-white flex flex-col items-center justify-center"
>
  <nav class="bg-blue-900 p-4 w-full">
    <div class="container mx-auto flex justify-between items-center">
      <h1 class="text-3xl font-bold text-white">
        Lalàna Velona sy Mazava, Toky ho an’ny Daholobe
      </h1>
      <div class="flex text-white justify-between gap-2">
        <Modal className="text-blue-600 bg-white" title="Settings">
          <PromptManager />
        </Modal>
        {#if !error}
          <Modal className="text-blue-600 bg-white" title="Documents">
            <Document />
          </Modal>
          <Modal className="text-blue-600 bg-white" title="Guide Utilisateur">
            <div class="max-h-3/4 overflow-scroll">
              <PdfViewer showBorder={false} scale={1.5} url={Guide} />
            </div>
          </Modal>
        {/if}
      </div>
    </div>
  </nav>
  <Chatbot />
</main>
