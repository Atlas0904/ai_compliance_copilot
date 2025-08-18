# ai_compliance_copilot

1. AI 合規文件助理（Compliance Copilot）
	•	功能：
	•	上傳公司政策 / 金管會法規 / ISO 文件 → 系統建立 RAG 知識庫。
	•	使用者可提問，例如「這份合約裡有沒有 GDPR 風險？」。
	•	系統會回覆 回答 + 引用來源 + 高亮可能的敏感資訊。
	•	能展現的點
	1.	前後端全端設計：
	•	前端：React chat UI（含文件上傳、對話紀錄）
	•	後端：FastAPI + OpenAI API / Llama
	2.	合規需求：
	•	加入 稽核模式：輸出回答時必須附引用，若不足以回答 → 回「資料不足」。
	•	支援自動遮罩 Email / ID / Phone（敏感資訊處理 pipeline）。
	3.	RAG & Prompt 工程：
	•	Prompt 模板：規定回答格式、引用段落。
	•	使用向量資料庫（FAISS / Milvus / Weaviate）。
	4.	部署 & 安全：
	•	Docker 化 → 部署在 AWS/GCP。
	•	加上 API Key 保護、Rate Limiting。
	•	使用 HTTPS 與日誌存證。

👉 面試 demo：
上傳一份 PDF 法規，問「客戶資料保存多久？」
→ 系統回答「依第 3.2 條，需保存 3 年（來源：文件第 5 頁）」，同時標註 檢測到 Email，自動遮罩。
