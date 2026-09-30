<script lang="ts">
  import { onMount } from "svelte";
  import { themeStore, themeStorage, type Theme } from "../lib/store";

  function apply(theme: Theme) {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }

  function toggle() {
    const next: Theme = $themeStore === "dark" ? "light" : "dark";
    apply(next);
    themeStorage.save([next]);
    themeStore.set(next);
  }

  /* Keeps the attribute in sync when another tab changes the theme. */
  onMount(() => {
    const onStorage = (event: StorageEvent) => {
      if (event.key === "theme" && event.newValue) {
        const theme = JSON.parse(event.newValue)[0] as Theme;
        themeStore.set(theme);
        apply(theme);
      }
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  });
</script>

<button
  type="button"
  on:click={toggle}
  class="btn btn-icon btn-outline"
  aria-label={$themeStore === "dark" ? "Passer en thème clair" : "Passer en thème sombre"}
  title={$themeStore === "dark" ? "Thème clair" : "Thème sombre"}
>
  {#if $themeStore === "dark"}
    <svg
      class="h-[1.1rem] w-[1.1rem]"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linecap="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="4" />
      <path
        d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"
      />
    </svg>
  {:else}
    <svg
      class="h-[1.1rem] w-[1.1rem]"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
    </svg>
  {/if}
</button>
