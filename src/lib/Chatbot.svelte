<script lang="ts">
  import type { MessageEntity } from "../domain/entities/message";
  import Displayer from "../atoms/Diplayer.svelte";
  import { onMount, tick } from "svelte";
  import { AIProvider, isAbortError } from "../infra/ai/aiProvider";
  import {
    promptStore,
    promptSystemStore,
    providersStore,
    providerStore,
    language,
  } from "./store";
  import { LocalStorage } from "../infra/storage/localStorage";

  import VoiceInput from "../atoms/VoiceInput.svelte";
  import { Embedding } from "../infra/storage/embedding";
  import BasicDiplayer from "../atoms/BasicDiplayer.svelte";
  import Uploader from "../atoms/Uploader.svelte";
  import Modal from "../atoms/Modal.svelte";

  const historyStorage = new LocalStorage<MessageEntity>("history", []);

  let store: Embedding | null = null;
  let useStore = false; // Nouvelle variable pour la checkbox

  let history: MessageEntity[] = historyStorage.getAll();
  let input: string = "";
  let loading: boolean = false;
  let streamContent = "";
  let streamProvider = "";
  let fileName: string = "";
  let errorMessage = "";
  let controller: AbortController | null = null;

  let chunks: string[] = [];

  let messageContainer: HTMLDivElement;

  const ai = new AIProvider();

  // Tokens arrive one by one, far faster than the screen refreshes. Writing
  // `streamContent` on every token invalidated the whole component and re-diffed
  // the whole message list, so they are batched to one update per frame.
  let pendingTokens = "";
  let frame: number | null = null;

  const flushTokens = (): string => {
    if (frame !== null) {
      cancelAnimationFrame(frame);
      frame = null;
    }
    if (!pendingTokens) return streamContent;

    streamContent += pendingTokens;
    pendingTokens = "";
    return streamContent;
  };

  const pushToken = (token: string) => {
    pendingTokens += token;
    if (frame === null) {
      frame = requestAnimationFrame(() => {
        frame = null;
        flushTokens();
      });
    }
  };

  // A scroll region only follows new content if it is told to: browsers only
  // auto-anchor growth near the top of the content, so a streaming answer
  // (which grows at the bottom) ran off the edge while the view stayed put.
  const STICK_THRESHOLD_PX = 96;

  // Held in an object on purpose. Assigning a top-level `let` would invalidate
  // the component on every `scroll` event, so a single smooth scroll would
  // trigger a full re-render per frame.
  const scrollState = { stick: true };

  const isNearBottom = () => {
    if (!messageContainer) return true;
    const { scrollTop, scrollHeight, clientHeight } = messageContainer;
    return scrollHeight - (scrollTop + clientHeight) < STICK_THRESHOLD_PX;
  };

  const onScroll = () => {
    // `scroll` also fires for our own programmatic scrolls, which is what keeps
    // this flag correct: it lands near the bottom and re-arms the flag.
    scrollState.stick = isNearBottom();
  };

  const scrollToBottom = (behavior: ScrollBehavior = "auto", force = false) => {
    if (!messageContainer) return;
    if (!force && !scrollState.stick) return;
    messageContainer.scrollTo({ top: messageContainer.scrollHeight, behavior });
  };

  // A new exchange must always be visible, so this one forces the scroll.
  $: if (history) {
    scrollToBottom("smooth", true);
  }

  // Following the stream used to hang off `streamContent`, which stopped firing
  // once tokens were batched into `flushTokens`. Reading it here re-arms the
  // scroll on every update.
  //
  // `tick()` resolves once the DOM is patched and still runs before the next
  // paint; waiting a whole animation frame instead left the view one frame
  // behind the growing answer, which showed up as a ~50px gap.
  $: if (loading || streamContent) {
    void tick().then(() => scrollToBottom("auto"));
  }

  // Persisted only when the message list actually changes, never on a token.
  $: if (history) {
    historyStorage.save(history);
  }

  const getStoreResults = async (query: string) => {
    if (!store || !useStore) return { documents: [], metadatas: [] };
    try {
      const storeResult = await store.search(query);
      return {
        documents: storeResult.documents,
        metadatas: [...new Set(storeResult.metadatas)],
      };
    } catch (e) {
      console.log("no DB");
      return { documents: [], metadatas: [] };
    }
  };

  const insertToStore = async (input: string, response: string) => {
    if (!store) return { documents: [], metadatas: [] };
    try {
      await store.add(`input:${input}=>output:${response}`, {
        input,
        response,
      });
    } catch (e) {
      console.log("no DB");
    }
  };

  const sendMessage = async () => {
    if (input.trim() === "" || loading) return;

    const text = input;

    loading = true;
    errorMessage = "";
    // `streamContent` was never cleared, so the previous answer stayed on screen
    // for the whole next generation.
    streamContent = "";
    pendingTokens = "";
    streamProvider = "";
    // `frame` was reset to null while a frame was still queued, which left that
    // callback free to flush the next answer's first tokens early.
    if (frame !== null) {
      cancelAnimationFrame(frame);
      frame = null;
    }

    let documents: string[] = [];
    let metadatas: string[] = [];

    const { documents: initialDocuments, metadatas: initialMetadatas } =
      await getStoreResults(text);
    documents = initialDocuments;
    metadatas = initialMetadatas;

    input = "";
    history = [...history, { sender: "user", text: text }];

    // Limiter l'historique à 5 derniers messages
    const recentHistory = history.slice(-5);

    // Every message owns its controller so the stop button can abort it and a
    // component unmount cannot leave a request running.
    controller = new AbortController();

    try {
      const response = await ai.chat({
        text,
        useVectorstore: useStore,
        signal: controller.signal,
        history: [
          { sender: "system", text: $promptSystemStore },
          ...documents.map((text) => {
            return { sender: "system", text };
          }),
          ...metadatas.map((text) => {
            return { sender: "system", text };
          }),
          ...chunks.map((chunk) => {
            return { sender: "system", text: chunk };
          }),
          { sender: "system", text: `you will respond in ${$language}` },
          ...recentHistory,
        ],
        providerName: $providerStore,
        stream: pushToken,
        onProvider: (name: string) => (streamProvider = name),
      });

      const answer = response.text;

      history = [
        ...history,
        {
          sender: "assistant",
          text: answer,
          provider: response.provider,
          context: [...metadatas, ...documents],
          insertToStore: async () => {
            await insertToStore(text, answer);
          },
        },
      ];
    } catch (error) {
      if (isAbortError(error)) {
        // The user stopped the generation: keep what was already received.
        const partial = flushTokens();
        if (partial) {
          // `streamProvider` is the model that was actually emitting, not the
          // requested one: the badge must not claim the wrong provider.
          history = [...history, { sender: "assistant", text: partial, provider: streamProvider }];
        }
      } else {
        console.error("Chat failed:", error);
        errorMessage = error instanceof Error ? error.message : String(error);
      }
    } finally {
      controller = null;
      // Apply whatever the last animation frame was still holding before the
      // view is measured.
      flushTokens();
      loading = false;
      // The last frame can land after `loading` goes false, so re-check the
      // geometry once the DOM has settled.
      void tick().then(() => scrollToBottom("auto"));
    }
  };

  const stopGeneration = () => {
    controller?.abort();
    controller = null;
  };

  onMount(() => {
    // A single subscription, unsubscribed on destroy. The previous reactive
    // `$: { promptStore.subscribe(...) }` created a new subscription on every
    // run and never cleaned it up, duplicating the localStorage writes.
    const unsubscribePrompt = promptStore.subscribe((prompts) => {
      if (prompts.length > 0 && $promptSystemStore === "") {
        promptSystemStore.set(prompts[0].text);
      }
    });

    const setup = async () => {
      try {
        const providers = ai.getAll();

        providersStore.set(providers);
        if (!$providerStore) {
          providerStore.set(providers[0] ?? "backend");
        }

        store = new Embedding();
        await store.initialize();
      } catch (err) {
        // The chat still works without the vector store, so this is not fatal.
        console.warn("Embedding store unavailable:", err);
      }
    };
    void setup();

    return () => {
      unsubscribePrompt();
      controller?.abort();
      if (frame !== null) cancelAnimationFrame(frame);
    };
  });
