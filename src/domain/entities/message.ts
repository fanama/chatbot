export interface MessageEntity {
  sender: string;
  text: string;
  provider?: string;
  context?: string[];
  insertToStore?: () => void
}

export interface Input {
  text: string;
  image?: string;
  history?: MessageEntity[];
  model?: string;
  providerName?: string;
  useVectorstore?: boolean;
  /** Cancels an in-flight request (stop button, new message, unmount). */
  signal?: AbortSignal;
  stream?: (chunk: string) => void;
  /** Fired as soon as the backend announces the answering model. */
  onProvider?: (provider: string) => void;
}

export interface Response {
  text: string;
  summary?: string;
  provider: string;
}
