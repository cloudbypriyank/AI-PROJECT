# AI Customer Support Multi-Agent Architecture

```mermaid
graph TD

    A[User Input] --> B{Triage Agent}

    B -->|Technical Query| C[Tech Support Agent + RAG]
    B -->|Billing Query| D[Billing Agent]
    B -->|Need Human Support| E[Escalation Agent]

    C --> F[(Vector Database / Knowledge Base)]
    D --> G[(Account & Billing Mock API)]

    F --> H[Final AI Response + TTS]
    G --> H

    E --> I[(JSON Audit Logs)]

    %% Styles
    classDef agent fill:#c9e4ff,stroke:#1e88e5,stroke-width:2px,color:#000;
    classDef data fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef process fill:#dcedc8,stroke:#689f38,stroke-width:2px,color:#000;
    classDef output fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000;

    %% Apply Classes
    class B,C,D,E agent;
    class F,G data;
    class I process;
    class H output;
```

---

## Flow Explanation

1. User sends a query.
2. Triage Agent identifies the query type.
3. Based on intent:
   - Technical issues → Tech Agent + RAG
   - Billing issues → Billing Agent
   - Human support needed → Escalation Agent
4. Tech Agent retrieves context from the Knowledge Base.
5. Billing Agent interacts with Account/Billing API.
6. Final response is generated with optional Text-to-Speech (TTS).
7. Escalated requests are stored in JSON audit logs.

---

## Components Used

| Component | Purpose |
|---|---|
| Triage Agent | Routes user requests |
| Tech Agent | Handles technical questions |
| RAG Pipeline | Retrieves contextual knowledge |
| Billing Agent | Handles billing/account queries |
| Escalation Agent | Transfers complex cases to humans |
| Vector DB | Stores embeddings and documents |
| Mock API | Simulates billing/account system |
| JSON Logs | Stores escalated conversations |
| TTS | Converts response to voice |

---

## Tech Stack Suggestion

- Python
- FastAPI
- LangChain / LlamaIndex
- OpenAI / Gemini APIs
- ChromaDB / FAISS
- ElevenLabs / gTTS
- Streamlit or React Frontend