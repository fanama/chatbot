<script lang="ts">
  import "../assets/themes/prism-atom-dark.css";
  import type { MessageEntity } from "../domain/entities/message";
  import { Marked } from "marked";
  import DOMPurify from "dompurify";
  import clipboard from "../infra/keyboard/clipBoard";
  import VoiceOutput from "./VoiceOutput.svelte";
  import { userStore } from "../lib/store";
  import { ROLES } from "../domain/values/users";

  export let message: MessageEntity;

  let contextDisplayer = false;
  let resultElement: HTMLDivElement;

  const escapeHtml = (value: string) =>
    value
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");

  // The copy button is emitted next to the block by the renderer, so it no
  // longer has to be injected into the DOM after the fact. That removed a
  // MutationObserver per message watching the whole subtree and re-querying
  // every code block of the document on each mutation (O(messages x blocks)).
  const parser = new Marked({
    renderer: {
      code({ text, lang }): string {
        const language = (lang || "").replace(/[^a-zA-Z0-9+#-]/g, "");
        const cls = language ? ` class="language-${language}"` : "";
        const langLabel = language
          ? `<span class="code-lang">${language}</span>`
          : "";
        // The pair is wrapped so the copy button can be absolutely positioned
        // over the block. Its styling moved to `.chat-prose .code-block` in
        // app.css: it used to carry hardcoded inline colours.
        return (
          `<div class="code-block">` +
          `<pre><code${cls}>${escapeHtml(text)}</code></pre>` +
          langLabel +
          `<button type="button" class="copy-button" data-copy-code>Copier</button>` +
          `</div>`
        );
      },
    },
  });

  // Was non-reactive: with an unkeyed `{#each}` Svelte reuses the instance, so a
  // row could keep the alignment of the previous author.
  $: isUser = message.sender === "user";

  // `marked` is synchronous: the previous `await` only added a reactivity
  // round-trip. The HTML is sanitised because the text comes from the model
  // *and* from localStorage, which made `{@html}` a stored-XSS sink.
  $: parsedContent = DOMPurify.sanitize(parser.parse(message.text ?? "") as string);

  // Delegated: one listener for the whole message instead of one per code block.
  function copyFromCodeBlock(event: MouseEvent) {
    const trigger = (event.target as HTMLElement | null)?.closest("[data-copy-code]");
    if (!trigger) return;
    const code = trigger.closest(".code-block")?.querySelector("code")?.textContent ?? "";
    clipboard.copy(code);
  }
</script>

<div class="message-container flex w-full gap-3 md:gap-4 items-start">
  {#if !isUser}
    <span
      class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-fg"
      aria-hidden="true"
    >
      <svg
        class="h-4 w-4"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.9"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M12 3v3M5.6 6.6l2.1 2.1M4 13h3M9.7 18.3l-2.1 2.1M18 13h3" />
        <rect x="9" y="8" width="6" height="12" rx="3" />
        <circle cx="19" cy="5" r="1.6" />
        <path d="M4 5h2.5" />
      </svg>
    </span>
  {/if}

  <div class="flex min-w-0 flex-1 flex-col {isUser ? 'items-end' : 'items-start'}">
    <div
      bind:this={resultElement}
      on:click={copyFromCodeBlock}
      class="message w-full max-w-[min(46rem,85%)] rounded-xl px-4 py-3 shadow-sm {isUser
        ? 'bg-primary text-primary-fg rounded-br-md'
        : 'bg-surface-raised text-foreground border border-border rounded-bl-md'}"
    >
      {#if isUser}
        <div class="whitespace-pre-wrap break-words">{message.text}</div>
      {:else}
        <div class="chat-prose break-words">{@html parsedContent}</div>
      {/if}
    </div>

    <div
      class="mt-1.5 flex flex-wrap items-center gap-1 {isUser
        ? 'justify-end'
        : 'justify-start'}"
    >
      {#if message.provider && !isUser}
        <span
          class="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface-raised px-2 py-0.5 text-[0.7rem] text-muted"
          title="Modèle ayant généré cette réponse"
        >
          <span class="h-1.5 w-1.5 rounded-full bg-success" aria-hidden="true"></span>
          {message.provider}
        </span>
      {/if}

      <button
        on:click={() => clipboard.copy(message.text)}
        type="button"
        class="btn btn-xs btn-ghost"
        aria-label="Copier le message"
        title="Copier"
      >
        <svg
          class="h-3.5 w-3.5"
          viewBox="0 0 20 20"
          fill="none"
          stroke="currentColor"
          stroke-width="1.6"
        >
          <rect x="8" y="8" width="12" height="12" rx="2"></rect>
          <path d="M16 8V4a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-4"
          ></path>
        </svg>
        <span>Copier</span>
      </button>

      <VoiceOutput textValue={message.text} />

      {#if message.context && message.context.length > 0}
        <button
          class="btn btn-xs btn-ghost"
          on:click={() => (contextDisplayer = !contextDisplayer)}
          aria-expanded={contextDisplayer}
          title="Afficher les documents utilisés"
        >
          <svg
            class="h-3.5 w-3.5"
            viewBox="0 0 20 20"
            fill="none"
            stroke="currentColor"
            stroke-width="1.6"
          >
            <path d="M3 5.5A1.5 1.5 0 0 1 4.5 4h4L10 6h5.5A1.5 1.5 0 0 1 17 7.5v7A1.5 1.5 0 0 1 15.5 16h-11A1.5 1.5 0 0 1 3 14.5Z"
            ></path>
          </svg>
          <span>Contexte</span>
        </button>
        {#if $userStore?.role == ROLES.ADMIN}
          <button
            class="btn btn-xs btn-ghost"
            on:click={() => message.insertToStore?.()}
            title="Enregistrer ce couple question/réponse"
          >
            <svg
              class="h-3.5 w-3.5"
              viewBox="0 0 20 20"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
            >
              <path d="M10 3v9m0 0 3.5-3.5M10 12 6.5 8.5"></path>
              <path d="M3.5 13v2A1.5 1.5 0 0 0 5 16.5h10a1.5 1.5 0 0 0 1.5-1.5v-2"
              ></path>
            </svg>
            <span>Enregistrer</span>
          </button>
        {/if}
      {/if}
    </div>
  </div>

  {#if isUser}
    <span
      class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-surface-sunken text-muted ring-1 ring-border"
      aria-hidden="true"
    >
      <svg
        class="h-4 w-4"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.9"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <circle cx="12" cy="8" r="3.6" />
        <path d="M4.5 20a7.5 7.5 0 0 1 15 0" />
      </svg>
    </span>
  {/if}

  {#if message.context && contextDisplayer && message.context.length > 0}
    <div
      class="mt-2 flex w-full flex-col items-start gap-2 rounded-lg border border-border bg-surface-raised p-3"
    >
      <p class="text-[0.7rem] font-medium uppercase tracking-wide text-muted">
        Documents utilisés
      </p>
      {#each message.context as context, i (i)}
        <pre
          class="w-full whitespace-pre-wrap break-words rounded-lg bg-surface-sunken p-2 text-xs text-foreground">{context}</pre>
      {/each}
    </div>
  {/if}
</div>
