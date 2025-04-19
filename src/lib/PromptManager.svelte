<script lang="ts">
  import type { PromptEntity } from "../domain/entities/prompt";
  import { promptStore, promptStorage } from "./store";

  // Define the prompt store

  // Local state for managing the current prompt being edited
  let currentPrompt: PromptEntity | null = null;
  let title = "";
  let subtitle = "";
  let text = "";
  let showPromptList = false;

  let prompts = promptStorage.getAll();

  // Function to add or update a prompt
  function savePrompt() {
    if (currentPrompt) {
      // Update existing prompt
      prompts = prompts.map((prompt) =>
        prompt === currentPrompt
          ? { ...prompt, title, subtitle, text }
          : prompt,
      );
    } else {
      // Add new prompt
      prompts = [...prompts, { title, subtitle, text }];
    }
    resetForm();
    togglePage();
  }

  // Function to edit a prompt
  function editPrompt(prompt: PromptEntity) {
    currentPrompt = prompt;
    title = prompt.title;
    subtitle = prompt.subtitle;
    text = prompt.text;
    togglePage();
  }

  // Function to reset the form
  function resetForm() {
    currentPrompt = null;
    title = "";
    subtitle = "";
    text = "";
  }

  // Function to remove a prompt
  function removePrompt(prompt: PromptEntity) {
    prompts = prompts.filter((p) => p !== prompt);
  }

  function togglePage() {
    showPromptList = !showPromptList;
  }

  $: if (prompts) {
    promptStorage.save(prompts);
    promptStore.set(prompts);
  }
</script>

<div
  class="w-full h-full text-white border-l border-r border-blue-600 font-mono flex flex-col"
>
  <div class="flex flex-row justify-center">
    <button
      on:click={togglePage}
      class="p-2 bg-blue-700 text-white hover:bg-blue-800 border border-blue-600"
    >
      Toggle to {!showPromptList ? "Form" : "List"}
    </button>
  </div>
  {#if showPromptList}
    <div id="editor" class="p-4 w-full flex-grow flex flex-col">
      <h1 class="text-2xl font-bold mb-4 border-b border-blue-600 pb-2">
        Prompt Manager
      </h1>

      <label for="title" class="block text-sm font-medium text-blue-200">
        Title
      </label>
      <input
        id="title"
        type="text"
        bind:value={title}
        class="mt-1 p-2 w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-blue-800 text-blue-200"
      />

      <label for="subtitle" class="block text-sm font-medium text-blue-200">
        Subtitle
      </label>
      <input
        id="subtitle"
        type="text"
        bind:value={subtitle}
        class="mt-1 p-2 w-full rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-blue-800 text-blue-200"
      />

      <label for="text" class="block text-sm font-medium text-blue-200">
        Text
      </label>
      <textarea
        id="text"
        bind:value={text}
        class="mt-1 p-2 w-full h-40 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-blue-800 text-blue-200"
      ></textarea>

      <div class="flex flex-row gap-2 mt-4">
        <button
          on:click={savePrompt}
          class="px-4 py-2 bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 border border-blue-600"
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
  {:else}
    <div class="h-full text-white p-4 rounded-md shadow-md flex-grow">
      <h2 class="text-xl font-semibold mb-4 border-b border-blue-600 pb-2">
        Prompts List
      </h2>
      <div class="h-full overflow-y-auto grid grid-cols-1 gap-1">
        {#each $promptStore as prompt}
          <div
            class=" text-white p-4 rounded-md shadow-sm bg-gradient-to-br from-blue-400 via-blue-900 to-blue-800 h-full"
          >
            <h3 class="text-lg font-semibold text-white">{prompt.title}</h3>
            <h4 class="text-md text-white">{prompt.subtitle}</h4>

            <div class="mt-2 flex flex-row justify-center gap-4">
              <button
                on:click={() => editPrompt(prompt)}
                class="px-3 py-1 bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 border border-blue-600"
              >
                Edit
              </button>
              <button
                on:click={() => removePrompt(prompt)}
                class="flex flex-row px-3 py-1 bg-red-600 text-white rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 border border-red-600"
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
        {/each}
      </div>
    </div>
  {/if}
</div>
