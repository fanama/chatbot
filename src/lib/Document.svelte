<script lang="ts">
  import { onMount } from "svelte";
  import { Embedding } from "../infra/storage/embedding";
  import Uploader from "../atoms/Uploader.svelte";

  let fileName: string = "";
  let chunks: string[] = [];
  let titles: string[] = [];

  let text = "";
  let store: Embedding | null = null;
  let results: string[] = [];
  let isLoading = false;
  let percent = 0;
  let uploadError = "";

  onMount(async () => {
    try {
      store = new Embedding();
      await store.initialize(); // Ensure the store is initialized
    } catch (err) {
      console.error(err);
    }
  });

  async function addDoc(value: string, metadata?: object) {
    if (store && value) {
      try {
        await store.add(value, metadata);
        text = ""; // Clear the input after adding
      } catch (err) {
        console.error(err);
      }
    }
  }

  async function searchDoc() {
    if (store && text) {
      try {
        isLoading = true;
        const { documents: searchResults, metadatas } =
          await store.search(text);
        console.log({ metadatas });
        results = [...new Set([...metadatas, ...searchResults])];
      } catch (err) {
        console.error(err);
      } finally {
        isLoading = false;
      }
    }
  }

  async function loadChunks() {
    if (chunks.length < 1) {
      uploadError = "Aucun contenu à envoyer.";
      return;
    }
    console.log("Loading");
    isLoading = true;
    uploadError = "";
    const context = `
# TABLE OF CONTENT

${titles.join("\n")}

      `;

    // The loop index is used directly: `chunks.indexOf(chunk)` rescanned the
    // array on every iteration (O(n^2)) and also reported the wrong page for
    // duplicated chunks.
    for (const [index, chunk] of chunks.entries()) {
      await addDoc(chunk, {
        context,
        fileName,
        page: `page : ${index}`,
      });
      percent = (index + 1) / chunks.length;
    }

    isLoading = false;
    chunks = [];
  }
</script>

<div class="page page-pad">
  <header class="mb-5">
    <h1 class="page-title">Documents</h1>
    <p class="page-sub">
      Importez des fichiers et interrogez les documents enregistrés.
    </p>
  </header>

  <!-- `grid-cols-2` with no breakpoint: two crushed columns on a phone. -->
  <div class="grid gap-4 lg:grid-cols-2">
    <!-- Colonne de gauche : import -->
    <Uploader bind:fileName bind:chunks bind:titles />

    <!-- Colonne de droite : recherche -->
    <div class="card flex flex-col p-4">
      <h2 class="section-label mb-3">Recherche</h2>
      <input
        bind:value={text}
        class="field"
        placeholder="Rechercher dans les documents…"
        aria-label="Rechercher dans les documents"
      />
      <div class="mt-3 flex gap-2">
        <button
          on:click={loadChunks}
          disabled={isLoading}
          class="btn btn-md btn-primary"
        >
          Envoyer le texte
        </button>
        <button
          on:click={searchDoc}
          disabled={isLoading || !text.trim()}
          class="btn btn-md btn-outline"
        >
          Rechercher
        </button>
      </div>

      {#if uploadError}
        <p class="mt-3 text-sm text-danger" role="alert">{uploadError}</p>
      {/if}

      {#if isLoading}
        <div class="mt-4">
          <div class="progress">
            <div
              class="progress-bar"
              style="width: {Math.max(Math.trunc(percent * 100), 4)}%"
            ></div>
          </div>
          <p class="mt-2 text-sm text-muted">
            Traitement en cours… {Math.trunc(percent * 100)} %
          </p>
        </div>
      {:else if results.length > 0}
        <div class="mt-4 min-h-0 flex-1">
          <h3 class="section-label mb-2">Résultats</h3>
          <div class="flex flex-col gap-2">
            {#each results as result, i (i)}
              <div
                class="max-h-40 overflow-y-auto whitespace-pre-wrap break-words rounded-md bg-surface-sunken p-2.5 text-sm text-foreground"
              >
                {result}
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>