</script>

<!-- Single scroll container: there used to be an `overflow-y-scroll` wrapper
     around an `overflow-y-auto` message list, so the page scrolled behind the
     composer and auto-scroll fought the outer element. -->
<div class="flex min-h-0 w-full flex-1 flex-col">
  <div
    bind:this={messageContainer}
    on:scroll={onScroll}
    class="min-h-0 flex-1 overflow-y-auto overscroll-contain bg-surface-sunken px-4 py-6 md:px-6"
  >    <div class="mx-auto flex w-full max-w-4xl flex-col gap-5">
      {#each history as message}
        <Displayer {message} />
      {/each}

      {#if loading}
        <BasicDiplayer message={streamContent} provider={streamProvider} />
      {/if}

      {#if errorMessage}
        <p
          class="rounded-lg border border-danger/40 bg-danger-soft px-4 py-3 text-sm text-danger"
          role="alert"
        >
          {errorMessage}
        </p>
      {/if}
    </div>
  </div>


  <div class="w-full shrink-0 border-t border-border bg-surface px-4 py-3 md:px-6">
    <div class="mx-auto flex w-full max-w-4xl flex-col gap-2.5">
      <div class="flex items-center justify-between gap-3">
        <div class="flex min-w-0 items-center gap-3">
          <Modal
            title={fileName || "Joindre un document"}
            className="btn-sm btn-outline max-w-56 overflow-hidden text-ellipsis whitespace-nowrap"
          >
            <Uploader bind:fileName bind:chunks hide={true} />
          </Modal>

          {#if store}
            <label
              class="flex cursor-pointer select-none items-center gap-2 text-xs text-muted"
            >
              <input
                type="checkbox"
                bind:checked={useStore}
                class="h-3.5 w-3.5 accent-[var(--primary)]"
              />
              <span>Recherche documentaire</span>
            </label>
          {/if}
        </div>

        {#if history.length > 0}
          <button
            on:click={() => (history = [])}
            class="btn btn-sm btn-ghost shrink-0"
            title="Effacer la conversation"
            aria-label="Effacer la conversation"
          >
            <svg
              class="h-3.5 w-3.5"
              viewBox="0 0 20 20"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linecap="round"
              aria-hidden="true"
            >
              <path
                d="M3.5 5.5h13M8 5.5V4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v1.5M5.5 5.5 6 15a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1l.5-9.5"
              ></path>
            </svg>
            <span>Effacer</span>
          </button>
        {/if}
      </div>

      <div class="flex items-end gap-2">
        <textarea
          bind:value={input}
          rows="1"
          placeholder="Posez votre question…"
          class="field min-h-10 max-h-40 flex-1 resize-none py-2.5"
          on:keydown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
          aria-label="Message"
        ></textarea>

        <VoiceInput bind:transcript={input} />

        {#if loading}
          <!-- Stop button: aborts the fetch, which also releases the worker
               thread blocked in the Flask generator. -->
          <button
            on:click={stopGeneration}
            title="Arrêter la génération"
            aria-label="Arrêter la génération"
            class="btn btn-icon-lg btn-danger"
          >
            <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <rect x="5" y="5" width="10" height="10" rx="1.5" />
            </svg>
          </button>
        {:else}
          <button
            on:click={sendMessage}
            title="Envoyer"
            aria-label="Envoyer le message"
            disabled={!input.trim()}
            class="btn btn-icon-lg btn-primary"
          >
            <svg
              class="h-4 w-4"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        {/if}
      </div>
    </div>
  </div>
</div>
