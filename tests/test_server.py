from fastapi.testclient import TestClient

import server


def setup_function() -> None:
    """Reset knowledge base before each test."""
    server.kb = server.KnowledgeBase()


def test_upload_and_mask() -> None:
    client = TestClient(server.app)
    data = b"My email is user@example.com"
    files = {"file": ("policy.txt", data, "text/plain")}
    resp = client.post("/upload", files=files)
    assert resp.status_code == 200

    answer = client.get("/ask", params={"q": "email"}).json()
    assert answer["answer"] == "My email is [EMAIL]"
    assert answer["sources"] == ["policy.txt"]


def test_insufficient_data() -> None:
    client = TestClient(server.app)
    data = b"Customer data must be stored for 3 years"
    files = {"file": ("policy.txt", data, "text/plain")}
    client.post("/upload", files=files)

    # Query unrelated to the document should trigger insufficient data
    answer = client.get("/ask", params={"q": "What is the phone number?"}).json()
    assert answer == {"answer": "資料不足", "sources": []}

