import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [svelte(), tailwindcss()],
  server: {
    // The Flask API runs separately in development.
    proxy: {
      "/chat-sse": "http://127.0.0.1:3000",
      "/chat": "http://127.0.0.1:3000",
      "/query": "http://127.0.0.1:3000",
      "/documents": "http://127.0.0.1:3000",
      "/empty-documents": "http://127.0.0.1:3000",
      "/initialize": "http://127.0.0.1:3000",
    },
  },
  build: {
    // Vite warns by default at 500 kB; the real problem was a single 700 kB
    // chunk, so keep the bar and let it be measured.
    chunkSizeWarningLimit: 500,
  },
});
