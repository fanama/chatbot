import { mount } from "svelte";
import "./app.css";
import App from "./App.svelte";
import { themeStorage } from "./lib/store";

/* Applied before `mount()` on purpose: doing it in `onMount` painted one frame
   of the light theme first, which reads as a flash on every navigation. */
document.documentElement.classList.toggle("dark", themeStorage.getAll()[0] === "dark");

const app = mount(App, {
  target: document.getElementById("app")!,
});

export default app;
