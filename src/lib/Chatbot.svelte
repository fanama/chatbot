<script lang="ts">
  import type { MessageEntity } from "../domain/entities/message";
  import Displayer from "../atoms/Diplayer.svelte";
  import { onMount } from "svelte";
  import { OpenRouterAI } from "../infra/ai/openRouter";
  import { promptStore } from "./store";
  import { LocalStorage } from "../infra/storage/localStorage";

  const historyStorage = new LocalStorage<MessageEntity>("history", []);

  $: prompts = $promptStore;

  let promptSystem = "";
  let model = "google/gemma-3-12b-it:free";
  let models: string[] = [];

  let history: MessageEntity[] = historyStorage.getAll();
  let input: string = "";
  let loading: boolean = false;

  // const ai = new GoogleAI();
  const ai = new OpenRouterAI();

  $: if (history) {
    historyStorage.save(history);
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
      model,
    });

    // Add AI response to the chat
    history = [
      ...history,
      {
        sender: "model",
        text: response,
      },
    ];

    // Set loading state to false
    loading = false;
  };

  onMount(async () => {
    try {
      promptSystem = prompts[0].text;
      models = await ai.models();
    } catch (err) {}
    // Scroll to the bottom of the chat when new messages are added
    const chatContainer = document.getElementById("chat-container");
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  });
</script>

<div
  id="chat-container"
  class="h-full w-full overflow-y-auto border border-green-600 rounded-lg p-4 mb-4 shadow-lg bg-green-900 text-green-300 font-mono"
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
<div class="flex flex-row w-full gap-2 mb-4">
  <textarea
    bind:value={input}
    placeholder="Type your message..."
    class="border border-green-600 p-3 w-3/4 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-green-800 text-green-300 font-mono text-white"
    on:keydown={(e) => {
      if (e.key === "Enter") sendMessage();
    }}
  ></textarea>
  <div class="flex flex-col gap-2 w-1/3">
    <select
      bind:value={model}
      class="w-full border border-green-600 p-3 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-green-800 text-green-300 font-mono"
    >
      {#each models as model}
        <option value={model}>{model}</option>
      {/each}
    </select>
    <select
      bind:value={promptSystem}
      class="w-full border border-green-600 p-3 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-green-800 text-green-300 font-mono"
    >
      {#each prompts as prompt}
        <option value={prompt.text}>{prompt.title}</option>
      {/each}
    </select>
  </div>
</div>

<div class="flex flex-row justify-center w-full gap-2">
  <button
    on:click={sendMessage}
    class="flex items-center justify-center w-9/10 bg-green-700 text-gray-100 p-3 rounded-lg shadow-md hover:bg-green-800 focus:outline-none focus:ring-2 focus:ring-green-500 border border-green-600 font-mono"
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

  <button
    on:click={() => {
      history = [];
    }}
    class="bg-red-800 text-gray-100 p-3 rounded-lg shadow-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 border border-red-600 flex justify-center items-center font-mono"
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
    Clear
  </button>
</div>
