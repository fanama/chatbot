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

<h1 class="text-2xl font-bold mb-4">Chatbot</h1>
<div
  id="chat-container"
  class="h-full w-full overflow-y-auto border border-gray-300 rounded-lg p-4 mb-4 shadow-lg bg-white"
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
    class="border border-gray-300 p-3 w-full rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
    on:keydown={(e) => {
      if (e.key === "Enter") sendMessage();
    }}
  />
  <select
    bind:value={promptSystem}
    class="border border-gray-300 p-3 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
  >
    {#each prompts as prompt}
      <option value={prompt.prompt}>{prompt.title}</option>
    {/each}
  </select>
</div>
<div class="flex flex-row w-full gap-2">
  <button
    on:click={sendMessage}
    class="w-full bg-blue-500 text-white p-3 rounded-lg shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
  >
    Send
  </button>
  <button
    on:click={() => {
      history = [];
    }}
    class="w-full bg-red-500 text-white p-3 rounded-lg shadow-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500"
  >
    Clear
  </button>
</div>
