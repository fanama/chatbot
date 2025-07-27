<script lang="ts">
  import Modal from "./atoms/Modal.svelte";
  import Chatbot from "./lib/Chatbot.svelte";
  import Document from "./lib/Document.svelte";
  import PromptManager from "./lib/PromptManager.svelte";
  import { Embedding } from "./infra/storage/embedding";
  import { onMount } from "svelte";
  import PdfViewer from "svelte-pdf";
  import Guide from "./assets/guide_utilisateur.pdf";
  import Video from "./assets/GuideVideo.mp4";

  let error: string | null = null;
  let page = 0;
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
  class="h-screen bg-gradient-to-br from-blue-800 to-white flex flex-col items-center"
>
  <nav class="bg-blue-900 p-4 w-full">
    <div class="container mx-auto flex justify-between items-center">
      <button
        type="button"
        class="text-3xl font-bold text-white bg-transparent border-none cursor-pointer p-0 m-0 focus:outline-none"
        on:click={() => (page = 0)}
        aria-label="Retour à l'accueil"
      >
        {import.meta.env.TITLE || "Demo"}
      </button>
      <div class="flex text-white justify-between gap-2">
        <button
          class={`w-full p-2 rounded-xs cursor-pointer text-blue-600 bg-white`}
          on:click={() => (page = 0)}>Chatbot</button
        >
        <button
          class={`w-full p-2 rounded-xs cursor-pointer text-blue-600 bg-white`}
          on:click={() => (page = 1)}>Settings</button
        >
        {#if !error}
          <button
            class={`w-full p-2 rounded-xs cursor-pointer text-blue-600 bg-white`}
            on:click={() => (page = 2)}>Documents</button
          >
          <button
            class={`w-full p-2 rounded-xs cursor-pointer text-blue-600 bg-white`}
            on:click={() => (page = 3)}>Guide Utilisateur</button
          >
          <button
            class={`w-full p-2 rounded-xs cursor-pointer text-blue-600 bg-white`}
            on:click={() => (page = 4)}>Guide Vidéo</button
          >
        {/if}
      </div>
    </div>
  </nav>
  {#if page == 1}
    <PromptManager />
  {:else if page == 2}
    <Document />
  {:else if page == 3}
    <div class="max-h-3/4 overflow-scroll">
      <PdfViewer showBorder={false} scale={1.5} url={Guide} />
    </div>
  {:else if page == 4}
    <div class="max-h-3/4 flex justify-center">
      <video class="w-[700px]" controls>
        <track kind="captions" />
        <source src={Video} type="video/mp4" />
      </video>
    </div>
  {:else}
    <Chatbot />
  {/if}
</main>
