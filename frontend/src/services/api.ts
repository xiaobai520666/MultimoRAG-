const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const json = await res.json();

  if (json.code !== 0) {
    throw new Error(json.message || "请求失败");
  }

  return json.data as T;
}

export async function get<T>(path: string): Promise<T> {
  return request<T>(path, { method: "GET" });
}

export async function post<T>(path: string, body: any): Promise<T> {
  return request<T>(path, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function uploadFile(file: File, knowledgeId: string) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("knowledge_id", knowledgeId);

  const res = await fetch(`${API_BASE}/ingestion/upload`, {
    method: "POST",
    body: formData,
  });

  const json = await res.json();
  if (json.code !== 0) {
    throw new Error(json.message || "上传失败");
  }
  return json.data;
}
