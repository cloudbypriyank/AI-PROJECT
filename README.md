
# CloudDash: Multi-Agent Autonomous Support Cluster

**Project Status:** Production-Ready | **Developer:** Priyank Pawar

This repository contains a production-grade multi-agent support system designed for **CloudDash**. It leverages **Gemini 3.1 Flash-Lite** and a **RAG (Retrieval-Augmented Generation)** pipeline to handle Technical, Billing, and Escalation workflows with zero hallucination.

## 🎥 Video Demonstration

**[Watch the System Walkthrough & Demo](https://www.google.com/search?q=GOOGLE_DRIVE_VIDEO_DEMO_URL)**

---

## 🚀 Key Features

* **Multi-Agent Orchestration**: Autonomous routing between Triage, Technical, Billing, and Escalation specialists.
* **Context-Aware RAG**: Knowledge Base integration with mandatory `[KB-XXX]` source citations.
* **Audit Logging (Observability)**: Every interaction, intent classification, and handover is recorded in `logs/conversation_traces.json`.
* **Voice-Enabled UI**: Integrated browser-based Text-to-Speech with a professional female voice profile.
* **Portability**: Support for both `.env` configuration and in-app API key injection.

---

## 🛠️ Tech Stack

* **Language**: Python 3.11+.
* **Framework**: Streamlit (UI) & LlamaIndex (RAG Orchestration).
* **LLM**: Google Gemini 3.1 Flash-Lite.
* **Embeddings**: HuggingFace BAAI/bge-small-en-v1.5.

---

## 🏃 Local Setup

**Prerequisites:** Python installed on your system.

1. **Clone & Install Dependencies:**
```bash
pip install -r requirements.txt

```


2. **Environment Configuration:**
Create a `.env` file in the root directory or enter the key directly in the app sidebar:
```env
GEMINI_API_KEY=your_gemini_api_key_here

```


3. **Launch the Console:**
```bash
streamlit run app.py

```



---

## 📂 Project Structure

* `agents.py`: Core logic for AgentSystem, Handover Protocol, and Logging.
* `app.py`: Streamlit frontend and conversation state management.
* `knowledge_base/`: Structured JSON storage for cloud integration articles.
* `logs/`: Persistent storage for conversation traces and session audits.

---

## 🧪 Testing Scenarios

To verify the system's robustness, try these test queries:

* **Technical**: *"How do I fix a 'Connection Timed Out' error on my 3rd AWS node?"*
* **Guardrails**: *"Can I integrate my smart coffee machine with CloudDash?"* (Tests KB failure handling)
* **Escalation**: *"I am frustrated and want to speak with a human."* (Tests handover logic)

---