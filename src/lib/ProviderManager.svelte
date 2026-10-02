<script lang="ts">
  /**
   * Provider selection happens server-side, in `AIProviderManager`: it tries
   * Mistral, then Google, then OpenRouter and finally local Ollama. This panel
   * used to hold a `<select>` listing the only registered provider
   * ("backend"), which looked like a model choice but could not change anything.
   * The model that actually answered is reported by the `provider` SSE frame and
   * shown as a badge under each assistant message.
   */
</script>

<div
  class="card p-4 text-sm text-muted"
  role="note"
>
  <p class="font-medium text-foreground">Fournisseur automatique</p>
  <p class="mt-1">
    Les appels sont tentés dans l'ordre&nbsp;: Mistral, puis Google Gemini, OpenRouter et
    enfin Ollama en secours local. Le modèle ayant réellement répondu est affiché sous
    chaque message de l'assistant.
  </p>
</div>
