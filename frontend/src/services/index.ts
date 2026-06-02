import { get, post, del, uploadFile } from "./api";
import { Knowledge, ChatRequest, ChatResponse } from "./types";

export { uploadFile };

export async function listKnowledge(page = 1, size = 10) {
  return get<{ items: Knowledge[]; total: number }>(`/knowledge?page=${page}&size=${size}`);
}

export async function createKnowledge(name: string, description = "") {
  return post<Knowledge>("/knowledge", { name, description });
}

export async function deleteKnowledge(id: string) {
  return del<{}>(`/knowledge/${id}`);
}

export async function sendMessage(request: ChatRequest) {
  return post<ChatResponse>("/chat", request);
}

export async function searchKnowledge(knowledgeId: string, query: string, topK = 5) {
  return post("/retrieval/search", {
    knowledge_id: knowledgeId,
    query,
    top_k: topK,
  });
}
