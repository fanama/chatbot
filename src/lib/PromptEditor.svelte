<script lang="ts">
  import type { PromptEntity } from "../domain/entities/prompt";
  export let title = "";
  export let subtitle = "";
  export let text = "";
  export let currentPrompt: PromptEntity | null | undefined;
  export let savePrompt: () => void;
  export let resetForm: () => void;
</script>

<!-- The heading used to read "Prompt Manager", duplicating the page title it
     now lives under. -->
<section class="card p-4">
  <h2 class="text-base font-semibold tracking-tight text-foreground">
    {currentPrompt ? "Modifier le prompt" : "Nouveau prompt"}
  </h2>
  <p class="mt-1 mb-4 text-sm text-muted">
    Ces instructions sont ajoutées au début de chaque échange.
  </p>

  <div class="flex flex-col gap-4">
    <div>
      <label for="prompt-title" class="mb-1.5 block text-sm font-medium text-foreground"
        >Titre</label
      >
      <input
        id="prompt-title"
        type="text"
        bind:value={title}
        class="field"
        placeholder="Titre du prompt"
      />
    </div>

    <div>
      <label
        for="prompt-subtitle"
        class="mb-1.5 block text-sm font-medium text-foreground">Sous-titre</label
      >
      <input
        id="prompt-subtitle"
        type="text"
        bind:value={subtitle}
        class="field"
        placeholder="Description courte"
      />
    </div>

    <div>
      <label for="prompt-text" class="mb-1.5 block text-sm font-medium text-foreground"
        >Texte</label
      >
      <textarea
        id="prompt-text"
        bind:value={text}
        class="field min-h-40 resize-y font-mono text-xs"
        placeholder="Instructions envoyées au modèle…"
      ></textarea>
    </div>
  </div>

  <div class="mt-4 flex gap-2">
    <button on:click={savePrompt} class="btn btn-md btn-primary">
      {currentPrompt ? "Mettre à jour" : "Créer le prompt"}
    </button>
    <button on:click={resetForm} class="btn btn-md btn-outline">
      Réinitialiser
    </button>
  </div>
</section>
