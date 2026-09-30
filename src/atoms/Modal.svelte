<script lang="ts">
  import { onMount } from "svelte";

  export let isOpen: boolean = false;
  export let title: string;
  export let className: string = "";

  const toogleModal = () => {
    isOpen = !isOpen;
  };

  // Click-away was the only way to dismiss with the keyboard: the panel is not
  // a focus trap and Escape did nothing.
  function onKeydown(event: KeyboardEvent) {
    if (event.key === "Escape" && isOpen) {
      isOpen = false;
    }
  }

  onMount(() => {
    window.addEventListener("keydown", onKeydown);
    return () => window.removeEventListener("keydown", onKeydown);
  });
</script>

<!-- Only the base class is forced: the caller picks the size and the variant,
     so a trigger can never end up with `btn-sm` twice. -->
<button
  class={`btn ${className}`}
  on:click={toogleModal}><slot name="trigger">{title}</slot></button
>

{#if isOpen}
  <div
    class="fixed inset-0 flex items-start justify-end p-4 backdrop"
    role="button"
    tabindex="-1"
    aria-label="Fermer la fenêtre"
    on:click={toogleModal}
    on:keydown={(e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        toogleModal();
      }
    }}
  >
    <div
      class="max-h-full max-w-full overflow-auto rounded-lg border border-border bg-surface-raised p-4 shadow-xl"
      role="dialog"
      aria-modal="true"
      tabindex="-1"
      aria-label={title || undefined}
      on:click|stopPropagation
    >
      <div class="flex justify-end">
        <button
          class="btn btn-sm btn-ghost"
          on:click={toogleModal}
          aria-label="Fermer"
        >
          <svg
            class="h-4 w-4"
            viewBox="0 0 20 20"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            aria-hidden="true"
          >
            <path d="M5 5l10 10M15 5L5 15" />
          </svg>
        </button>
      </div>
      {#if title}
        <h1 class="p-2 text-lg font-semibold text-foreground">{title}</h1>
      {/if}
      <slot></slot>
    </div>
  </div>
{/if}

<style>
  /* Was fully transparent: the panel floated with no scrim to click away from. */
  .backdrop {
    background-color: oklch(0.15 0.01 258 / 0.5);
  }
</style>
