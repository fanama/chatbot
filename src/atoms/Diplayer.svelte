<script lang="ts">
  import "../assets/themes/prism-atom-dark.css";
  import type { MessageEntity } from "../domain/entities/message";
  import { marked } from "marked";
  import clipboard from "../infra/keyboard/clipBoard";
  import VoiceOutput from "./VoiceOutput.svelte";
  import { onMount } from "svelte";
  import { userStore } from "../lib/store";

  export let message: MessageEntity;

  let parsedContent = "";
  let contextDisplayer = false;
  let resultElement: HTMLDivElement;

  async function parse() {
    try {
      parsedContent = await marked.parse(message.text);
    } catch {
      parsedContent = message.text;
    }
  }

  $: parse();

  const isUser = message.sender === "user";

  // Fonction pour ajouter les boutons de copie
  const addCopyButtons = () => {
    // Attendre que le contenu soit rendu
    setTimeout(() => {
      const codeBlocks = document.querySelectorAll(
        ".message-container pre code"
      );

      codeBlocks.forEach((codeBlock) => {
        // Vérifier si le bouton existe déjà
        if (!codeBlock.nextElementSibling?.classList.contains("copy-button")) {
          const copyButton = document.createElement("button");
          copyButton.innerText = "Copier";
          copyButton.className = "copy-button";
          copyButton.style.marginLeft = "10px";
          copyButton.style.padding = "2px 6px";
          copyButton.style.backgroundColor = "#3b82f6";
          copyButton.style.color = "white";
          copyButton.style.borderRadius = "4px";
          copyButton.style.cursor = "pointer";

          copyButton.onclick = () => {
            clipboard.copy(codeBlock.innerHTML);
          };

          // Ajouter le bouton après le bloc de code
          codeBlock.after(copyButton);
        }
      });
    }, 100); // Petit délai pour s'assurer que le contenu est rendu
  };

  // Fonction pour observer les changements dans le DOM
  const observeDOMChanges = () => {
    const observer = new MutationObserver(addCopyButtons);
    observer.observe(resultElement, {
      childList: true,
      subtree: true,
    });
  };

  onMount(() => {
    addCopyButtons();
    observeDOMChanges();
  });
</script>

<div
  class="message-container flex flex-col md:flex-row gap-4 items-start w-full"
>
  <!-- Résultat principal -->
  <div
    bind:this={resultElement}
    class={`message flex items-start space-x-4 mb-4 ${isUser ? "justify-end" : "justify-start"} flex-1 `}
  >
    <div
      class="bg-gradient-to-br flex flex-col from-blue-200 to-white text-blue-900 p-4 rounded-lg overflow-auto"
    >
      {#if isUser}
        <div>{message.text}</div>
      {:else}
        {@html parsedContent}
      {/if}

      <div class="flex flex-row gap-2 text-right p-2">
        <button
          on:click={() => clipboard.copy(message.text)}
          type="button"
          class="px-2 py-1 bg-blue-600 cursor-pointer text-white rounded hover:bg-blue-500 flex items-center text-xs"
          aria-label="Copy to clipboard"
          title="Copy to clipboard"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect x="8" y="8" width="12" height="12" rx="2" ry="2"></rect>
            <path
              d="M16 8V4a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-4"
            ></path>
          </svg>
          <span class="ml-1">Copy</span>
        </button>

        {#if message.provider}
          <div
            class="px-2 py-1 bg-blue-600 text-white rounded flex items-center text-xs"
          >
            <span class="ml-1">{message.provider}</span>
          </div>
        {/if}

        <VoiceOutput textValue={message.text} />
        {#if message.context && message.context.length > 0}
          <button
            class="px-2 py-1 bg-blue-600 text-white rounded flex items-center text-xs"
            on:click={() => (contextDisplayer = !contextDisplayer)}
            >context</button
          >
          {#if $userStore?.role == "ADMIN"}
            <button
              class="px-2 py-1 bg-blue-600 text-white rounded flex items-center text-xs"
              on:click={message.insertToStore}>enregistrer</button
            >
          {/if}
        {/if}
      </div>
    </div>
  </div>

  <!-- Contexte -->
  {#if message.context && contextDisplayer && message.context.length > 0}
    <div
      style={`height: ${resultElement?.clientHeight}px;`}
      class="context-container px-2 py-1 overflow-auto rounded flex flex-col items-start text-xs bg-white text-blue-600 w-full md:w-1/3"
    >
      {#each message.context as context}
        <pre class="p-1 w-full whitespace-pre-wrap">{context}</pre>
      {/each}
    </div>
  {/if}
</div>
