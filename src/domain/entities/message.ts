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
  useVectorestore?: boolean;
  stream?: (chunk: string) => void
}

export interface Response {
  text: string;
  summary?: string;
  provider: string;
}
