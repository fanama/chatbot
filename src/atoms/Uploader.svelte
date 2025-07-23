<script lang="ts">
  import { onMount } from "svelte";
  import pdf2md from "@opendocsg/pdf2md";
  let fileInput: HTMLInputElement;
  let textContent: string = "";
  export let chunks: string[] = [];

  interface Chunk {
    title: string;
    content: string[];
  }

  function markdownToChunks(markdown: string): Chunk[] {
    const lines = markdown.split("\n").filter((line) => line.trim() !== "");
    console.log(markdown);

    let chunks = [];
    let currentChunk: Chunk | null = null;

    for (const line of lines) {
      if (line.startsWith("#")) {
        if (currentChunk !== null) {
          chunks.push(currentChunk);
        }
        currentChunk = {
          title: line,
          content: [],
        };
      } else {
        if (currentChunk !== null) {
          currentChunk.content.push(line);
        }
      }
    }

    if (currentChunk !== null) {
      chunks.push(currentChunk);
    }
    return chunks;
  }

  const onSubmit = async (event: Event) => {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const formData = new FormData(form);

    fileInput = form.querySelector('input[type="file"]') as HTMLInputElement;
    const file = fileInput.files?.[0];
    if (file) {
      if (file.type === "application/pdf") {
        formData.append("file", file);
        await processPdfFile(file);
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

  const processPdfFile = async (file: File) => {
    try {
      let reader = new FileReader();

      reader.onload = async function (event) {
        if (!event.target) {
          return;
        }
        let arrayBuffer = event.target.result;
        const markdown = await pdf2md(arrayBuffer);
        splitTextIntoChunks(markdown);
      };

      reader.readAsArrayBuffer(file);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error uploading file. Please try again.");
    }
  };

  const splitTextIntoChunks = (text: string) => {
    chunks = markdownToChunks(text).map((chunk) => {
      return `${chunk.title} \n${chunk.content.join("\n")}`;
    });
  };
</script>

<main class="p-8 overflow-scroll">
  <h1 class="text-2xl font-bold mb-4 text-white">Upload</h1>

  <form on:submit={onSubmit} class="flex flex-col gap-4">
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
      class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-green-300 transition duration-300"
    >
      Convert to Text
    </button>
  </form>

  {#if chunks.length > 0}
    <div
      class="mt-4 h-screen overflow-y-scroll bg-gray-100 flex flex-col gap-2"
    >
      {#each chunks as chunk}
        <pre class="text-blue-600 p-2 rounded-lg max-w-96">{chunk}</pre>
      {/each}
    </div>
  {:else}
    <p class="text-gray-500 mt-4">No chunks available.</p>
  {/if}
</main>
