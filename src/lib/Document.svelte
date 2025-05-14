<script lang="ts">
  import { onMount } from "svelte";
  import { Embedding } from "../infra/storage/embedding";
  import Uploader from "../atoms/Uploader.svelte";

  let chunks: string[] = [];
  let text = "";
  let store: Embedding | null = null;
  let results: string[] = [];
  let isLoading = false;

  onMount(async () => {
    try {
      store = new Embedding();
      await store.initialize(); // Ensure the store is initialized
    } catch (err) {
      console.error(err);
    }
  });

  async function addDoc(value: string) {
    if (store && value) {
      try {
        await store.add(value);
        text = ""; // Clear the input after adding
      } catch (err) {
        console.error(err);
      } finally {
      }
    }
  }

  async function searchDoc() {
    if (store && text) {
      try {
        isLoading = true;
        const searchResults = await store.search(text);
        results = searchResults;
        console.log({ results });
      } catch (err) {
        console.error(err);
      } finally {
        isLoading = false;
      }
    }
  }

  async function loadChunks() {
    if (chunks.length < 1) {
      alert("there is no chunk to upload");
      return;
    }
    console.log("loading");
    isLoading = true;

    for (const chunk of chunks) {
      await addDoc(chunk);
      console.log(chunks.indexOf(chunk));
    }

    isLoading = false;
  }
</script>

<div class="w-full">
  <Uploader bind:chunks />
  <div class="flex flex-col gap-2">
    <input
      bind:value={text}
      class="flex-1 p-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-blue-600"
      placeholder="Enter text..."
    />
    <button
      on:click={loadChunks}
      disabled={isLoading}
      class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-blue-300"
    >
      Add
    </button>
    <button
      on:click={searchDoc}
      disabled={isLoading}
      class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-green-300"
    >
      Search
    </button>
  </div>

  {#if isLoading}
    <p class="text-center text-gray-500">Loading...</p>
  {/if}

  {#if results.length > 0}
    <div class="mt-4">
      <h2 class="text-xl font-bold mb-2">Search Results:</h2>
      <div class="flex flex-col gap-2">
        {#each results as result}
          <div class="p-2 bg-gray-100 text-blue-600 rounded-lg">{result}</div>
        {/each}
      </div>
    </div>
  {/if}
</div>
