<script lang="ts">
  import type { PromptEntity } from "../domain/entities/prompt";
  import { promptSystemStore } from "./store";

  export let prompt: PromptEntity;
  export let editPrompt: (prompt: PromptEntity) => void;
  export let selectPrompt: (prompt: PromptEntity) => void;
  export let removePrompt: (prompt: PromptEntity) => void;

  $: selected = $promptSystemStore == prompt.text;
</script>

<!-- Both branches of the ternary below were byte-identical, so the selected
     prompt was visually indistinguishable from the others. -->
<article
  class={`card flex flex-col p-4 ${selected ? "border-primary bg-primary-soft" : ""}`}
  aria-current={selected ? "true" : undefined}
>
  <div class="flex items-start gap-2">
    <div class="min-w-0 flex-1">
      <h3 class="truncate text-base font-semibold text-foreground">
        {prompt.title}
      </h3>
      {#if prompt.subtitle}
        <p class="mt-0.5 truncate text-sm text-muted">{prompt.subtitle}</p>
      {/if}
    </div>
    {#if selected}
      <span
        class="inline-flex shrink-0 items-center gap-1 rounded-full bg-primary px-2 py-0.5 text-[0.7rem] font-medium text-primary-fg"
      >
        <svg
          class="h-3 w-3"
          viewBox="0 0 20 20"
          fill="none"
          stroke="currentColor"
          stroke-width="2.2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M4.5 10.5l3.5 3.5 7.5-8" />
        </svg>
        Actif
      </span>
    {/if}
  </div>

  <div class="mt-4 flex flex-wrap gap-2">
    <button
      on:click={() => selectPrompt(prompt)}
      disabled={selected}
      class="btn btn-sm {selected ? 'btn-outline' : 'btn-primary'}"
      aria-pressed={selected}
    >
      {selected ? "Sélectionné" : "Utiliser"}
    </button>
    <button
      on:click={() => editPrompt(prompt)}
      class="btn btn-sm btn-outline"
    >
      Modifier
    </button>
    <button
      on:click={() => removePrompt(prompt)}
      class="btn btn-sm btn-ghost ml-auto text-danger hover:bg-danger-soft hover:text-danger"
    >
      Supprimer
    </button>
  </div>
</article>
