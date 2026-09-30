<script lang="ts">
  import Chatbot from "./lib/Chatbot.svelte";
  import Document from "./lib/Document.svelte";
  import PromptManager from "./lib/PromptManager.svelte";
  import { Embedding } from "./infra/storage/embedding";
  import { onMount } from "svelte";
  import Login from "./lib/Login.svelte";
  import Accueil from "./lib/Accueil.svelte";

  import { LocalStorage } from "./infra/storage/localStorage";
  import { userStore } from "./lib/store";
  import type { UserEntity } from "./domain/entities/user";
  import Footer from "./atoms/Footer.svelte";
  import ThemeToggle from "./atoms/ThemeToggle.svelte";
  import { ROLES } from "./domain/values/users";
  import { pages } from "./domain/values/pages";

  let error: string | null = null;

  const pageStorage = new LocalStorage<string>("page", [pages.HOME]);
  const userStorage = new LocalStorage<UserEntity>("users", []);

  $: page = pageStorage.getAll()[0];

  const setPage = (p: string) => {
    page = p;
    pageStorage.save([p]);
  };

  onMount(async () => {
    try {
      page = pageStorage.getAll()[0];
      const users = userStorage.getAll();
      userStore.set(users[0] || { name: "user", role: "USER" });

      const store = new Embedding();

      await store.initialize(); // Ensure the store is initialized
    } catch (err) {
      error = "Failed to initialize the embedding store.";
      console.error(err);
    }
  });

  const login = () => {
    setPage(pages.CHATBOT);
  };

  type NavItem = { id: string; label: string; admin?: boolean };

  // `!error` gated the guide pages before; kept, but as data instead of markup
  // repeated once per button.
  $: navItems = [
    { id: pages.HOME, label: "Accueil" },
    { id: pages.CHATBOT, label: "Chat" },
    { id: pages.SETTINGS, label: "Paramètres", admin: true },
    { id: pages.DOCUMENTS, label: "Documents", admin: true },
    ...(!error
      ? [
          { id: pages.PDF, label: "Guide" },
          { id: pages.VIDEO, label: "Vidéo" },
        ]
      : []),
  ] as NavItem[];

  $: visibleNav = navItems.filter(
    (item) => !item.admin || $userStore?.role === ROLES.ADMIN,
  );
</script>

<!-- `h-dvh` + `min-h-0` on the middle child: without a bounded height the chat
     scroller had nothing to constrain it and the composer drifted off-screen. -->
<main class="flex h-dvh w-full flex-col overflow-hidden bg-surface text-foreground">
  {#if page != pages.HOME}
    <header
      class="flex shrink-0 flex-wrap items-center gap-x-1 gap-y-2 border-b border-border bg-surface-raised px-4 py-3 md:px-6"
    >
      <!-- Link to home, not an action: kept off the `.btn` scale but padded to
           the same 32px rhythm as the nav items so the focus ring is actually
           visible around the text. `-my-1` keeps the header height unchanged. -->
      <button
        type="button"
        on:click={() => setPage(pages.HOME)}
        class="-my-1 mr-1.5 truncate rounded-lg px-1.5 py-1 text-base font-semibold tracking-tight text-foreground transition-colors hover:bg-surface-sunken hover:text-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
        aria-label="Retour à l'accueil"
        title={import.meta.env.VITE_TITLE || "Démo"}
      >
        {import.meta.env.VITE_TITLE || "Démo"}
      </button>

      <nav class="flex min-w-0 flex-1 flex-wrap items-center gap-1" aria-label="Navigation principale">
        {#each visibleNav as item (item.id)}
          <button
            type="button"
            on:click={() => setPage(item.id)}
            aria-current={page === item.id ? "page" : undefined}
            class={`btn btn-sm ${
              page === item.id
                ? "bg-primary-soft text-primary hover:bg-primary-soft"
                : "btn-ghost"
            }`}
          >
            {item.label}
          </button>
        {/each}
      </nav>

      <ThemeToggle />
    </header>
  {/if}

  <!-- `flex flex-col` is load-bearing: it makes this a flex container so the
       active page's `flex-1` (Chatbot) gets a bounded height. As a plain block
       the child's `flex-1` was ignored, Chatbot grew to its content, its
       `overflow-y-auto` message list never scrolled, and `overflow-hidden` here
       made the overflowing messages unreachable. -->
  <div class="flex min-h-0 flex-1 flex-col overflow-hidden">
    {#if page == pages.HOME}
      <div class="page">
        <Accueil chat={login} />

        <Login {login} />
      </div>
    {:else if page == pages.SETTINGS}
      <PromptManager />
    {:else if page == pages.DOCUMENTS}
      <Document />
    {:else if page == pages.PDF}
      <!-- svelte-pdf pulls the whole PDF.js runtime (~3.7 MB with the worker).
           It used to be a static import, so every visitor paid for it on the home
           page even without opening this tab. -->
      {#await Promise.all([
        import("svelte-pdf"),
        import("./assets/guide_utilisateur.pdf"),
      ])}
        <p class="page-pad text-muted">Chargement du guide…</p>
      {:then [module, guide]}
        <div class="page-pad">
          <h1 class="page-title">Guide utilisateur</h1>
          <p class="page-sub">
            Documentation de l'application, au format PDF.
          </p>
          <div class="mt-4 h-[calc(100%-5rem)] overflow-auto">
            <module.default showBorder={false} scale={1.5} url={guide.default} />
          </div>
        </div>
      {/await}
    {:else if page == pages.VIDEO}
      <!-- The 33 MB guide is only fetched when the page is opened. -->
      {#await import("./assets/GuideVideo.mp4").then((m) => m.default)}
        <p class="page-pad text-muted">Chargement de la vidéo…</p>
      {:then videoUrl}
        <div class="page page-pad">
          <h1 class="page-title">Vidéo de présentation</h1>
          <p class="page-sub">
            Présentation vidéo de l'application.
          </p>
          <video
            class="mt-4 w-full max-w-4xl rounded-lg border border-border bg-surface-raised"
            controls
            preload="metadata"
          >
            <source src={videoUrl} type="video/mp4" />
            Votre navigateur ne prend pas en charge la lecture vidéo.
          </video>
        </div>
      {/await}
    {:else if page == pages.CHATBOT}
      <Chatbot />
    {/if}
  </div>

  <Footer />
</main>
