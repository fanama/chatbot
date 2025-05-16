<script lang="ts">
  import { onMount } from "svelte";
  let fileInput: HTMLInputElement;
  let textContent: string = "";
  export let chunks: string[] = [];

  const onSubmit = async (event: Event) => {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const formData = new FormData(form);

    fileInput = form.querySelector('input[type="file"]') as HTMLInputElement;
    const file = fileInput.files?.[0];
    if (file) {
      if (file.type === "application/pdf") {
        formData.append("file", file);
        await processPdfFile(formData);
      } else if (file.type === "text/plain" || file.type === "text/markdown") {
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

  const processPdfFile = async (formData: FormData) => {
    try {
      const response = await fetch("http://localhost:3001/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      const textContent = data.text;
      splitTextIntoChunks(textContent);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error uploading file. Please try again.");
    }
  };

  const splitTextIntoChunks = (text: string) => {
    chunks = text.split("\n\n");
  };

  onMount(() => {
    // Initialize or set up anything if needed
  });
</script>

<main class="p-8 max-w-2xl mx-auto">
  <h1 class="text-2xl font-bold mb-4">Upload a PDF or Text File</h1>

  <form on:submit={onSubmit} class="flex flex-col gap-2">
    <input
      type="file"
      name="video"
      required
      class="block w-full text-sm text-gray-500
    file:mr-4 file:py-2 file:px-4
    file:rounded-md file:border-0
    file:text-sm file:font-semibold
    file:bg-blue-50 file:text-blue-700
    hover:file:bg-blue-100
    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
    />
    <button
      type="submit"
      class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-green-300"
      >Upload</button
    >
  </form>

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
