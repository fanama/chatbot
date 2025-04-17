export interface MessageEntity {
  sender: string;
  text: string;
}

export interface Input {
  text: string;
  history?: MessageEntity[];
  model?: string;
}
