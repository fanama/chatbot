<script lang="ts">
  import PromptDisplayer from "./PromptDisplayer.svelte";
  import PromptEditor from "./PromptEditor.svelte";
  import ProviderManager from "./ProviderManager.svelte";
  import type { PromptEntity } from "../domain/entities/prompt";
  import { promptStore, promptStorage, promptSystemStore } from "./store";
  import LanguageSelector from "../atoms/LanguageSelector.svelte";
  import { onMount } from "svelte";

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
            : prompt
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

  onMount(() => {
    // A single subscription, unsubscribed on destroy. The reactive
    // `$: { promptStore.subscribe(...) }` ran on every invalidation, leaking one
    // subscription per run and writing to localStorage repeatedly. This
    // component is remounted on each navigation, so the leak compounded.
    return promptStore.subscribe((value) => {
      promptStorage.save(value);
    });
  });
</script>

<div class="page page-pad flex flex-col gap-4">
  <header>
    <h1 class="page-title">Paramètres</h1>
    <p class="page-sub">
      Langue des réponses et instructions système envoyées au modèle.
    </p>
  </header>

  <div class="card p-4">
    <LanguageSelector />
  </div>

  <!-- ProviderManager already renders its own bordered panel. -->
  <ProviderManager />

  <button
    on:click={togglePage}
    class="btn btn-md btn-outline self-start"
  >
    {!showPromptList ? "Nouveau prompt" : "← Retour à la liste"}
  </button>

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
    <div class="flex min-h-0 w-full flex-1 flex-col">
      <div class="grid min-h-0 grid-cols-1 gap-3 overflow-y-auto lg:grid-cols-2">
        {#each $promptStore as prompt (prompt.title + prompt.text)}
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
