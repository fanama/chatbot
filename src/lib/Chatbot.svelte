<script lang="ts">
  import type { MessageEntity } from "../domain/entities/message";
  import type { PromptEntity } from "../domain/entities/prompt";
  import Displayer from "../atoms/Diplayer.svelte";
  import { onMount } from "svelte";
  import { OpenRouterAI } from "../infra/ai/openRouter";
  import PROMPT from "../../data/prompts.json";

  let prompts: PromptEntity[] = PROMPT;

  let promptSystem: string = prompts[0].prompt;
  let history: MessageEntity[] = [];
  let input: string = "";
  let loading: boolean = false;

  // const ai = new GoogleAI();
  const ai = new OpenRouterAI();

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

  onMount(() => {
    // Scroll to the bottom of the chat when new messages are added
    const chatContainer = document.getElementById("chat-container");
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  });
</script>

<h1 class="text-3xl font-bold mb-4 text-green-800">Nerd-Bot</h1>
<div
  id="chat-container"
  class="h-full w-full overflow-y-auto border border-gray-600 rounded-lg p-4 mb-4 shadow-lg bg-gray-900 text-green-400"
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
  <input
    bind:value={input}
    placeholder="Type your message..."
    class="border border-gray-600 p-3 w-full rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-800 text-green-400"
    on:keydown={(e) => {
      if (e.key === "Enter") sendMessage();
    }}
  />
  <select
    bind:value={promptSystem}
    class="border border-gray-600 p-3 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-gray-800 text-green-400"
  >
    {#each prompts as prompt}
      <option value={prompt.prompt}>{prompt.title}</option>
    {/each}
  </select>
</div>

<div class="flex flex-row justify-center w-full gap-2">
  <button
    on:click={sendMessage}
    class="flex items-center justify-center w-9/10 bg-green-800 text-gray-100 p-3 rounded-lg shadow-md hover:bg-green-900 focus:outline-none focus:ring-2 focus:ring-green-500 border border-gray-600"
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
    class="bg-red-900 text-gray-100 p-3 rounded-lg shadow-md hover:bg-red-800 focus:outline-none focus:ring-2 focus:ring-red-500 border border-gray-600 flex justify-center items-center"
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
    clear
  </button>
</div>
