<script lang="ts">
  import Modal from "./atoms/Modal.svelte";
  import Chatbot from "./lib/Chatbot.svelte";
  import PromptManager from "./lib/PromptManager.svelte";
</script>

<main class="h-screen bg-black flex flex-col items-center justify-center p-4">
  <h1
    class="text-3xl font-bold mb-4 text-green-400 bg-green-800 w-full text-center border border-green-600 rounded-lg"
  >
    Nerd-Bot
  </h1>
  <div class="flex flex-row p-1">
    <Modal className="bg-green-800 text-white " title="useCases"
      ><PromptManager /></Modal
    >
  </div>
  <Chatbot />
</main>
