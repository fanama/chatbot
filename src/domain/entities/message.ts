export interface MessageEntity {
  sender: string;
  text: string;
  provider?: string;
  context?: string[];
}

export interface Input {
  text: string;
  history?: MessageEntity[];
  model?: string;
  providerName?: string;
}

export interface Response {
  text: string;
  provider: string;
}
