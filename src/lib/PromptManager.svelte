<script lang="ts">
  import PromptDisplayer from "./PromptDisplayer.svelte";
  import PromptEditor from "./PromptEditor.svelte";
  import ProviderManager from "./ProviderManager.svelte";
  import type { PromptEntity } from "../domain/entities/prompt";
  import { promptStore, promptStorage, promptSystemStore } from "./store";
  import LanguageSelector from "../atoms/LanguageSelector.svelte";

  // Local state for managing the current prompt being edited
  let currentPrompt: PromptEntity | null = null;
  let title = "";
  let subtitle = "";
  let text = "";
  let showPromptList = false;

  // Function to add or update a prompt
  function savePrompt() {
    promptStore.update((prompts) => {
      if (currentPrompt) {
        // Update existing prompt
        return prompts.map((prompt) =>
          prompt === currentPrompt
            ? { ...prompt, title, subtitle, text }
            : prompt,
        );
      } else {
        // Add new prompt
        return [...prompts, { title, subtitle, text }];
      }
    });
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

  function selectPrompt(prompt: PromptEntity) {
    promptSystemStore.set(prompt.text);
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
    promptStore.update((prompts) => prompts.filter((p) => p !== prompt));
  }

  function togglePage() {
    showPromptList = !showPromptList;
  }

  // Reactive statement to save prompts to storage whenever promptStore updates
  $: {
    promptStore.subscribe((value) => {
      promptStorage.save(value);
    });
  }
</script>

<div class="w-full h-3/4 text-white font-mono flex flex-col gap-2">
  <LanguageSelector />
  <button
    on:click={togglePage}
    class="p-2 text-blue-700 bg-gradient-to-br from-white to-blue-200 cursor-pointer rounded w-full h-full"
  >
    {!showPromptList ? "New" : "Return"}
  </button>
  <div class="p-2">
    <ProviderManager />
  </div>
  {#if showPromptList}
    <PromptEditor
      bind:title
      bind:subtitle
      bind:text
      {currentPrompt}
      {savePrompt}
      {resetForm}
    />
  {:else}
    <div class="h-full w-full text-white p-4 rounded-md flex-grow">
      <div class="h-full overflow-y-auto grid grid-cols-1 gap-1">
        {#each $promptStore as prompt}
          <PromptDisplayer
            {prompt}
            {selectPrompt}
            {editPrompt}
            {removePrompt}
          />
        {/each}
      </div>
    </div>
  {/if}
</div>
