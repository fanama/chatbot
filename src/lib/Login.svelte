<script lang="ts">
  import { LocalStorage } from "../infra/storage/localStorage";
  import type { UserEntity } from "../domain/entities/user";
  import { userStore } from "./store";

  const userLocalStorage = new LocalStorage<UserEntity>("users", []);

  let username = "";
  let password = "";

  let error = "";

  export let login: () => void;

  function handleLogin() {
    if (!username) {
      error = "Veuillez remplir tous les champs";
      return;
    }
    if (username == "admin" && password == "1234") {
      userLocalStorage.save([{ name: username, role: "ADMIN" }]);
      userStore.set({ name: username, role: "ADMIN" });
    } else {
      userStore.set({ name: username, role: "USER" });

      userLocalStorage.save([{ name: username, role: "USER" }]);
    }
    login();
  }
</script>

<!-- `pb-14` so the card no longer finishes flush against the footer: the
     features section above ends on its own padding and left none here. -->
<div class="px-4 pb-14 md:px-6">
  <div class="card mx-auto w-full max-w-md p-6 md:p-8">
    {#if error}
      <div
        class="mb-4 rounded-lg border border-danger/40 bg-danger-soft px-4 py-3 text-sm text-danger"
        role="alert"
      >
        <span class="block">{error}</span>
      </div>
    {/if}

    <form class="space-y-4" on:submit|preventDefault={handleLogin}>
      <div class="mb-2 text-center">
        <h2 class="text-xl font-semibold tracking-tight text-foreground">
          Connexion
        </h2>
        <p class="mt-1 text-sm text-muted">Connectez-vous à votre compte</p>
      </div>

      <div class="space-y-4">
        <div>
          <label
            for="username"
            class="mb-1.5 block text-sm font-medium text-foreground"
            >Nom d'utilisateur</label
          >
          <input
            id="username"
            name="username"
            required
            class="field"
            placeholder="Entrez votre nom d'utilisateur"
            autocomplete="username"
            bind:value={username}
          />
        </div>

        <div>
          <label
            for="password"
            class="mb-1.5 block text-sm font-medium text-foreground"
            >Mot de passe</label
          >
          <input
            id="password"
            name="password"
            type="password"
            required
            class="field"
            placeholder="Entrez votre mot de passe"
            autocomplete="current-password"
            bind:value={password}
          />
        </div>
      </div>

      <div>
        <button type="submit" class="btn btn-primary w-full">
          Se connecter
        </button>
      </div>
    </form>
  </div>
</div>
