<script lang="ts">
  import { language } from "../lib/store";
</script>

<div>
  <label for="languageSelect" class="section-label mb-1.5 block"
    >Langue de réponse</label
  >
  <select
    id="languageSelect"
    bind:value={$language}
    class="field select-field"
  >
    <option value="en-US">English (US)</option>
    <option value="es-ES">Español (España)</option>
    <option value="fr-FR">Français (France)</option>
    <option value="de-DE">Deutsch (Deutschland)</option>
  </select>
</div>
