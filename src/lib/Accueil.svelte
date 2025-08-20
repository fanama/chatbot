<script lang="ts">
  export let chat: () => void;
</script>

<main class="h-full w-full bg-gray-50">
  <section
    class="hero py-24 px-4 text-center bg-gradient-to-r from-indigo-600 to-indigo-800 text-white"
  >
    <h1 class="text-4xl md:text-5xl font-bold mb-6">Bienvenue !</h1>
    <p class="text-xl md:text-2xl mb-10 max-w-2xl mx-auto">
      Votre assistant conversationnel intelligent
    </p>
    <button
      class="bg-white text-indigo-600 hover:bg-indigo-100 font-bold py-3 px-8 cursor-pointer rounded-full transition duration-300 shadow-md hover:shadow-lg"
      on:click={() => chat()}
    >
      Let's chat !
    </button>
  </section>

  <section class="features py-16 px-4">
    <h2 class="text-3xl font-bold text-center mb-16 text-indigo-800">
      Nos fonctionnalités
    </h2>
    <div
      class="feature-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto"
    >
      <div
        class="feature p-8 bg-white rounded-xl shadow-lg hover:shadow-xl transition duration-300 transform hover:-translate-y-1"
      >
        <div class="text-indigo-600 mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-10 w-10 mx-auto"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
        </div>
        <h3 class="text-xl font-semibold mb-4 text-indigo-800">
          Réponses instantanées
        </h3>
        <p class="text-gray-600">
          Obtenez des réponses en temps réel à vos questions
        </p>
      </div>
      <div
        class="feature p-8 bg-white rounded-xl shadow-lg hover:shadow-xl transition duration-300 transform hover:-translate-y-1"
      >
        <div class="text-indigo-600 mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-10 w-10 mx-auto"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            />
          </svg>
        </div>
        <h3 class="text-xl font-semibold mb-4 text-indigo-800">
          Apprentissage automatique
        </h3>
        <p class="text-gray-600">Notre IA s'améliore avec chaque interaction</p>
      </div>
      <div
        class="feature p-8 bg-white rounded-xl shadow-lg hover:shadow-xl transition duration-300 transform hover:-translate-y-1"
      >
        <div class="text-indigo-600 mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-10 w-10 mx-auto"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-5"
            />
          </svg>
        </div>
        <h3 class="text-xl font-semibold mb-4 text-indigo-800">Multilingue</h3>
        <p class="text-gray-600">Disponible dans plusieurs langues</p>
      </div>
    </div>
  </section>
</main>
