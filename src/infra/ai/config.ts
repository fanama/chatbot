/**
 * Resolve the backend base URL from the environment.
 *
 * A malformed or relative VITE_URL would send the conversation (and the
 * documents found by the RAG) to an arbitrary host, so the value is validated
 * here rather than trusted.
 */
function resolveBaseUrl(): string {
  const raw = (import.meta.env.VITE_URL || "").trim();

  if (!raw) {
    // Same origin: the reverse proxy forwards /chat-sse, /query, /documents.
    return "";
  }

  let parsed: URL;
  try {
    parsed = new URL(raw);
  } catch {
    console.warn(
      `VITE_URL is not a valid absolute URL, falling back to same-origin. Got: ${raw}`,
    );
    return "";
  }

  if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
    console.warn(
      `VITE_URL must use http or https, got ${parsed.protocol}. Falling back to same-origin.`,
    );
    return "";
  }

  return raw.replace(/\/+$/, "");
}

export const BACKEND_URL = resolveBaseUrl();

/** A provider that aborts an in-flight request when the signal fires. */
export class AbortedError extends Error {
  constructor(message = "Request aborted") {
    super(message);
    this.name = "AbortedError";
  }
}

export function isAbortError(error: unknown): boolean {
  return (
    error instanceof AbortedError ||
    (typeof error === "object" &&
      error !== null &&
      (error as { name?: string }).name === "AbortError")
  );
}
