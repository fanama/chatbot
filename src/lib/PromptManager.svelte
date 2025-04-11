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

  // Function to add or update a prompt
  function savePrompt() {
    if (currentPrompt) {
      // Update existing prompt
      const newPrompt = $promptStore.map((prompt) =>
        prompt === currentPrompt
          ? { ...prompt, title, subtitle, text }
          : prompt,
      );
      promptStore.set(newPrompt);
      promptStorage.save(newPrompt);
    } else {
      // Add new prompt
      promptStore.set([...$promptStore, { title, subtitle, text }]);
      promptStorage.add({ title, subtitle, text });
    }
    resetForm();
  }

  // Function to edit a prompt
  function editPrompt(prompt: PromptEntity) {
    currentPrompt = prompt;
    title = prompt.title;
    subtitle = prompt.subtitle;
    text = prompt.text;
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
    const newPrompt = $promptStore.filter((p) => p !== prompt);
    promptStore.set(newPrompt);
    promptStorage.save(newPrompt);
  }

  function togglePage() {
    showPromptList = !showPromptList;
  }
</script>

<div class="container w-fit h-full text-white font-mono">
  <div class="flex flex-row justify-center">
    <button
      on:click={togglePage}
      class=" p-2 bg-green-800 text-white shadow-sm hover:bg-green-900 border border-green-700"
    >
      Toggle to {!showPromptList ? "Form" : "List"}
    </button>
  </div>
  {#if showPromptList}
    <div class="p-4 w-fit h-full rounded-md shadow-md">
      <h1 class="text-2xl font-bold mb-4 border-b border-green-600 pb-2">
        Prompt Manager
      </h1>

      <div class="mb-4">
        <label for="title" class="block text-sm font-medium text-green-300"
          >Title</label
        >
        <input
          id="title"
          type="text"
          bind:value={title}
          class="mt-1 p-2 w-full border border-green-600 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm bg-green-900 text-green-300"
        />
      </div>

      <div class="mb-4">
        <label for="subtitle" class="block text-sm font-medium text-green-300"
          >Subtitle</label
        >
        <input
          id="subtitle"
          type="text"
          bind:value={subtitle}
          class="mt-1 p-2 w-full border border-green-600 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm bg-green-900 text-green-300"
        />
      </div>

      <div class="mb-4">
        <label for="text" class="block text-sm font-medium text-green-300"
          >Text</label
        >
        <textarea
          id="text"
          bind:value={text}
          class="mt-1 p-2 w-full border border-green-600 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm bg-green-900 text-green-300"
        ></textarea>
      </div>

      <div class="flex justify-between">
        <button
          on:click={savePrompt}
          class="px-4 py-2 bg-green-600 text-white rounded-md shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 border border-green-700"
        >
          {currentPrompt ? "Update" : "Create"} Prompt
        </button>
        <button
          on:click={resetForm}
          class="px-4 py-2 bg-gray-700 text-white rounded-md shadow-sm hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 border border-gray-800"
        >
          Reset
        </button>
      </div>
    </div>
  {:else}
    <div class="h-full text-white p-4 rounded-md shadow-md">
      <h2 class="text-xl font-semibold mb-4 border-b border-green-600 pb-2">
        Prompts List
      </h2>
      <div class="h-full overflow-y-auto grid grid-cols-2 gap-1">
        {#each $promptStore as prompt}
          <div
            class="border border-green-600 text-white p-4 rounded-md shadow-sm bg-green-900"
          >
            <h3 class="text-lg font-semibold text-green-300">{prompt.title}</h3>
            <h4 class="text-md text-gray-400">{prompt.subtitle}</h4>
            <p class="text-gray-300">{prompt.text}</p>
            <div class="mt-2 flex flex-row justify-between">
              <button
                on:click={() => editPrompt(prompt)}
                class="px-3 py-1 bg-blue-700 text-white rounded-md shadow-sm hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 border border-blue-800"
              >
                Edit
              </button>
              <button
                on:click={() => removePrompt(prompt)}
                class="flex flex-row px-3 py-1 bg-red-700 text-white rounded-md shadow-sm hover:bg-red-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 border border-red-800"
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
