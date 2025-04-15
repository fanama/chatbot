<script lang="ts">
  import type { MessageEntity } from "../domain/entities/message";
  import { marked } from "marked";
  import clipboard from "../infra/keyboard/clipBoard";

  export let message: MessageEntity;
</script>

<div
  class={`message flex items-start space-x-4 mb-4 ${message.sender === "user" ? "justify-end" : "justify-start"}`}
>
  <div
    class={`${message.sender === "user" ? "bg-green-800 text-white" : "bg-green-800 text-white"} p-4 rounded-lg shadow-md w-fit overflow-scroll border border-green-600`}
  >
    {@html marked.parse(message.text)}
    <div class="text-right p-2">
      <button
        on:click={() => clipboard.copy(message.text)}
        type="button"
        class="px-2 py-1 bg-green-600 text-white rounded hover:bg-green-500 flex items-center text-xs"
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
    </div>
  </div>
</div>
