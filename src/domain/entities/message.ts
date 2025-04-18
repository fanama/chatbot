export interface MessageEntity {
  sender: string;
  text: string;
  provider?: string;
}

export interface Input {
  text: string;
  history?: MessageEntity[];
  model?: string;
}

export interface Response {
  text: string;
  provider: string;
}
