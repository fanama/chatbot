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
  } from "./store";
  import { LocalStorage } from "../infra/storage/localStorage";

  import VoiceInput from "../atoms/VoiceInput.svelte";

  const historyStorage = new LocalStorage<MessageEntity>("history", []);

  $: prompts = $promptStore;

  $: promptSystem = $promptSystemStore;
  $: provider = $providerStore;

  let history: MessageEntity[] = historyStorage.getAll();
  let input: string = "";
  let loading: boolean = false;

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

  const sendMessage = async () => {
    if (input.trim() === "") return;

    // Add user message to the chat
    history = [...history, { sender: "user", text: input }];

    // Clear the input field
    const text = input;
    input = "";

    // Set loading state to true
    loading = true;

    // Make API call to Google Generative AI
    const response = await ai.chat({
      text,
      history: [{ sender: "system", text: promptSystem }, ...history],
      providerName: provider,
    });

    // Add AI response to the chat
    history = [
      ...history,
      {
        sender: "model",
        text: response.text,
        provider: response.provider,
      },
    ];

    // Set loading state to false
    loading = false;
  };

  onMount(async () => {
    try {
      promptSystem = prompts[0].text;
      const providers = ai.getAll();
      const provider = providers[0];
      providersStore.set(providers);
      providerStore.set(provider);
    } catch (err) {}
  });
</script>

<div
  bind:this={messageContainer}
  class="h-full w-full md:w-3/4 p-2 overflow-y-auto rounded-b-lg p-4 mb-4 text-blue-200 font-mono"
>
  {#each history as message}
    <Displayer {message} />
  {/each}
  {#if loading}
    <div class="flex justify-center items-center">
      <span class="visually-hidden">Loading...</span>
    </div>
  {/if}
</div>
<div class="flex flex-row justify-end p-2 gap-6 w-full">
  <button
    on:click={() => {
      history = [];
    }}
    class=" bg-red-700 cursor-pointer text-gray-100 p-3 rounded-lg shadow-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 border border-red-600 flex justify-center items-center font-mono"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="h-5 w-5"
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
<div class="flex flex-row w-full items-stretch p-6">
  <textarea
    bind:value={input}
    placeholder="Type your message..."
    class="p-3 flex-grow rounded-l-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gradient-to-br from-gray-200 to-white text-blue-600 font-mono"
    on:keydown={(e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault(); // Empêche le comportement par défaut (aller à la ligne)
        sendMessage();
      }
    }}
  ></textarea>

  <VoiceInput bind:transcript={input} />
  <button
    on:click={sendMessage}
    class="flex items-center justify-center bg-blue-600 text-gray-100 p-3 rounded-r-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-blue-600 font-mono"
  >
    <svg
      class="w-6 h-6 mr-2"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
      ></path>
    </svg>
    Send
  </button>
</div>
