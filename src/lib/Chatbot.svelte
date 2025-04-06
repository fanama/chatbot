<script lang="ts">
  import type { MessageEntity } from "../domain/entities/message";
  import Displayer from "../atoms/Diplayer.svelte";
  import { onMount } from "svelte";
  //import { GoogleAI } from "../infra/ai/google";
  import { OpenRouterAI } from "../infra/ai/openRouter";

  let messages: MessageEntity[] = [];
  let input: string = "";
  let loading: boolean = false;

  // const ai = new GoogleAI();
  const ai = new OpenRouterAI();

  const sendMessage = async () => {
    if (input.trim() === "") return;

    // Add user message to the chat
    messages = [...messages, { sender: "user", text: input }];

    // Clear the input field
    const text = input;
    input = "";

    // Set loading state to true
    loading = true;

    // Make API call to Google Generative AI
    const response = await ai.chat({ text, history: messages });

    // Add AI response to the chat
    messages = [
      ...messages,
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

<h1>Chatbot</h1>
<div
  id="chat-container"
  class="h-full w-full overflow-y-auto border border-gray-300 rounded-lg p-4 mb-4 shadow-md"
>
  {#each messages as message}
    <Displayer {message} />
  {/each}
  {#if loading}
    <div class="flex justify-center items-center">
      <span class="visually-hidden">Loading...</span>
    </div>
  {/if}
</div>

<input
  bind:value={input}
  placeholder="Type your message..."
  class="border border-gray-300 p-3 w-full mb-4 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
  on:keydown={(e) => {
    if (e.key === "Enter") sendMessage();
  }}
/>
<button
  on:click={sendMessage}
  class="bg-blue-500 text-white p-3 rounded-lg shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
>
  Send
</button>
