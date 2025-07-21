<script lang="ts">
  import type { PromptEntity } from "../domain/entities/prompt";
  import { promptSystemStore, promptStore } from "./store";

  export let prompt: PromptEntity;
  export let editPrompt: (prompt: PromptEntity) => void;
  export let selectPrompt: (prompt: PromptEntity) => void;
  export let removePrompt: (prompt: PromptEntity) => void;

  $: selected = $promptSystemStore == prompt.text;
</script>

<div
  class={`text-blue-900 p-4 rounded-md shadow-sm ${selected ? "bg-gradient-to-br from-green-200 to-white" : "bg-gradient-to-br from-blue-200 to-white"} h-full`}
>
  <h3 class="text-lg font-semibold text-blue-900">{prompt.title}</h3>
  <h4 class="text-md text-blue-900">{prompt.subtitle}</h4>

  <div class="mt-2 flex flex-row justify-between">
    <button
      on:click={() => editPrompt(prompt)}
      class="px-3 py-1 cursor-pointer bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 border border-blue-600"
    >
      Edit
    </button>
    <button
      on:click={() => selectPrompt(prompt)}
      class="px-3 py-1 cursor-pointer bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 border border-blue-600"
    >
      Select
    </button>
    <button
      on:click={() => removePrompt(prompt)}
      class="flex flex-row cursor-pointer px-3 py-1 bg-red-600 text-white rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 border border-red-600"
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
      Remove
    </button>
  </div>
</div>
