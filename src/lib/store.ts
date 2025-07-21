import { writable } from "svelte/store";
import type { PromptEntity } from "../domain/entities/prompt.ts";
import PROMPT from "../../data/prompts.json";
import { LocalStorage } from "../infra/storage/localStorage.js";

export const promptStorage = new LocalStorage<PromptEntity>("prompt", PROMPT);
export const promptStore = writable<PromptEntity[]>(promptStorage.getAll());
export const promptSystemStore = writable<string>("");
export const providersStore = writable<string[]>([]);
export const providerStore = writable<string>("");
export const language = writable<string>("fr-FR");
