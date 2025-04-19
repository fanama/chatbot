<script lang="ts">
  import Modal from "./atoms/Modal.svelte";
  import Chatbot from "./lib/Chatbot.svelte";
  import PromptManager from "./lib/PromptManager.svelte";
</script>

<main
  class="h-screen bg-blue-800 flex flex-col items-center justify-center p-4"
>
  <h1
    class="text-3xl font-bold mb-4 text-blue-300 bg-blue-700 w-full text-center border border-blue-600 rounded-lg"
  >
    Nerd-Bot
  </h1>
  <div class="flex flex-row p-1">
    <Modal className="text-blue-600 bg-white" title="liste des consignes"
      ><PromptManager /></Modal
    >
  </div>
  <Chatbot />
</main>
