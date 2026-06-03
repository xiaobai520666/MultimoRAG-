"""Local E2E test — run before pushing. Uses only stdlib."""
import json, time, sys, os, urllib.request, urllib.error

API = "http://localhost:8000/api/v1"
passed = 0
failed = 0


def api_call(method, path, body=None):
    """Make API call, return parsed JSON."""
    url = f"{API}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"code": -1, "message": str(e), "data": None}


def check(name, resp_or_code, extra=""):
    global passed, failed
    if isinstance(resp_or_code, dict):
        code = resp_or_code.get("code", -1)
    else:
        code = resp_or_code
    if code == 0:
        print(f"  PASS: {name} {extra}")
        passed += 1
        return True
    else:
        print(f"  FAIL: {name} (code={code}) {extra}")
        failed += 1
        return False


def upload_file(kb_id, filepath):
    """Multipart file upload using http.client."""
    import http.client

    boundary = "----TestBoundary12345"
    host = "localhost"
    port = 8000

    with open(filepath, "rb") as f:
        file_content = f.read()

    filename = os.path.basename(filepath)
    body_lines = [
        f"--{boundary}",
        f"Content-Disposition: form-data; name=\"knowledge_id\"",
        "",
        kb_id,
        f"--{boundary}",
        f"Content-Disposition: form-data; name=\"file\"; filename=\"{filename}\"",
        "Content-Type: text/plain",
        "",
    ]
    header = "\r\n".join(body_lines).encode() + b"\r\n"
    footer = f"\r\n--{boundary}--\r\n".encode()
    body = header + file_content + footer

    conn = http.client.HTTPConnection(host, port, timeout=60)
    conn.request(
        "POST",
        "/api/v1/ingestion/upload",
        body=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    resp = conn.getresponse()
    raw = resp.read().decode()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"code": -1, "message": f"Invalid JSON: {raw[:100]}", "data": None}


print("======= Local E2E Test =======")

# 1. Health
print("1. Health Check")
check("Health", api_call("GET", "/health")["code"])

# 2. Create KB
print("2. Create Knowledge Base")
kb = api_call("POST", "/knowledge", {"name": "Local E2E", "description": "dev test"})
kb_id = (kb.get("data") or {}).get("id")
check("Create KB", kb["code"], f"id={kb_id}")

# 3. Upload
print("3. Upload File")
content = "MultimoRAG是多模态RAG问答系统。它支持文本、图片、音频三种内容类型的知识库构建与智能问答。系统自动解析文件分块嵌入并存入向量库。用户提问时检索相关知识片段生成带引用的回答。"
with open("test_upload.txt", "w", encoding="utf-8") as f:
    f.write(content)
upload = upload_file(kb_id, "test_upload.txt")
check("Upload", upload)

# 4. Wait
print("4. Waiting for processing...")
time.sleep(3)

# 5. Chat
print("5. RAG Chat")
chat = api_call("POST", "/chat", {
    "knowledge_id": kb_id, "message": "MultimoRAG是什么？", "history": [],
})
chat_data = chat.get("data") or {}
check("Chat", chat["code"], chat_data.get("reply", "")[:60] or "")

# 6. Search
print("6. Search")
sr = api_call("POST", "/retrieval/search", {
    "knowledge_id": kb_id, "query": "多模态", "top_k": 3,
})
n = len(sr.get("data", {}).get("results", []))
check("Search", sr["code"], f"({n} results)")

# 7. Agent
print("7. Agent")
ag = api_call("POST", "/agent/execute", {
    "knowledge_id": kb_id, "message": "总结知识库",
})
check("Agent", ag["code"])

# 8. Delete
print("8. Delete")
check("Delete", api_call("DELETE", f"/knowledge/{kb_id}")["code"])

# 9. Clean
print("9. Clean Verify")
lst = api_call("GET", "/knowledge?page=1&size=10")
total = lst.get("data", {}).get("total", -1)
check("Clean", 0 if total == 0 else -1, f"total={total}")

# Cleanup
if os.path.exists("test_upload.txt"):
    os.remove("test_upload.txt")

print(f"\n======= {passed} passed, {failed} failed =======")
sys.exit(0 if failed == 0 else 1)
