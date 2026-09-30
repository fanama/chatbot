<script lang="ts">
  import { onDestroy, onMount } from "svelte";
  import { language } from "../lib/store";

  export let transcript = "";
  let canRecord = true;
  let recognition: any = null;
  let isListening = false;
  let baseTranscript = "";

  onDestroy(() => {
    if (recognition) {
      try {
        recognition.abort();
      } catch {}
    }
  });

  onMount(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition ||
      (window as any).mozSpeechRecognition ||
      (window as any).msSpeechRecognition;

    if (!SpeechRecognition) {
      canRecord = false;
      return;
    }

    try {
      recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        isListening = true;
      };

      recognition.onresult = (event: any) => {
        let interimText = "";
        let finalText = "";

        for (let i = 0; i < event.results.length; i++) {
          const res = event.results[i];
          if (res.isFinal) {
            finalText += res[0].transcript;
          } else {
            interimText += res[0].transcript;
          }
        }

        const currentSpeech = (finalText + interimText).trim();
        if (currentSpeech) {
          const separator = baseTranscript && !baseTranscript.endsWith(" ") ? " " : "";
          transcript = baseTranscript + separator + currentSpeech;
        }
      };

      recognition.onend = () => {
        isListening = false;
      };

      recognition.onerror = (event: any) => {
        // En cas de simple absence de voix détectée, on ne stoppe pas l'écoute agressivement
        if (event.error === "no-speech") {
          return;
        }
        console.warn("Speech recognition error:", event.error);
        isListening = false;
      };
    } catch (err) {
      console.error("Failed to initialize SpeechRecognition:", err);
      canRecord = false;
    }
  });

  function startRecording() {
    if (!recognition) return;
    try {
      baseTranscript = transcript ? transcript.trim() : "";
      recognition.lang = $language;
      recognition.start();
    } catch (err) {
      console.warn("Could not start speech recognition:", err);
    }
  }

  function stopRecording() {
    if (!recognition) return;
    try {
      recognition.stop();
    } catch (err) {
      console.warn("Could not stop speech recognition:", err);
    }
    isListening = false;
  }
</script>

{#if canRecord}
  <button
    type="button"
    class={`btn btn-icon-lg btn-outline ${
      isListening ? "border-primary text-primary" : "text-muted"
    }`}
    on:click={isListening ? stopRecording : startRecording}
    aria-label={isListening ? "Arrêter l'enregistrement" : "Dicter le message"}
    title={isListening ? "Arrêter la dictée" : "Dicter"}
  >
    {#if isListening}
      <span
        class="h-2.5 w-2.5 animate-pulse rounded-full bg-danger"
        aria-hidden="true"
        title="Enregistrement en cours"
      ></span>
    {:else}
      <svg
        class="h-4 w-4"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.9"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
        <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
        <line x1="12" y1="19" x2="12" y2="22" />
      </svg>
    {/if}
  </button>
{/if}
