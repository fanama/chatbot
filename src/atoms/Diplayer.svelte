<script lang="ts">
  import type { MessageEntity } from "../domain/entities/message";
  import { marked } from "marked";

  export let message: MessageEntity;
</script>

<div
  class={`message flex items-start space-x-4 mb-4 ${message.sender === "user" ? "justify-end" : "justify-start"}`}
>
  <div
    class={`${message.sender === "user" ? "bg-green-800 text-white" : "bg-green-800 text-white"} p-4 rounded-lg shadow-md w-fit overflow-scroll border border-green-600`}
  >
    {@html marked.parse(message.text)}
  </div>
</div>
