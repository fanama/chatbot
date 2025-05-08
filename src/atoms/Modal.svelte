<script lang="ts">
  export let isOpen: boolean = false;
  export let title: string;
  export let className: string = "";

  const toogleModal = () => {
    isOpen = !isOpen;
  };
</script>

<button
  class={`w-full p-2 rounded-xs cursor-pointer ${className}`}
  on:click={toogleModal}>{title}</button
>

{#if isOpen}
  <div
    class="fixed inset-0 flex justify-end items-start p-4 backdrop"
    on:click={toogleModal}
  >
    <div
      class="p-2 rounded-lg max-w-full h-full bg-blue-900"
      on:click|stopPropagation
    >
      <div class="flex p-1 justify-end">
        <button
          class="text-gray-600 text-white p-3 hover:bg-red-800 bg-red-400 cursor-pointer rounded"
          on:click={toogleModal}
        >
          ×
        </button>
      </div>
      <slot></slot>
    </div>
  </div>
{/if}

<style>
  .backdrop {
    background-color: rgba(0, 0, 0, 0);
  }
</style>
