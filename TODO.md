# TODO - Suivi du Projet Chatbot

Dernière mise à jour : 30 septembre 2026

---

## 1. Tâches Réalisées

### Sécurité & Architecture Backend
- [x] Sécurisation des clés LLM : retrait des appels directs côté client et migration complète vers le backend Flask.
- [x] Gestion centralisée des fournisseurs LLM avec chaîne de fallback (Mistral -> Google Gemini -> OpenRouter -> Ollama local).
- [x] Streaming SSE robuste via la route `/chat-sse` avec transmission préalable du badge provider réel (`provider -> text -> [DONE]`).
- [x] Gestion de l'interruption côté client et libération immédiate du worker Flask à l'annulation.
- [x] Migration de l'environnement Python vers `uv` / `pyproject.toml` (suppression de `requirements.txt`).

### Design Système & Interface Utilisateur (UI)
- [x] Définition des tokens sémantiques et thèmes clair / sombre homogènes dans `src/app.css`.
- [x] Création des classes partagées pour l'échelle visuelle :
  - Boutons : `.btn`, `.btn-md`, `.btn-sm`, `.btn-xs`, `.btn-lg`, `.btn-icon`, `.btn-icon-lg`
  - Variantes : `.btn-primary`, `.btn-outline`, `.btn-ghost`, `.btn-danger`
  - Formulaires & Conteneurs : `.field`, `.select-field`, `.card`, `.page`, `.page-pad`, `.page-title`, `.page-sub`, `.section-label`, `.progress`
- [x] Styles de blocs de code prism/markdown toujours sombres (`--code-surface`, `--code-border`, etc.).
- [x] Traduction intégrale de l'interface en français.
- [x] Harmonisation de toutes les pages :
  - `src/App.svelte` (shell, navigation principale, pages PDF et vidéo)
  - `src/lib/Accueil.svelte` (vue d'accueil responsive)
  - `src/lib/Login.svelte` (carte de connexion et gestion des erreurs)
  - `src/lib/Document.svelte` & `src/atoms/Uploader.svelte` (recherche et découpage/import RAG)
  - `src/lib/PromptManager.svelte`, `PromptEditor.svelte`, `PromptDisplayer.svelte` (gestion des prompts et sélecteur de langue)
  - `src/atoms/Modal.svelte` (support Escape, rôles ARIA, `tabindex` et backdrop cliquable)

### Expérience Chat & Scroll
- [x] Correction de l'auto-scroll pendant le streaming via `tick()` et détection de proximité (`STICK_THRESHOLD_PX = 96`).
- [x] Arrêt immédiat de l'auto-follow si l'utilisateur remonte manuellement pendant la génération.
- [x] Support des caractères UTF-8 accentués découpés à travers les paquets SSE.

### Nettoyage du Codebase
- [x] Suppression des composants et assets de démo inutilisés (`src/lib/Counter.svelte`, `src/assets/svelte.svg`).
- [x] Suppression de tous les résidus de classes de couleurs codées en dur au profit des tokens sémantiques.

---

## 2. En Cours / Prochaines Étapes Immédiates

- [ ] **Optimisation du bundle frontend** : Configurer `build.rollupOptions.output.manualChunks` ou l'import dynamique pour découper les chunks JS dépassant 500 kB (signalé par Vite).
- [ ] **Nettoyage des avertissements d'accessibilité (A11y)** :
  - `src/atoms/Displayer.svelte` : Associer des gestionnaires clavier aux clics d'action média/seek.
  - `src/App.svelte` : Fournir un fichier de sous-titres `.vtt` pour la vidéo de guide (ou gérer la piste manquante selon le besoin).
- [ ] **Nettoyage des paramètres d'appel** : Supprimer l'envoi de `providerName` par `Chatbot.svelte` si Flask ne l'exploite plus, ou le réintégrer formellement si la sélection dynamique côté client est requise.

---

## 3. Améliorations Futures (Backlog)

### Fonctionnalités
- [ ] **Gestion avancée des sessions/historiques** : Permettre d'exporter, d'importer ou de purger les historiques de chat depuis l'interface utilisateur.
- [ ] **Amélioration du RAG** : Intégrer la prévisualisation des sources de documents citées directement dans les bulles de réponse du chat.
- [ ] **Indicateurs de latence/métriques** : Afficher le temps de réponse (TTFT) et le débit de tokens générés.

### Tests & CI/CD
- [ ] **Intégration des tests E2E Headless** : Automatiser la suite de tests de non-régression (scroll, streaming, thèmes, responsive 375 px) dans un pipeline CI (ex: GitHub Actions).
- [ ] **Mocks serveurs de test** : Ajouter des fixtures de tests pour simuler les réponses des API LLM externes sans dépendance réseau.
