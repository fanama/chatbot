<script lang="ts">
  import { onMount } from "svelte";

  let fileInput: HTMLInputElement;
  let textContent: string = "";
  export let chunks: string[] = [];
  let chunkSize: number = 1000; // Define the size of each chunk

  const handleFileChange = async (event: Event) => {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      if (file.type === "text/plain" || file.type === "text/markdown") {
        await processTextFile(file);
      } else {
        alert("Unsupported file type. Please upload a PDF or text file.");
        console.log(file.type);
      }
    }
  };

  const processTextFile = async (file: File) => {
    const text = await file.text();
    textContent = text;
    splitTextIntoChunks(text);
  };

  const splitTextIntoChunks = (text: string) => {
    chunks = text.split("\n");
  };

  onMount(() => {
    // Initialize or set up anything if needed
  });
</script>

<main class="p-8 max-w-2xl mx-auto">
  <h1 class="text-2xl font-bold mb-4">Upload a PDF or Text File</h1>

  <input
    type="file"
    bind:this={fileInput}
    accept=".txt,.md"
    on:change={handleFileChange}
    class="block w-full text-sm text-gray-500
    file:mr-4 file:py-2 file:px-4
    file:rounded-md file:border-0
    file:text-sm file:font-semibold
    file:bg-blue-50 file:text-blue-700
    hover:file:bg-blue-100
    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
  />

  {#if chunks.length > 0}
    <div class="h-40 overflow-scroll flex flex-col gap-2">
      <h2 class="text-xl font-semibold mb-2">Text Chunks</h2>
      {#each chunks as chunk}
        <p class="bg-white text-blue-600 p-2">{chunk}</p>
      {/each}
    </div>
  {:else}
    <p>No chunks available.</p>
  {/if}
</main>
