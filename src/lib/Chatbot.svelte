<script lang="ts">
  import type { MessageEntity } from "../domain/entities/message";
  import Displayer from "../atoms/Diplayer.svelte";
  import { onMount } from "svelte";
  import { AIProvider } from "../infra/ai/aiProvider";
  import {
    promptStore,
    promptSystemStore,
    providersStore,
    providerStore,
    language,
  } from "./store";
  import { LocalStorage } from "../infra/storage/localStorage";

  import VoiceInput from "../atoms/VoiceInput.svelte";
  import { Embedding } from "../infra/storage/embedding";
  import BasicDiplayer from "../atoms/BasicDiplayer.svelte";
  import Uploader from "../atoms/Uploader.svelte";
  import Modal from "../atoms/Modal.svelte";

  const historyStorage = new LocalStorage<MessageEntity>("history", []);

  let store: Embedding | null = null;
  let useStore = false; // Nouvelle variable pour la checkbox

  let history: MessageEntity[] = historyStorage.getAll();
  let input: string = "";
  let loading: boolean = false;
  let streamContent = "";
  let fileName: string = "";

  let chunks: string[] = [];

  let messageContainer: HTMLDivElement;

  const ai = new AIProvider();

  function scrollBottom() {
    if (messageContainer) {
      messageContainer.scrollTo({
        top: messageContainer.scrollHeight,
        behavior: "smooth",
      });
    }
  }

  $: if (history) {
    historyStorage.save(history);
    setTimeout(scrollBottom, 0);
  }

  const getStoreResults = async (query: string) => {
    if (!store || !useStore) return { documents: [], metadatas: [] };
    try {
      const storeResult = await store.search(query);
      return {
        documents: storeResult.documents,
        metadatas: [...new Set(storeResult.metadatas)],
      };
    } catch (e) {
      console.log("no DB");
      return { documents: [], metadatas: [] };
    }
  };

  const insertToStore = async (input: string, response: string) => {
    if (!store) return { documents: [], metadatas: [] };
    try {
      await store.add(`input:${input}=>output:${response}`, {
        input,
        response,
      });
      return {};
    } catch (e) {
      console.log("no DB");
      return { documents: [], metadatas: [] };
    }
  };

  const sendMessage = async () => {
    if (input.trim() === "") return;

    // Add user message to the chat

    const text = input;

    // Set loading state to true
    loading = true;

    let documents: string[] = [];
    let metadatas: string[] = [];

    const { documents: initialDocuments, metadatas: initialMetadatas } =
      await getStoreResults(text);
    documents = initialDocuments;
    metadatas = initialMetadatas;

    input = "";
    history = [...history, { sender: "user", text: text }];

    // Limiter l'historique à 5 derniers messages
    const recentHistory = history.slice(-5);

    // Make API call to Google Generative AI
    const response = await ai.chat({
      text,
      useVectorestore: useStore,
      history: [
        { sender: "system", text: $promptSystemStore },
        ...documents.map((text) => {
          return { sender: "system", text };
        }),
        ...metadatas.map((text) => {
          return { sender: "system", text };
        }),
        ...chunks.map((chunk) => {
          return { sender: "system", text: chunk };
        }),
        { sender: "system", text: `you will respond in ${$language}` },
        ...recentHistory,
      ],
      providerName: $providerStore,
      stream: (text) => (streamContent += text),
    });

    // Add AI response to the chat
    history = [
      ...history,
      {
        sender: "system",
        text: response.text,
        provider: response.provider,
        context: [...metadatas, ...documents],
        insertToStore: () => {
          insertToStore(text, response.text);
          alert("ajouté !");
        },
      },
    ];

    // Set loading state to false
    loading = false;
    streamContent = "";
  };

  onMount(async () => {
    try {
      if ($promptSystemStore == "" && $promptStore.length > 0) {
        promptSystemStore.set($promptStore[0].text);
      }
      const providers = ai.getAll();

      providersStore.set(providers);
      if (!$providerStore) {
        const provider = providers[0];
        providerStore.set(provider);
      }

      store = new Embedding();
      await store.initialize(); // Ensure the store is initialized
    } catch (err) {}
  });
</script>

<div class="flex flex-col h-full w-full overflow-y-scroll p-2">
  <!-- Message Container -->
  <div
    bind:this={messageContainer}
    class="min-h-[60vh] w-full p-4 mb-4 text-blue-200 font-mono overflow-y-auto rounded-b-lg"
  >
    <!-- Message History -->
    {#each history as message}
      <Displayer {message} />
    {/each}

    <!-- Loading Indicator -->
    {#if loading}
      <BasicDiplayer message={streamContent} />
    {/if}
  </div>

  <!-- Controls Section -->
  <div class="flex flex-col gap-2 w-full">
    <!-- Clear History Button -->
    <div class="flex flex-row justify-end p-2 gap-2">
      <button
        on:click={() => {
          history = [];
        }}
        class="bg-red-700 cursor-pointer text-gray-100 p-2 rounded-lg shadow-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 border border-red-600 flex justify-center items-center font-mono text-xs"
        title="Clear conversation history"
      >
        <svg
          xmlns="http://www.w3.org/2009/svg"
          class="h-4 w-4"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fill-rule="evenodd"
            d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
            clip-rule="evenodd"
          />
        </svg>
      </button>
    </div>

    <!-- Input Controls -->
    <div class="w-full p-2 flex flex-col gap-3">
      <!-- File Upload + Options -->
      <div class="flex items-center gap-4">
        <Modal
          title={fileName || "load file"}
          className="bg-blue-500 text-white max-w-32 overflow-hidden text-ellipsis whitespace-nowrap text-xs"
        >
          <Uploader bind:fileName bind:chunks hide={true} />
        </Modal>

        {#if store}
          <label class="flex items-center gap-2 text-xs text-white">
            <input type="checkbox" bind:checked={useStore} />
            <span>Recherche documentaire</span>
          </label>
        {/if}
      </div>

      <!-- Message Input -->
      <div class="flex items-stretch w-full">
        <textarea
          bind:value={input}
          placeholder="Type your message..."
          class="
        flex-grow p-2 rounded-l-lg bg-gradient-to-br from-gray-200 to-white
        text-blue-600 font-mono text-sm shadow-sm
        focus:outline-none focus:ring-2 focus:ring-blue-500
      "
          on:keydown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
          aria-label="Message input"
        ></textarea>

        <VoiceInput bind:transcript={input} />

        <!-- Send Button -->
        <button
          on:click={sendMessage}
          title="Send message"
          class="
        p-2 rounded-r-lg bg-blue-600 text-gray-100
        shadow-md border border-blue-600 font-mono text-xs
        hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500
        flex items-center justify-center
      "
        >
          <svg
            class="w-4 h-4 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</div>
