from asyncio import constants
import streamlit as st
import uuid
import asyncio
from datetime import datetime
from agents import AgentSystem, Message, ConversationSession
from agents import speak_text

# Page Config
st.set_page_config(page_title="CloudDash Support Console", layout="wide")


# Custom Styling (Elegant Dark Streamlit)
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #0E1117;
    }
    .stApp {
        background-color: #ffffff;
        color: #0E1117;
    }
    .agent-header {
        font-family: monospace;
        font-size: 10px;
        letter-spacing: 2px;
        color: #FF4B4B;
        margin-bottom: 5px;
    }
    .msg-user {
        background-color: #ffffff;
        border-left: 3px solid #60A5FA;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .msg-agent {
        background-color: #ffffff;
        border-left: 3px solid #FF4B4B;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_agent():
    return AgentSystem()

# Initialize Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "agent_system" not in st.session_state:
    st.session_state.agent_system = load_agent()
if "session" not in st.session_state:
    st.session_state.session = ConversationSession(id=st.session_state.session_id)



if "pending_speech" in st.session_state and st.session_state.pending_speech:
    speak_text(st.session_state.pending_speech)
    st.session_state.pending_speech = None
# Sidebar
with st.sidebar:
    st.title("S CloudDash")
    speak_toggle = st.toggle("Speak", value=False,)
    
    st.markdown("---")
    st.subheader("System Status")
    st.write(f"**Active Agent:** {st.session_state.session.active_agent}")
    st.write(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
    
    st.markdown("---")
    st.subheader("Quick Ops") 

    


    if st.button("New Support Trace", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.session = ConversationSession(id=st.session_state.session_id)
        st.rerun()

# Main Chat
st.title("Unified Operation Stream")
st.caption("Multi-Agent Autonomous Support Cluster | v1.2-Python")

# Display History
for msg in st.session_state.session.history:
    style_class = "msg-user" if msg.role == "user" else "msg-agent"
    sender_label = "[USER_CLI]" if msg.role == "user" else f"[STREAM_{msg.sender}_AGENT]"
    
    st.markdown(f"""
    <div class="{style_class}">
        <div class="agent-header">{sender_label} ({msg.timestamp})</div>
        <div>{msg.content}</div>
    </div>
    """, unsafe_allow_html=True)

# Input
user_input = st.chat_input("Enter command or question...")

if user_input:
    # Add User Message
    user_msg = Message(
        role="user", 
        content=user_input, 
        sender="USER", 
        timestamp=datetime.now().strftime("%H:%M:%S")
    )
    st.session_state.session.history.append(user_msg)
    
    # Rerun to show user message immediately
    st.rerun()

# Processing Logic (Check if last message needs reply)
if st.session_state.session.history and st.session_state.session.history[-1].role == "user":
    with st.spinner(f"Processing via {st.session_state.session.active_agent} Agent..."):
        user_msg_text = st.session_state.session.history[-1].content
        agent = st.session_state.agent_system
        session = st.session_state.session
        
        # 1. Triage
        if session.active_agent == "TRIAGE":
            t_res = agent.run_triage(session, user_msg_text)
            session.active_agent = t_res.get("intent", "TECHNICAL")
            st.info(f"Routed to Specialist: {session.active_agent}")
        
        # 2. Specialist Run
        response_text = ""
        try:
            if session.active_agent == "TECHNICAL":
                st.badge(label="TECHNICAL",icon = "⚠️")
                response_text = agent.run_technical(session, user_msg_text)
            elif session.active_agent == "BILLING":
                st.badge(label="BILLING", icon = "💰")
                response_text = agent.run_billing(session, user_msg_text)
            elif session.active_agent == "ESCALATION":
                st.badge(label="ESCALATION",icon = "🚨")
                response_text = agent.run_escalation(session, user_msg_text)

            # Check for auto-escalation
            if "escalate" in response_text.lower() or "human" in response_text.lower():
                if session.active_agent != "ESCALATION":
                    session.active_agent = "ESCALATION"
                    response_text = agent.run_escalation(session, user_msg_text)

            if speak_toggle:
                st.session_state.pending_speech = response_text
            # Add Agent Reply
            agent_msg = Message(
                role="assistant",
                content=response_text,
                sender=session.active_agent,
                timestamp=datetime.now().strftime("%H:%M:%S")
            )
            session.history.append(agent_msg)
            st.rerun()
        except Exception as e:
            st.error(f"Agent Logic Error: {str(e)}")
