<script lang="ts">
  import type { MessageEntity } from "../domain/entities/message";
  import { marked } from "marked";
  import clipboard from "../infra/keyboard/clipBoard";
  import VoiceOutput from "./VoiceOutput.svelte";

  export let message: MessageEntity;

  // Parse markdown content once when the component is created
  let parsedContent = "";

  async function parse() {
    try {
      parsedContent = await marked.parse(message.text);
    } catch {
      parsedContent = message.text;
    }
  }

  $: parse();

  const isUser = message.sender === "user";
</script>

<div
  class={`message flex items-start space-x-4 mb-4 ${isUser ? "justify-end" : "justify-start"}`}
>
  <div
    class={`bg-gradient-to-br from-blue-200 to-white text-blue-900 p-4 rounded-lg  w-fit overflow-auto `}
  >
    {#if isUser}
      {message.text}
    {:else}<div class="markdown-content">
        {@html parsedContent}
      </div>
    {/if}

    <div class="flex flex-row gap-2 text-right p-2">
      <button
        on:click={() => clipboard.copy(message.text)}
        type="button"
        class="px-2 py-1 bg-blue-600 cursor-pointer text-white rounded hover:bg-blue-500 flex items-center text-xs"
        aria-label="Copy to clipboard"
        title="Copy to clipboard"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <rect x="8" y="8" width="12" height="12" rx="2" ry="2"></rect>
          <path
            d="M16 8V4a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-4"
          ></path>
        </svg>
        <span class="ml-1">Copy</span>
      </button>
      {#if message.provider}
        <div
          class="px-2 py-1 bg-blue-600 text-white rounded flex items-center text-xs"
        >
          <span class="ml-1">{message.provider}</span>
        </div>
      {/if}
      <VoiceOutput textValue={message.text} />
    </div>
  </div>
</div>

<style>
  /* Custom styles for markdown content */
  .markdown-content h1,
  .markdown-content h2,
  .markdown-content h3,
  .markdown-content h4,
  .markdown-content h5,
  .markdown-content h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
  }
  .markdown-content p {
    margin-bottom: 1em;
  }
  .markdown-content code {
    background-color: #f5f5f5;
    padding: 0.2em 0.4em;
    border-radius: 3px;
  }
  .markdown-content pre {
    background-color: #f5f5f5;
    padding: 1em;
    border-radius: 3px;
    overflow-x: auto;
  }
  .markdown-content blockquote {
    border-left: 4px solid #ccc;
    padding-left: 1em;
    margin-left: 0;
    color: #666;
  }
</style>
