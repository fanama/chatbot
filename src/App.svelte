<script lang="ts">
  import Modal from "./atoms/Modal.svelte";
  import Chatbot from "./lib/Chatbot.svelte";
  import PromptManager from "./lib/PromptManager.svelte";
</script>

<main
  class="h-screen bg-gradient-to-br from-blue-800 to-white flex flex-col items-center justify-center"
>
  <nav class="bg-blue-900 p-4 w-full">
    <div class="container mx-auto flex justify-between items-center">
      <h1 class="text-3xl font-bold text-white">Nerd-Bot</h1>
      <div class="flex text-white">
        <Modal className="text-blue-600 bg-white" title="Settings">
          <PromptManager />
        </Modal>
      </div>
    </div>
  </nav>
  <div class="flex flex-row p-1"></div>
  <Chatbot />
</main>
