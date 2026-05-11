graph TD
    A[User Input] --> B{Triage Agent}
    B -->|Technical| C[Tech Agent + RAG]
    B -->|Billing| D[Billing Agent]
    B -->|Human| E[Escalation Agent]
    C --> F[Knowledge Base]
    D --> G[Account Mock API]
    F --> H[Final Response + TTS]
    G --> H
    E --> I[JSON Audit Log]
    
    classDef agent fill:#c9e4ff,stroke:#1e88e5,stroke-width:2px;
    classDef data fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef process fill:#dcedc8,stroke:#689f38,stroke-width:2px;
    classDef output fill:#ffe0b2,stroke:#e65100,stroke-width:2px;

    class B,C,D,E agent;
    class F,G data;
    class I process;
    class H output;