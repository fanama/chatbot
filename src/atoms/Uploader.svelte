<script lang="ts">
  let fileInput: HTMLInputElement;
  let textContent: string = "";
  let uploadError = "";
  export let fileName = "";
  export let chunks: string[] = [];
  export let titles: string[] = [];
  export let hide: boolean = false;
  interface Chunk {
    fileName: string;
    title: string;
    content: string[];
  }

  function markdownToChunks(fileName: string, markdown: string): Chunk[] {
    const lines = markdown.split("\n").filter((line) => line.trim() !== "");

    let chunks: Chunk[] = [];
    let currentChunk: Chunk | null = null;

    for (const line of lines) {
      const isTitle = line.startsWith("#");
      const currentTitleLevel = isTitle ? line.split(" ").shift()!.length : 0;
      const lastTitleLevel = currentChunk?.title?.startsWith("#")
        ? currentChunk.title.split(" ").shift()!.length
        : 0;

      if (isTitle && currentChunk && currentTitleLevel === lastTitleLevel) {
        currentChunk.title += line;
      } else if (isTitle) {
        if (currentChunk) {
          chunks.push(currentChunk);
        }
        currentChunk = {
          fileName,
          title: line,
          content: [],
        };
      } else {
        if (currentChunk) {
          currentChunk.content.push(line);
        } else {
          // Si pas de titre encore, commence un chunk avec un titre null (temporaire)
          currentChunk = {
            fileName,
            title: fileName,
            content: [line],
          };
        }
      }
    }

    if (currentChunk) {
      chunks.push(currentChunk);
    }

    chunks = chunks.reduce<Chunk[]>((acc, chunk) => {
      if (chunk.content.length === 1 && acc.length > 0) {
        acc[acc.length - 1].content.push(chunk.content[0]);
        acc[acc.length - 1].content = [...new Set(acc[acc.length - 1].content)];
      } else if (chunk.content.length > 1) {
        acc.push(chunk);
      }
      return acc;
    }, []);

    // Si pas de titre dans le fichier entier, fusionne en un seul chunk
    if (
      !chunks.some((chunk) => chunk.title !== fileName) &&
      chunks.length > 1
    ) {
      return [
        {
          fileName,
          title: fileName,
          content: chunks.flatMap((c) => c.content),
        },
      ];
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
      fileName = file.name;

      if (file.type === "application/pdf") {
        formData.append("file", file);
        await processPdfFile(file);
      } else if (
        file.type === "text/plain" ||
        file.type === "text/markdown" ||
        file.type.startsWith("text/") || // Covers many code/text files
        fileName.endsWith(".ts") || // TypeScript files
        fileName.endsWith(".svelte") || // TypeScript files
        fileName === "dockerfile" || // Dockerfile (often no extension)
        fileName.endsWith(".dockerfile") || // Sometimes with extension
        fileName.endsWith(".yml") ||
        fileName.endsWith(".yaml") ||
        fileName.endsWith(".md") ||
        fileName === ".dockerignore"
      ) {
        await processTextFile(file);
      } else {
        uploadError =
          "Type de fichier non pris en charge. Importez un PDF, un fichier texte ou du code.";
        console.log(file.type);
      }
    }
  };

  const processTextFile = async (file: File) => {
    const text = await file.text();
    textContent = text;
    splitTextIntoChunks(file.name, text);
  };

  const processPdfFile = async (file: File) => {
    try {
      // Loaded on demand: pdf2md embeds a PDF.js runtime, and this component is
      // mounted in both the chat and the document page, so a static import made
      // every visitor download it.
      const { default: pdf2md } = await import("@opendocsg/pdf2md");

      const arrayBuffer = await file.arrayBuffer();
      const markdown = await pdf2md(arrayBuffer);
      splitTextIntoChunks(file.name, markdown);
    } catch (error) {
      console.error("Error uploading file:", error);
      uploadError = "Erreur lors de la lecture du fichier. Réessayez.";
    }
  };

  const splitTextIntoChunks = (fileName: string, text: string) => {
    chunks = markdownToChunks(fileName, text).map((chunk) => {
      return `#${fileName}\n\n ${chunk.title} \n${chunk.content.join("\n")}`;
    });
  };

  function unload() {
    fileName = "";
    chunks = [];
    titles = [];
    uploadError = "";
  }
</script>

<!-- Was a nested `<main>` inside the shell's own `<main>`, padded `p-8` while
     the panel next to it used `p-4`, and its own `text-2xl` heading now that
     the page carries the title. -->
<section class="card flex flex-col p-4">
  <h2 class="section-label mb-3">Import</h2>

  <form on:submit={onSubmit} class="flex flex-col gap-3">
    <input
      type="file"
      name="file"
      required
      class="block w-full rounded-md border border-border bg-surface-raised p-2 text-sm text-muted
        file:mr-3 file:cursor-pointer file:rounded-md file:border-0 file:bg-surface-sunken
        file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-foreground
        hover:file:bg-surface-hover
        focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
    />
    {#if chunks.length == 0}
      <button type="submit" class="btn btn-md btn-primary self-start">
        Charger le fichier
      </button>
    {/if}
  </form>

  {#if uploadError}
    <p class="mt-3 text-sm text-danger" role="alert">{uploadError}</p>
  {/if}

  {#if chunks.length > 0 && !hide}
    <div
      class="mt-4 max-h-96 min-h-0 flex-1 space-y-2 overflow-y-auto"
    >
      {#each chunks as chunk, i (i)}
        <pre
          class="m-0 w-full whitespace-pre-wrap break-words rounded-md border border-border bg-surface-sunken p-2.5 text-xs text-foreground">{chunk}</pre
        >
      {/each}
    </div>
  {:else if chunks.length > 0}
    <div
      class="mt-3 flex items-center gap-2 rounded-md border border-success/40 bg-success/10 px-3 py-2 text-sm text-foreground"
      role="status"
    >
      <span class="h-2 w-2 shrink-0 rounded-full bg-success" aria-hidden="true"
      ></span>
      <span class="min-w-0 truncate">
        {chunks.length} section{chunks.length > 1 ? "s" : ""} prête
        {chunks.length > 1 ? "s" : ""} à envoyer.
      </span>
      <button class="btn btn-xs btn-outline ml-auto shrink-0" on:click={unload}>
        Retirer
      </button>
    </div>
  {:else}
    <p class="mt-3 text-sm text-muted">Aucun contenu chargé.</p>
  {/if}
</section>
