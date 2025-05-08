<script lang="ts">
  import { onMount } from "svelte";
  import Mic from "../assets/mic.svg";
  import MicOff from "../assets/mic-off.svg";
  import { language } from "../lib/store";

  export let transcript = "";
  const dispatch = (eventName: string, detail: any) => {
    const event = new CustomEvent(eventName, { detail });
    window.dispatchEvent(event);
  };
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
        transcript += newTranscript;
        dispatch("transcriptChanged", { transcript });
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
  {#if isListening}
    <button
      id="stopButton"
      class="px-4 py-2 text-white bg-red-500"
      on:click={stopRecording}
    >
      <img src={MicOff} alt="record" class="w-[1rem]" />
    </button>
  {:else}
    <button
      id="startButton"
      class="px-4 py-2 text-white bg-blue-500"
      on:click={startRecording}
    >
      <img src={Mic} alt="record" class="w-[1rem]" />
    </button>
  {/if}
{/if}
