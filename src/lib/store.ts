import { writable } from "svelte/store";
import type { PromptEntity } from "../domain/entities/prompt.ts";
import PROMPT from "../../data/prompts.json";
import { LocalStorage } from "../infra/storage/localStorage.js";

export const promptStorage = new LocalStorage<PromptEntity>("prompt", PROMPT);

export const promptStore = writable<PromptEntity[]>(promptStorage.getAll());
