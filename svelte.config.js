import { mdsvex } from 'mdsvex';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
// import sveltePreprocess from 'svelte-preprocess'; // Uncomment if you want to add svelte-preprocess too

export default {
  extensions: ['.svelte', '.md'],
  preprocess: [
    mdsvex({
      highlight: {
        highlighter: async (code, lang) => {
          const { default: prism } = await import('prismjs');
          const language = prism.languages[lang];
          return language ? prism.highlight(code, language, lang) : code;
        }
      }
    }),
    vitePreprocess(),
    // sveltePreprocess(), // Uncomment if you want this as well
  ],
};
