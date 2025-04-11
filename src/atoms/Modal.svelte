<script lang="ts">
  export let isOpen: boolean = false;
  export let title: string;
  export let className: string = "";

  const toogleModal = () => {
    isOpen = !isOpen;
  };
</script>

<button class={`w-full p-2 rounded-xs ${className}`} on:click={toogleModal}
  >{title}</button
>

{#if isOpen}
  <div
    class="fixed inset-0 flex h-max-screen items-center justify-center z-50 bg-black backdrop"
    on:click={toogleModal}
  >
    <div
      class=" p-2 rounded-lg shadow-lg max-w-full h-1/2 relative"
      on:click|stopPropagation
    >
      <button
        class="absolute top-2 right-2 text-gray-600 hover:text-gray-800"
        on:click={toogleModal}
      >
        ×
      </button>
      <slot></slot>
    </div>
  </div>
{/if}

<style>
  .backdrop {
    background-color: rgba(0, 0, 0, 0.4);
  }
</style>
