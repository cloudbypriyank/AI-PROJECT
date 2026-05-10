import contextlib
import os
import json
import uuid
import streamlit.components.v1 as components
import math
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from datetime import datetime
from typing import List, Dict, Any, Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from transformers import AutoTokenizer
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.gemini import Gemini

import os
import json
from datetime import datetime



load_dotenv()

model = genai.GenerativeModel('gemini-3.1-flash-lite')


Settings.llm = Gemini(
    model_name="models/gemini-3.1-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1,
)
print("LLM set successfully!")

# # set tokenizer to match LLM
# Settings.tokenizer = AutoTokenizer.from_pretrained(
#     "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# )
# print("Tokenizer set successfully!")

# set the embed model
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)
print("System initialized successfully!")




def speak_text(text):
    # Sanitize: Remove markdown, quotes, and newlines
    clean_text = text.replace('"', "'").replace('\n', ' ').replace('\r', ' ').replace('*', '')
    
    components.html(f"""
        <script>
            function startSpeaking() {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{clean_text}");
                var voices = window.speechSynthesis.getVoices();
                
                // Try to find a female-sounding voice (Microsoft Zira, Google US English, etc.)
                // This searches for 'female', 'Zira', 'Samantha', or 'Google US English'
                var selectedVoice = voices.find(voice => 
                    voice.name.includes('Zira') || 
                    voice.name.includes('Samantha') || 
                    voice.name.includes('Google US English') ||
                    voice.name.includes('Female')
                );
                if (selectedVoice) {{
                    msg.voice = selectedVoice;
                }}
                msg.lang = 'en-US';
                msg.rate = 1.0;
                window.speechSynthesis.speak(msg);
            }}

            if (window.speechSynthesis.onvoiceschanged !== undefined) {{
                window.speechSynthesis.onvoiceschanged = startSpeaking;
            }}

            startSpeaking();
            document.body.onclick = startSpeaking;
            
        </script>
    """, height=0)

class Message(BaseModel):
    role: str
    content: str
    sender: str
    timestamp: str

class ConversationSession(BaseModel):
    id: str 
    active_agent: str = "TRIAGE"
    history: List[Message] = []
    context: Dict[str, Any] = {"entities": {}, "handover_history": []}

