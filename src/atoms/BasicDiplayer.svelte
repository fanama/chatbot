<script lang="ts">
  export let message: string;
  export let provider = "";
</script>

<!-- Mirrors the assistant bubble in Diplayer.svelte so the streamed answer and
     the final message read as the same object instead of two designs. -->
<div class="flex w-full items-start gap-3 md:gap-4">
  <span
    class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-fg"
    aria-hidden="true"
  >
    <svg
      class="h-4 w-4"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.9"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path d="M12 3v3M5.6 6.6l2.1 2.1M4 13h3M9.7 18.3l-2.1 2.1M18 13h3" />
      <rect x="9" y="8" width="6" height="12" rx="3" />
      <circle cx="19" cy="5" r="1.6" />
      <path d="M4 5h2.5" />
    </svg>
  </span>

  <div class="flex min-w-0 flex-1 flex-col items-start">
    <div
      class="w-full max-w-[min(46rem,85%)] rounded-xl rounded-bl-md border border-border bg-surface-raised px-4 py-3 text-foreground shadow-sm"
    >
      <div class="whitespace-pre-wrap break-words">{message}</div>
    </div>

    <div class="mt-1.5 flex items-center gap-1">
      {#if provider}
        <span
          class="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface-raised px-2 py-0.5 text-[0.7rem] text-muted"
          title="Modèle en cours d'utilisation"
        >
          <span
            class="h-1.5 w-1.5 animate-pulse rounded-full bg-success"
            aria-hidden="true"
          ></span>
          {provider}
        </span>
      {/if}
    </div>
  </div>
</div>
