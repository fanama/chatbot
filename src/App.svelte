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
  import { ROLES } from "./domain/values/users";
  import { pages } from "./domain/values/pages";

  let error: string | null = null;

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
  class="min-h-[100vh] w-full bg-gradient-to-br from-blue-800 to-white flex flex-col"
>
  {#if page != pages.HOME}
    <nav class="bg-blue-900 p-4 w-full grid grid-cols-3 md:grid-cols-9 gap-4">
      <button
        type="button"
        class="text-3xl col-span-3 font-bold text-white bg-transparent border-none cursor-pointer p-0 m-0 focus:outline-none"
        on:click={() => setPage(pages.HOME)}
        aria-label="Retour à l'accueil"
      >
        {import.meta.env.VITE_TITLE || "Démo"}
      </button>
      <button
        class={`w-full md:w-auto p-3 rounded-md cursor-pointer text-blue-600 bg-white m-1 transition duration-300 ease-in-out hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50`}
        on:click={() => setPage(pages.HOME)}>Accueil</button
      >
      <button
        class={`w-full md:w-auto p-3 rounded-md cursor-pointer text-blue-600 bg-white m-1 transition duration-300 ease-in-out hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50`}
        on:click={() => setPage(pages.CHATBOT)}>Chatbot</button
      >
      {#if $userStore?.role == ROLES.ADMIN}
        <button
          class={`w-full md:w-auto p-3 rounded-md cursor-pointer text-blue-600 bg-white m-1 transition duration-300 ease-in-out hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50`}
          on:click={() => setPage(pages.SETTINGS)}>Paramètres</button
        >
      {/if}

      {#if !error}
        {#if $userStore?.role == ROLES.ADMIN}
          <button
            class={`w-full md:w-auto p-3 rounded-md cursor-pointer text-blue-600 bg-white m-1 transition duration-300 ease-in-out hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50`}
            on:click={() => setPage(pages.DOCUMENTS)}>Documents</button
          >
        {/if}

        <button
          class={`w-full md:w-auto p-3 rounded-md cursor-pointer text-blue-600 bg-white m-1 transition duration-300 ease-in-out hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50`}
          on:click={() => setPage(pages.PDF)}>Guide Utilisateur</button
        >
        <button
          class={`w-full md:w-auto p-3 rounded-md cursor-pointer text-blue-600 bg-white m-1 transition duration-300 ease-in-out hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50`}
          on:click={() => setPage(pages.VIDEO)}>Guide Vidéo</button
        >
      {/if}
    </nav>
  {/if}

  {#if page == pages.HOME}
    <div class="flex flex-col w-full h-full">
      <Accueil chat={login} />

      <Login {login} />
    </div>
  {:else if page == pages.SETTINGS}
    <PromptManager />
  {:else if page == pages.DOCUMENTS}
    <Document />
  {:else if page == pages.PDF}
    <div class="max-h-3/4 overflow-scroll w-full">
      <PdfViewer showBorder={false} scale={1.5} url={Guide} />
    </div>
  {:else if page == pages.VIDEO}
    <div class="max-h-3/4 flex justify-center w-full">
      <video class="w-full max-w-[700px]" controls>
        <track kind="captions" />
        <source src={Video} type="video/mp4" />
      </video>
    </div>
  {:else if (page = pages.CHATBOT)}
    <Chatbot />
  {/if}
  <Footer />
</main>
