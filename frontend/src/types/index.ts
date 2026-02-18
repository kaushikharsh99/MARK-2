export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  pinned: boolean;
  createdAt: number;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  tokenCount?: number;
}

export interface AppSettings {
  model: string;
  temperature: number;
  maxTokens: number;
  contextWindow: number;
  ragEnabled: boolean;
  asrEnabled: boolean;
  ttsEnabled: boolean;
  streamResponses: boolean;
  developerMode: boolean;
}

export type AppStatus = "online" | "generating" | "error" | "loading";
