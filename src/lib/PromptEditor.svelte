<script lang="ts">
  import type { PromptEntity } from "../domain/entities/prompt";
  export let title = "";
  export let subtitle = "";
  export let text = "";
  export let currentPrompt: PromptEntity | null | undefined;
  export let savePrompt: () => void;
  export let resetForm: () => void;
</script>

<div id="editor" class="p-4 w-full flex-grow flex flex-col text-white">
  <h1 class="text-2xl font-bold mb-4 border-b border-blue-600 pb-2">
    Prompt Manager
  </h1>

  <label for="title" class="block text-sm font-medium text-white">Title</label>
  <input
    id="title"
    type="text"
    bind:value={title}
    class="mt-1 p-2 w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-gradient-to-br from-white to-blue-200 text-blue-900"
  />

  <label for="subtitle" class="block text-sm font-medium text-white"
    >Subtitle</label
  >
  <input
    id="subtitle"
    type="text"
    bind:value={subtitle}
    class="mt-1 p-2 w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-gradient-to-br from-white to-blue-200 text-blue-900"
  />

  <label for="text" class="block text-sm font-medium text-white">Text</label>
  <textarea
    id="text"
    bind:value={text}
    class="mt-1 p-2 w-full h-40 rounded-md shadow-sm sm:text-sm bg-gradient-to-br from-white to-blue-200 text-blue-900"
  ></textarea>

  <div class="flex flex-row gap-2 mt-4">
    <button
      on:click={savePrompt}
      class="px-4 py-2 bg-gradient-to-br from-white to-blue-200 text-blue-600 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 border border-blue-600"
    >
      {currentPrompt ? "Update" : "Create"} Prompt
    </button>
    <button
      on:click={resetForm}
      class="px-4 py-2 bg-gray-600 text-white rounded-md shadow-sm hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 border border-gray-600"
    >
      Reset
    </button>
  </div>
</div>
