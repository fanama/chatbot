<script lang="ts">
  import { language } from "../lib/store";
</script>

<select
  id="languageSelect"
  bind:value={$language}
  class="w-full p-2 border border-gray-300 rounded-md"
>
  <option class="text-blue-900" value="en-US">English (US)</option>
  <option class="text-blue-900" value="es-ES">Spanish (Spain)</option>
  <option class="text-blue-900" value="fr-FR">French (France)</option>
  <option class="text-blue-900" value="de-DE">German (Germany)</option>
  <!-- Add more languages as needed -->
</select>
