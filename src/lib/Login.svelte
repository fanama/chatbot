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

<div class="h-full bg-blue-900 pt-80">
  <div class="w-full p-8 bg-blue-800">
    {#if error}
      <div
        class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4"
        role="alert"
      >
        <span class="block sm:inline">{error}</span>
      </div>
    {/if}
    <button
      type="button"
      class="text-3xl font-bold text-white bg-transparent border-none cursor-pointer p-0 m-0 focus:outline-none"
      aria-label="Retour à l'accueil"
    >
      {import.meta.env.VITE_TITLE || "Demo"}
    </button>

    <form class="space-y-6" on:submit|preventDefault={handleLogin}>
      <h2 class="text-left text-2xl text-white font-bold mb-6">Connexion</h2>

      <div class="mb-4">
        <input
          id="username"
          name="username"
          required
          class="appearance-none bg-white rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
          placeholder="Username"
          bind:value={username}
        />
      </div>

      <div class="mb-4">
        <input
          id="password"
          name="password"
          type="password"
          required
          class="appearance-none bg-white rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
          placeholder="Password"
          bind:value={password}
        />
      </div>

      <div>
        <button
          type="submit"
          class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Se connecter
        </button>
      </div>
    </form>
  </div>
</div>
