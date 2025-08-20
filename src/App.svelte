<script lang="ts">
  import Chatbot from "./lib/Chatbot.svelte";
  import Document from "./lib/Document.svelte";
  import PromptManager from "./lib/PromptManager.svelte";
  import { Embedding } from "./infra/storage/embedding";
  import { onMount } from "svelte";
  import PdfViewer from "svelte-pdf";
  import Guide from "./assets/guide_utilisateur.pdf";
  import Video from "./assets/GuideVideo.mp4";
  import Login from "./lib/Login.svelte";
  import Accueil from "./lib/Accueil.svelte";

  import { LocalStorage } from "./infra/storage/localStorage";
  import { userStore } from "./lib/store";
  import type { UserEntity } from "./domain/entities/user";
  import Footer from "./atoms/Footer.svelte";

  let error: string | null = null;

  const ROLES = {
    ADMIN: "ADMIN",
    USER: "USER",
  };
  const pages = {
    HOME: "home",
    CHATBOT: "chatbot",
    SETTINGS: "settings",
    DOCUMENTS: "documents",
    VIDEO: "video",
    PDF: "pdf",
  };

  const pageStorage = new LocalStorage<string>("page", [pages.HOME]);
  const userStorage = new LocalStorage<UserEntity>("users", []);

  $: page = pageStorage.getAll()[0];

  const setPage = (p: string) => {
    page = p;
    pageStorage.save([p]);
  };

  onMount(async () => {
    try {
      page = pageStorage.getAll()[0];
      const users = userStorage.getAll();
      userStore.set(users[0] || { name: "user", role: "USER" });

      const store = new Embedding();

      await store.initialize(); // Ensure the store is initialized
    } catch (err) {
      error = "Failed to initialize the embedding store.";
      console.error(err);
    }
  });

  const login = () => {
    setPage(pages.CHATBOT);
  };
</script>

<main
  class="h-screen bg-gradient-to-br from-blue-800 to-white flex flex-col items-center"
>
  {#if page != pages.HOME}
    <nav class="bg-blue-900 p-4 w-full">
      <div class="container mx-auto flex justify-between items-center">
        <button
          type="button"
          class="text-3xl font-bold text-white bg-transparent border-none cursor-pointer p-0 m-0 focus:outline-none"
          on:click={() => setPage(pages.HOME)}
          aria-label="Retour à l'accueil"
        >
          {import.meta.env.VITE_TITLE || "Demo"}
        </button>
        <div class="flex text-white justify-between gap-2">
          <button
            class={`w-full p-2 rounded-xs cursor-pointer text-blue-600 bg-white`}
            on:click={() => setPage(pages.CHATBOT)}>Chatbot</button
          >
          {#if $userStore?.role == ROLES.ADMIN}
            <button
              class={`w-full p-2 rounded-xs cursor-pointer text-blue-600 bg-white`}
              on:click={() => setPage(pages.SETTINGS)}>Settings</button
            >
          {/if}

          {#if !error}
            <button
              class={`w-full p-2 rounded-xs cursor-pointer text-blue-600 bg-white`}
              on:click={() => setPage(pages.DOCUMENTS)}>Documents</button
            >
            <button
              class={`w-full p-2 rounded-xs cursor-pointer text-blue-600 bg-white`}
              on:click={() => setPage(pages.PDF)}>Guide Utilisateur</button
            >
            <button
              class={`w-full p-2 rounded-xs cursor-pointer text-blue-600 bg-white`}
              on:click={() => setPage(pages.VIDEO)}>Guide Vidéo</button
            >
          {/if}
        </div>
      </div>
    </nav>
  {/if}

  {#if page == pages.HOME}
    <div class="flex flex-row w-full h-full">
      <Login {login} />

      <Accueil chat={login} />
    </div>
  {:else if page == pages.SETTINGS}
    <PromptManager />
  {:else if page == pages.DOCUMENTS}
    <Document />
  {:else if page == pages.PDF}
    <div class="max-h-3/4 overflow-scroll">
      <PdfViewer showBorder={false} scale={1.5} url={Guide} />
    </div>
  {:else if page == pages.VIDEO}
    <div class="max-h-3/4 flex justify-center">
      <video class="w-[700px]" controls>
        <track kind="captions" />
        <source src={Video} type="video/mp4" />
      </video>
    </div>
  {:else if (page = pages.CHATBOT)}
    <Chatbot />
  {/if}

  <Footer />
</main>
