export interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface CitationItem {
  chunk_id: string;
  document_id: string;
  text: string;
  score: number;
}

export interface ChatRequest {
  knowledge_id: string;
  message: string;
  history: Message[];
}

export interface ChatResponse {
  reply: string;
  citations: CitationItem[];
  usage: Record<string, any>;
}

export interface Knowledge {
  id: string;
  name: string;
  description: string;
  created_at: string;
  document_count: number;
}

export interface IngestTask {
  task_id: string;
  status: string;
  chunk_count?: number;
}
