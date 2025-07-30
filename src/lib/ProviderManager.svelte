<script lang="ts">
  import { providersStore, providerStore } from "./store";
</script>

<select
  bind:value={$providerStore}
  class="w-full h-full p-3 m-2 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-blue-900 font-mono"
>
  {#each $providersStore as provider}
    <option value={provider}>provider : {provider}</option>
  {/each}
</select>
