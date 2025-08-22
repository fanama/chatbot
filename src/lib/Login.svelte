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

<div
  class="bg-white bg-opacity-10 backdrop-filter backdrop-blur-md rounded-lg shadow-xl w-full p-6 md:p-8"
>
  {#if error}
    <div
      class="bg-red-100 bg-opacity-20 border border-red-400 text-red-300 px-4 py-3 rounded mb-4 text-sm"
      role="alert"
    >
      <span class="block">{error}</span>
    </div>
  {/if}

  <form class="space-y-4 md:space-y-6" on:submit|preventDefault={handleLogin}>
    <div class="text-center mb-6">
      <h2 class="text-2xl md:text-3xl font-bold">Connexion</h2>
      <p class="text-opacity-80 mt-1">Connectez-vous à votre compte</p>
    </div>

    <div class="space-y-4">
      <div>
        <label
          for="username"
          class="block text-sm font-medium text-white text-opacity-80 mb-1"
          >Nom d'utilisateur</label
        >
        <input
          id="username"
          name="username"
          required
          class="w-full px-3 py-2 placeholder-gray-400 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
          placeholder="Entrez votre nom d'utilisateur"
          bind:value={username}
        />
      </div>

      <div>
        <label
          for="password"
          class="block text-sm font-medium text-white text-opacity-80 mb-1"
          >Mot de passe</label
        >
        <input
          id="password"
          name="password"
          type="password"
          required
          class="w-full px-3 py-2 placeholder-gray-400 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
          placeholder="Entrez votre mot de passe"
          bind:value={password}
        />
      </div>
    </div>

    <div>
      <button
        type="submit"
        class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition duration-150 ease-in-out"
      >
        Se connecter
      </button>
    </div>
  </form>
</div>
