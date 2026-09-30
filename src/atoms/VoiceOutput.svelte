<script lang="ts">
  import { onDestroy } from "svelte";
  import { language } from "../lib/store";

  export let textValue = "";
  // One instance per message, and never cancelled on unmount: the voice kept
  // reading after leaving the conversation. One per page is enough.
  const synth = window.speechSynthesis;
  let isSpeaking = false;

  onDestroy(() => {
    synth.cancel();
  });

  function startSpeaking() {
    synth.cancel();

    for (const line of textValue.split("\n")) {
      if (!line.trim()) continue;
      const utterance = new SpeechSynthesisUtterance(line);
      utterance.lang = $language;
      utterance.onend = () => {
        isSpeaking = false;
      };
      synth.speak(utterance);
    }
    isSpeaking = true;
  }

  function stopSpeaking() {
    synth.cancel();
    isSpeaking = false;
  }
</script>

<div class="flex items-center gap-1">
  <button
    type="button"
    class="btn btn-xs btn-ghost"
    on:click={startSpeaking}
    disabled={!textValue.trim() || isSpeaking}
    aria-label="Lire le message à voix haute"
    title="Lire à voix haute"
  >
    <svg
      class="h-3.5 w-3.5"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <path d="M4 14v-2a8 8 0 0 1 16 0v2" />
      <path d="M4 14h2.5a1.5 1.5 0 0 1 1.5 1.5v2A1.5 1.5 0 0 1 6.5 19H6a2 2 0 0 1-2-2z" />
      <path d="M20 14h-2.5a1.5 1.5 0 0 0-1.5 1.5v2a1.5 1.5 0 0 0 1.5 1.5h.5a2 2 0 0 0 2-2z" />
    </svg>
    <span>Écouter</span>
  </button>
  <button
    type="button"
    class="btn btn-xs btn-ghost"
    on:click={stopSpeaking}
    disabled={!isSpeaking}
    aria-label="Arrêter la lecture"
    title="Arrêter"
  >
    <svg
      class="h-3.5 w-3.5"
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
    >
      <rect x="5" y="5" width="10" height="10" rx="1.5" />
    </svg>
  </button>
</div>
