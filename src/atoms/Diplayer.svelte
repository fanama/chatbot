<script lang="ts">
  import type { MessageEntity } from "../domain/entities/message";
  import { marked } from "marked";

  export let message: MessageEntity;
</script>

<div
  class={`message flex items-start space-x-4 mb-4 ${message.sender === "user" ? "justify-end" : "justify-start"}`}
>
  <div
    class={`${message.sender === "user" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-800"} p-4 rounded-lg shadow-md max-w-md`}
  >
    {@html marked.parse(message.text)}
  </div>
</div>
