<script lang="ts">
  import HeadPhones from "../assets/headphones.svg";
  import Stop from "../assets/stop.svg";
  import { language } from "../lib/store";

  export let textValue = "";
  let synth = window.speechSynthesis;
  let isSpeaking = false;
  let isStoped = false;

  function startSpeaking() {
    isStoped = false;
    if (synth.speaking) {
      synth.cancel();
    }
    const chunks = textValue.split("\n");
    for (const text of chunks) {
      if (isStoped) {
        break; // Exit the loop if stop was clicked
      }
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = $language; // Set the language
      synth.speak(utterance);
      isSpeaking = true;

      utterance.onend = () => {
        isSpeaking = false;
      };
    }
    isSpeaking = false;
  }

  function stopSpeaking() {
    if (synth.speaking) {
      synth.cancel();
      isSpeaking = false;
      isStoped = true;
    }
  }
</script>

<div class="flex flex-col space-y-4 text-xs">
  <div class="flex space-x-2">
    <button
      id="speakButton"
      class="px-4 py-2 text-white bg-blue-500 rounded-md cursor-pointer"
      on:click={startSpeaking}
    >
      <img src={HeadPhones} alt="listen..." class="w-[1rem] h-[1em]" />
    </button>
    <button
      id="stopButton"
      class="px-4 py-2 text-white bg-red-500 rounded-md cursor-pointer"
      on:click={stopSpeaking}
    >
      <img src={Stop} alt="listen..." class="w-[1rem] h-[1em]" />
    </button>
  </div>
</div>

<style>
  .hidden {
    display: none;
  }
</style>
