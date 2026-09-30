<script lang="ts">
  import { onMount } from "svelte";
  import { language } from "../lib/store";

  export let transcript = "";
  let canRecord = true;
  let recognition: any;
  let isListening = false;

  onMount(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition ||
      (window as any).mozSpeechRecognition ||
      (window as any).msSpeechRecognition;

    if (SpeechRecognition) {
      recognition = new SpeechRecognition();
      recognition.continuous = true; // Keep listening even after a pause
      recognition.interimResults = true; // Show interim results
      recognition.maxAlternatives = 1; // Number of possible transcriptions

      recognition.onstart = () => {
        isListening = true;
      };

      recognition.onresult = (event: any) => {
        let newTranscript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            newTranscript += event.results[i][0].transcript;
          }
        }
        if (newTranscript) {
          transcript += newTranscript;
        }
      };

      recognition.onend = () => {
        isListening = false;
      };

      recognition.onerror = (event: any) => {
        let errorMessage = "";
        switch (event.error) {
          case "network":
            errorMessage =
              "Network error. Please check your internet connection.";
            break;
          case "not-allowed":
            errorMessage = "Permission to use microphone is blocked.";
            break;
          case "no-speech":
            errorMessage = "No speech was detected.";
            break;
          case "audio-capture":
            errorMessage = "Microphone is not available.";
            break;
          default:
            errorMessage = "An error occurred during speech recognition.";
            break;
        }
        isListening = false;
      };
    } else {
      canRecord = false;
      console.error("Your browser does not support speech recognition.");
    }
  });

  function startRecording() {
    if (recognition) {
      recognition.lang = $language; // Update language before starting
      recognition.start();
    }
  }

  function stopRecording() {
    if (recognition) {
      recognition.stop();
    }
  }
</script>

{#if canRecord}
  <button
    id={isListening ? "stopButton" : "startButton"}
    class={`btn btn-icon-lg btn-outline ${
      isListening ? "border-primary text-primary" : "text-muted"
    }`}
    on:click={isListening ? stopRecording : startRecording}
    aria-label={isListening ? "Arrêter l'enregistrement" : "Dicter le message"}
    title={isListening ? "Arrêter" : "Dicter"}
  >
    {#if isListening}
      <span
        class="h-2 w-2 rounded-full bg-danger"
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
        aria-hidden="true"
      >
        <path d="M12 3v3M5.6 6.6l2.1 2.1M4 13h3M9.7 18.3l-2.1 2.1M18 13h3" />
        <rect x="9" y="8" width="6" height="12" rx="3" />
        <circle cx="19" cy="5" r="1.6" />
        <path d="M4 5h2.5" />
      </svg>
    {/if}
  </button>
{/if}