class KBArticle(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: List[str]



    
class AgentSystem:
    def __init__(self):

        self.llm = Settings.llm
        self.embed_model = Settings.embed_model
        self.kb_articles: List[KBArticle] = []
        self.kb_embeddings: List[Dict[str, Any]] = []
        self._load_kb()
    
    def log_event(self, session: ConversationSession, event_type: str, details: dict):
        # 1. Define the path (make sure it's relative to your main script)
        base_path = os.path.dirname(os.path.abspath(__file__)) 
        log_dir = os.path.join(base_path, "logs")
        log_file = os.path.join(log_dir, "conversation_traces.json")
    
        # 2. CREATE THE FOLDER if it doesn't exist (Section 3.1)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
        # 3. Create the log entry with a unique Trace ID (Section 3.2)
        log_entry = {
            "trace_id": session.id,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "active_agent": session.active_agent,
            **details
        }

        print(f"DEBUG: Logged {event_type} to {log_file}")
        print(f"DEBUG: Log entry: {log_entry}")
    
        # 4. Read/Write with proper file closing
        logs = []
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
                
        logs.append(log_entry)
    
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=4)
            f.flush() # Forces the data to the disk immediately

    def _load_kb(self):
        kb_path = "knowledge_base/articles.json"
        if os.path.exists(kb_path):
            with open(kb_path, "r") as f:
                data = json.load(f)
                self.kb_articles = [KBArticle(**a) for a in data]
            
            print(f"Generating embeddings for {len(self.kb_articles)} articles...")
            for article in self.kb_articles:
                text = f"{article.title}\n{article.content}\nTags: {','.join(article.tags)}"
                emb = self.embed_model.get_text_embedding(text)
                self.kb_embeddings.append({"id": article.id, "embedding": emb})
        else:
            print("Knowledge base not found!")

    def _get_similarity(self, v1, v2):
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_v1 = math.sqrt(sum(a * a for a in v1))
        norm_v2 = math.sqrt(sum(b * b for b in v2))
        if norm_v1 == 0 or norm_v2 == 0:
            return 0
        return dot_product / (norm_v1 * norm_v2)

    def retrieve(self, query: str, limit: int = 1) -> List[KBArticle]:
        query_emb = self.embed_model.get_text_embedding(query)
        scores = []
        for item in self.kb_embeddings:
            score = self._get_similarity(query_emb, item["embedding"])
            scores.append((item["id"], score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        top_ids = [s[0] for s in scores[:limit]]
        return [a for a in self.kb_articles if a.id in top_ids]

    def run_triage(self, session: ConversationSession, user_msg: str):
        prompt = f"""
        You are the Triage Agent for CloudDash.
        Classify the intent:
        - TECHNICAL: alert config, dashboard errors, API, cloud integrations.
        - BILLING: invoices, price plans, upgrades, payment failures.
        - ESCALATION: human support requests, high priority complaints, policy exceptions.

        User Message: "{user_msg}"
        Respond ONLY with a JSON object:
        {{ "intent": "TECHNICAL" | "BILLING" | "ESCALATION", "reason": "...", "entities": {{}} }}
        """
        response = self.llm.complete(prompt)
        print("\n\n")
        print("response: ", response.text)
        print("\n\n")
        try:
            # Cleaning the response in case Gemini adds markdown backticks
            clean_json = response.text.strip().replace("```json", "").replace("```", "").strip()
            result =  json.loads(clean_json)
            if "entities" in result:
                session.context["entities"].update(result["entities"])

            self.log_event(session, "INTENT_CLASSIFICATION", {
                "detected_intent": result.get("intent"),
                "reasoning": result.get("reason"),
                "entities": result.get("entities")
            })
            return result
        except Exception as e:
            print(f"Triage JSON error: {e}")
            return {"intent": "TECHNICAL", "reason": "parsing error"}



    def run_technical(self, session: ConversationSession, user_msg: str):
        docs = self.retrieve(user_msg)
        entities = session.context.get("entities", {})
        context = "\n\n".join([f"[Source: {d.id}] {d.title}: {d.content}" for d in docs])
        
        prompt = f"""
        Role: CloudDash Technical Support Agent.
        Known User Info: {entities}
        Context: {context}
        History: {session.history[-1].content if session.history else ""}
        User: "{user_msg}"

        Rules:
        - Use KB content only.
        - Cite [KB-XXX] sources.
        - If not found, suggest manual ESCALATION.
        """
        response = self.llm.complete(prompt)

        self.log_event(session, "AGENT_RESPONSE", {
            "agent_type": "TECHNICAL",
            "input": user_msg,
            "output": response.text,
            "sources": [d.id for d in docs]
        })
        return response.text

    def run_billing(self, session: ConversationSession, user_msg: str):
        prompt = f"""
        Role: CloudDash Billing Agent.
        Plans: Basic (Free, 3 nodes), Pro ($49/mo, 50 nodes), Enterprise (Custom).
        User: "{user_msg}"
        History: {session.history[-1].content if session.history else ""}
        """
        response = self.llm.complete(prompt)

        self.log_event(session, "AGENT_RESPONSE", {
            "agent_type": "BILLING",
            "input": user_msg,
            "output": response.text,
            "sources": []
        })
        return response.text

    def run_escalation(self, session: ConversationSession, user_msg: str):
        summary = "\n".join([f"{m.sender}: {m.content}" for m in session.history])
        prompt = f"""
        Role: CloudDash Escalation Specialist.
        A human is joining. Summarize the issue and reassure the customer.
        Full context: {summary}
        """
        response = self.llm.complete(prompt)

        self.log_event(session, "AGENT_RESPONSE", {
            "agent_type": "ESCALATION",
            "input": user_msg,
            "output": response.text
        })
        return response.text



    # Example of where to update context during a handover
    def handle_handover(self, session: ConversationSession, target_agent: str, reason: str):
        # 1. Update the active agent state 

        source_agent = session.active_agent
        session.active_agent = target_agent
    
        # 2. Update context for logging requirements 
        self.log_event(session, "HANDOVER", {
            "from": source_agent,
            "to": target_agent,
            "reason": reason,
            "context_snapshot": session.context["entities"].copy()   
        })
        # Append the handover event to history
        session.history.append(Message(
            role="system",
            content=f"Handled handover to {target_agent} due to: {reason}",
            sender="HANDOVER",
            timestamp=datetime.now().strftime("%H:%M:%S")
        ))

 