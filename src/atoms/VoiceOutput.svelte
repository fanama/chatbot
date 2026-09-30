<script lang="ts">
  import { onDestroy, onMount } from "svelte";
  import { language } from "../lib/store";

  export let textValue = "";

  const synth = typeof window !== "undefined" ? window.speechSynthesis : null;
  let isSpeaking = false;
  let voices: SpeechSynthesisVoice[] = [];

  function loadVoices() {
    if (!synth) return;
    voices = synth.getVoices();
  }

  onMount(() => {
    loadVoices();
    if (synth && synth.onvoiceschanged !== undefined) {
      synth.onvoiceschanged = loadVoices;
    }
  });

  onDestroy(() => {
    if (synth) synth.cancel();
  });

  /**
   * Nettoie le Markdown pour la synthèse vocale :
   * - Ignore les blocs de code complexes (incompréhensibles à l'écoute)
   * - Retire les balises markdown (*, _, #, ~, liens, code inline)
   */
  function cleanMarkdownForSpeech(text: string): string {
    return text
      .replace(/```[\s\S]*?```/g, "") // Blocs de code
      .replace(/`([^`]+)`/g, "$1") // Code en ligne -> texte simple
      .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1") // Liens [texte](url) -> texte
      .replace(/[*_~#>]/g, "") // Symboles de mise en forme
      .replace(/\n{2,}/g, "\n")
      .trim();
  }

  /**
   * Sélectionne la meilleure voix disponible pour la langue active :
   * Privilégie les voix naturelles/neurales (Google, Microsoft Neural, Apple Premium, etc.)
   */
  function getBestVoice(targetLang: string): SpeechSynthesisVoice | null {
    if (!voices.length) return null;

    const prefix = targetLang.split("-")[0].toLowerCase();
    const matchingVoices = voices.filter(
      (v) =>
        v.lang.toLowerCase() === targetLang.toLowerCase() ||
        v.lang.toLowerCase().startsWith(prefix),
    );

    if (!matchingVoices.length) return null;

    // Critères pour repérer les voix haute qualité/naturelles selon les navigateurs/OS
    const naturalKeywords = [
      "natural",
      "neural",
      "premium",
      "enhanced",
      "online",
      "google",
      "siri",
      "thomas",
      "audrey",
      "amelie",
    ];

    const best = matchingVoices.find((v) =>
      naturalKeywords.some((kw) => v.name.toLowerCase().includes(kw)),
    );

    return best || matchingVoices.find((v) => !v.localService) || matchingVoices[0];
  }

  function startSpeaking() {
    if (!synth) return;

    synth.cancel();

    const textToSpeak = cleanMarkdownForSpeech(textValue);
    if (!textToSpeak) return;

    // Découpage en phrases pour un rythme naturel et éviter les limites de buffer
    const sentences = textToSpeak
      .split(/(?<=[.?!;:])\s+|\n+/)
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    if (!sentences.length) return;

    const selectedVoice = getBestVoice($language);

    sentences.forEach((sentence, index) => {
      const utterance = new SpeechSynthesisUtterance(sentence);
      utterance.lang = $language;
      if (selectedVoice) {
        utterance.voice = selectedVoice;
      }

      // Vitesse et pitch légers pour adoucir la diction
      utterance.rate = 1.0;
      utterance.pitch = 1.0;

      // La lecture n'est considérée finie que lorsque la dernière phrase se termine
      if (index === sentences.length - 1) {
        utterance.onend = () => {
          isSpeaking = false;
        };
        utterance.onerror = () => {
          isSpeaking = false;
        };
      }

      synth.speak(utterance);
    });

    isSpeaking = true;
  }

  function stopSpeaking() {
    if (!synth) return;
    synth.cancel();
    isSpeaking = false;
  }
</script>

<div class="flex items-center gap-1">
  <button
    type="button"
    class="btn btn-xs btn-ghost"
    on:click={startSpeaking}
    disabled={!textValue.trim() || isSpeaking}
    aria-label="Lire le message à voix haute"
    title="Lire à voix haute"
  >
    <svg
      class="h-3.5 w-3.5"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <path d="M4 14v-2a8 8 0 0 1 16 0v2" />
      <path
        d="M4 14h2.5a1.5 1.5 0 0 1 1.5 1.5v2A1.5 1.5 0 0 1 6.5 19H6a2 2 0 0 1-2-2z"
      />
      <path
        d="M20 14h-2.5a1.5 1.5 0 0 0-1.5 1.5v2a1.5 1.5 0 0 0 1.5 1.5h.5a2 2 0 0 0 2-2z"
      />
    </svg>
    <span>Écouter</span>
  </button>
  <button
    type="button"
    class="btn btn-xs btn-ghost"
    on:click={stopSpeaking}
    disabled={!isSpeaking}
    aria-label="Arrêter la lecture"
    title="Arrêter"
  >
    <svg
      class="h-3.5 w-3.5"
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
    >
      <rect x="5" y="5" width="10" height="10" rx="1.5" />
    </svg>
  </button>
</div>
