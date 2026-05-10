import asyncio
import uuid
from datetime import datetime
from agents import AgentSystem, ConversationSession, Message

async def main():
    agent_system = AgentSystem()
    session_id = str(uuid.uuid4())
    session = ConversationSession(id=session_id)
    
    print("-" * 50)
    print("CloudDash Support CLI - Agent Cluster Online")
    print("-" * 50)
    print(f"Session started: {session_id}")
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break
            
        # User Msg
        session.history.append(Message(
            role="user", 
            content=user_input, 
            sender="USER", 
            timestamp=datetime.now().strftime("%H:%M:%S")
        ))
        
        print(f"[*] Triaging and processing via {session.active_agent}...")
        
        # Logic
        if session.active_agent == "TRIAGE":
            t_res = await agent_system.run_triage(session, user_input)
            session.active_agent = t_res.get("intent", "TECHNICAL")
            
        response = ""
        if session.active_agent == "TECHNICAL":
            response = await agent_system.run_technical(session, user_input)
        elif session.active_agent == "BILLING":
            response = await agent_system.run_billing(session, user_input)
        elif session.active_agent == "ESCALATION":
            response = await agent_system.run_escalation(session, user_input)
            
        print(f"\n[{session.active_agent} AGENT]: {response}")
        
if __name__ == "__main__":
    asyncio.run(main())
