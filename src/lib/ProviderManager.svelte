<script lang="ts">
  import { providersStore, providerStore } from "./store";
  let provider = $providerStore;
  $: providers = $providersStore;

  $: providerStore.set(provider);
</script>

<select
  bind:value={provider}
  class="w-full h-full p-3 m-2 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-blue-900 font-mono"
>
  {#each providers as provider}
    <option value={provider}>provider : {provider}</option>
  {/each}
</select>
