<script lang="ts">
  export let chat: () => void;

  const features = [
    {
      title: "Réponses instantanées",
      description: "Obtenez des réponses en temps réel à vos questions.",
      path: "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.86 9.86 0 0 1-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z",
    },
    {
      title: "Mémoire de vos échanges",
      description:
        "Le contexte de la conversation est conservé pour des réponses cohérentes.",
      path: "M12 8v4l2.5 2.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z",
    },
    {
      title: "Recherche documentaire",
      description:
        "Importez des fichiers et interrogez vos propres documents en langage naturel.",
      path: "M14 3v4a1 1 0 0 0 1 1h4M15 13H9m6 0h2a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h2m0-4H9a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h6",
    },
  ];
</script>

<!-- Was a nested `<main>` inside the shell's own `<main>`, and a flat
     `rounded-xl` / `gap-8` / `mb-16` scale that matched no other page. -->
<div>
  <section class="bg-primary px-4 py-20 text-center text-primary-fg md:py-28">
    <h1 class="text-4xl font-semibold tracking-tight md:text-5xl">
      {import.meta.env.VITE_TITLE || "Démo"}
    </h1>
    <p class="mx-auto mt-4 max-w-2xl text-lg text-primary-fg/90 md:text-xl">
      Votre assistant conversationnel intelligent
    </p>
    <button class="btn btn-lg btn-primary mt-8" on:click={() => chat()}>
      Démarrer la discussion
    </button>
  </section>

  <section class="px-4 py-14 md:px-6">
    <h2 class="page-title mb-6">Nos fonctionnalités</h2>
    <div
      class="mx-auto grid max-w-4xl grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    >
      {#each features as feature (feature.title)}
        <div class="card p-6">
          <div class="mb-3 text-primary">
            <svg
              class="h-6 w-6"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d={feature.path} />
            </svg>
          </div>
          <h3 class="text-base font-semibold text-foreground">{feature.title}</h3>
          <p class="mt-1.5 text-sm text-muted">{feature.description}</p>
        </div>
      {/each}
    </div>
  </section>
</div>
