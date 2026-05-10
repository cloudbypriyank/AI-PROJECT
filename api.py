from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from agents import AgentSystem, ConversationSession, Message
import asyncio
from datetime import datetime

app = FastAPI(title="CloudDash Support API")
agent_system = AgentSystem()
sessions = {}

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    s_id = request.session_id or str(uuid.uuid4())
    if s_id not in sessions:
        sessions[s_id] = ConversationSession(id=s_id)
    
    session = sessions[s_id]
    
    # User message
    user_msg = Message(
        role="user", 
        content=request.message, 
        sender="USER", 
        timestamp=datetime.now().isoformat()
    )
    session.history.append(user_msg)
    
    # Triage
    if session.active_agent == "TRIAGE":
        t_res = await agent_system.run_triage(session, request.message)
        session.active_agent = t_res.get("intent", "TECHNICAL")
    
    # Agent Run
    response_text = ""
    if session.active_agent == "TECHNICAL":
        response_text = await agent_system.run_technical(session, request.message)
    elif session.active_agent == "BILLING":
        response_text = await agent_system.run_billing(session, request.message)
    elif session.active_agent == "ESCALATION":
        response_text = await agent_system.run_escalation(session, request.message)
        
    # Append response
    agent_msg = Message(
        role="assistant",
        content=response_text,
        sender=session.active_agent,
        timestamp=datetime.now().isoformat()
    )
    session.history.append(agent_msg)
    
    return {
        "session_id": s_id,
        "response": response_text,
        "agent": session.active_agent
    }

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
