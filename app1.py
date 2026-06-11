import streamlit as st
from workflow import workflow, retrive_all_thread, checkpoint
from langchain_core.messages import HumanMessage, AIMessage
import uuid
import html as _html

st.set_page_config(
    page_title="LangGraph Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background-color: #111318 !important;
    color: #E2E4EA !important;
    font-family: 'Inter', sans-serif !important;
}

#MainMenu, footer, header,
[data-testid="stSidebar"],
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] { display: none !important; }

.block-container {
    padding: 0 0 5rem 0 !important;
    max-width: 100% !important;
    width: 100% !important;
}

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2A2D37; border-radius: 3px; }

/* ── NAVBAR ── */
.navbar {
    position: sticky;
    top: 0;
    z-index: 50;
    background: #111318;
    border-bottom: 1px solid #1E2029;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.8rem 2rem;
}
.navbar-left { display: flex; align-items: center; gap: 12px; }
.navbar-logo {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #6C63FF, #4F97FF);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
}
.navbar-title {
    font-size: 0.92rem;
    font-weight: 600;
    color: #E2E4EA;
    line-height: 1;
    margin-bottom: 3px;
}
.navbar-thread {
    font-size: 0.65rem;
    font-family: 'JetBrains Mono', monospace;
    color: #3A3E50;
    letter-spacing: 0.04em;
}

/* ── NEW CHAT BUTTON ── */
[data-testid="stButton"] > button {
    background: transparent !important;
    border: 1px solid #2A2D37 !important;
    color: #8B8FA8 !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.4rem 1rem !important;
    transition: border-color 0.15s, color 0.15s, background 0.15s !important;
    white-space: nowrap !important;
}
[data-testid="stButton"] > button:hover {
    border-color: #6C63FF !important;
    color: #A29CFF !important;
    background: rgba(108,99,255,0.07) !important;
}

/* ── CHAT AREA ── */
.chat-area {
    max-width: 820px;
    width: 100%;
    margin: 0 auto;
    padding: 1.4rem 1.5rem 0;
}

/* ── EXPANDER (conversation history only) ── */
[data-testid="stExpander"] {
    background: #16181F !important;
    border: 1px solid #1E2029 !important;
    border-radius: 12px !important;
    margin-bottom: 0.6rem !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    background: #16181F !important;
    color: #8B8FA8 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.65rem 1rem !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary:hover { color: #E2E4EA !important; }
[data-testid="stExpander"] summary svg  { fill: #8B8FA8 !important; }
[data-testid="stExpanderDetails"] {
    background: #16181F !important;
    padding: 0.5rem 0.75rem 0.8rem !important;
    border-top: 1px solid #1E2029 !important;
}
[data-testid="stExpanderDetails"] .stButton > button {
    background: #111318 !important;
    border: 1px solid #1E2029 !important;
    border-radius: 7px !important;
    color: #8B8FA8 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    padding: 0.38rem 0.75rem !important;
    width: 100% !important;
    text-align: left !important;
    margin-bottom: 0.25rem !important;
}
[data-testid="stExpanderDetails"] .stButton > button:hover {
    background: #1E2029 !important;
    border-color: #6C63FF !important;
    color: #A29CFF !important;
}
.active-thread-label {
    display: block;
    background: rgba(108,99,255,0.1);
    border: 1px solid rgba(108,99,255,0.25);
    border-radius: 7px;
    padding: 0.35rem 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #A29CFF;
    margin-bottom: 0.25rem;
}
.expander-empty {
    font-size: 0.75rem; color: #3A3E50;
    font-family: 'JetBrains Mono', monospace;
    text-align: center; padding: 0.5rem 0;
}

/* ── BUBBLES ── */
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] { display: none !important; }
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    gap: 0 !important;
    max-width: 820px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
[data-testid="stChatMessage"] > div:last-child { width: 100% !important; }
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] .stText {
    font-size: 0.9rem !important;
    line-height: 1.72 !important;
    color: #E2E4EA !important;
    margin: 0 !important;
}

.bubble-row { display: flex; width: 100%; margin: 0.5rem 0; padding: 0 1.5rem; }
.bubble-row.user      { justify-content: flex-end; }
.bubble-row.assistant { justify-content: flex-start; }

.bubble {
    max-width: 68%;
    padding: 0.75rem 1.15rem;
    font-size: 0.9rem;
    line-height: 1.72;
    white-space: pre-wrap;
    word-break: break-word;
}
.bubble.user {
    background: linear-gradient(135deg, #5B53EE, #7B74FF);
    color: #fff;
    border-radius: 18px 18px 4px 18px;
    box-shadow: 0 2px 12px rgba(108,99,255,0.25);
}
.bubble.assistant {
    background: #16181F;
    color: #D8DBE8;
    border: 1px solid #1E2029;
    border-radius: 18px 18px 18px 4px;
}

/* ── EMPTY STATE ── */
.empty-state {
    text-align: center;
    padding: 4.5rem 2rem 2rem;
    max-width: 820px;
    margin: 0 auto;
}
.empty-icon-wrap {
    width: 56px; height: 56px;
    border-radius: 16px;
    background: rgba(108,99,255,0.1);
    border: 1px solid rgba(108,99,255,0.2);
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
    margin: 0 auto 1rem;
}
.empty-state h3 { color: #8B8FA8; font-size: 1rem; font-weight: 500; margin: 0 0 0.35rem; }
.empty-state p  { font-size: 0.78rem; color: #3A3E50; margin: 0; line-height: 1.65; }

/* ── CHAT INPUT ── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
[data-testid="stChatInputContainer"],
[data-testid="stChatInputContainer"] > div,
[data-testid="stChatInputContainer"] > div > div {
    background: #111318 !important;
}
[data-testid="stBottom"] {
    background: linear-gradient(to top, #111318 80%, transparent) !important;
    padding: 0.5rem 0 1rem !important;
}
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div,
[data-testid="stChatInput"] > div > div > div {
    background: #16181F !important;
}
[data-testid="stChatInput"] {
    border: 1px solid #2A2D37 !important;
    border-radius: 14px !important;
    max-width: 820px !important;
    margin: 0 auto !important;
    transition: border-color .15s, box-shadow .15s !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #6C63FF !important;
    box-shadow: 0 0 0 3px rgba(108,99,255,0.12) !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] textarea:active {
    background: #16181F !important;
    background-color: #16181F !important;
    color: #E2E4EA !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    caret-color: #6C63FF !important;
    -webkit-text-fill-color: #E2E4EA !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #3A3E50 !important; }
[data-testid="stChatInput"] textarea:-webkit-autofill,
[data-testid="stChatInput"] textarea:-webkit-autofill:hover,
[data-testid="stChatInput"] textarea:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0 1000px #16181F inset !important;
    -webkit-text-fill-color: #E2E4EA !important;
    background-color: #16181F !important;
}
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #6C63FF, #4F97FF) !important;
    border-radius: 10px !important;
    border: none !important;
    transition: opacity .15s !important;
}
[data-testid="stChatInput"] button:hover { opacity: 0.85 !important; }

[data-testid="stHorizontalBlock"] { align-items: center !important; gap: 0 !important; }

[data-testid="stAlert"] {
    background: rgba(108,99,255,0.08) !important;
    border: 1px solid rgba(108,99,255,0.22) !important;
    border-radius: 9px !important;
    color: #A29CFF !important;
    font-size: 0.78rem !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def generate_thread():
    return uuid.uuid4()

def reset_chat():
    thread_id = generate_thread()
    st.session_state["thread_id"] = thread_id
    add_thread_id(thread_id)
    st.session_state["messages"] = []

def add_thread_id(thread_id):
    if thread_id not in st.session_state["thread_history"]:
        st.session_state["thread_history"].append(thread_id)

def load_conversation(thread_id):
    state = workflow.get_state(
        config={"configurable": {"thread_id": str(thread_id)}}
    )
    return state.values.get("messages", [])

def short_id(tid):
    return str(tid)[:8] + "…"

def render_bubble(role: str, content: str):
    safe = _html.escape(content)
    st.markdown(
        f'<div class="bubble-row {role}"><div class="bubble {role}">{safe}</div></div>',
        unsafe_allow_html=True,
    )


# ── Session state ─────────────────────────────────────────────────────────────
if "messages"       not in st.session_state: st.session_state["messages"]       = []
if "thread_id"      not in st.session_state: st.session_state["thread_id"]      = generate_thread()
if "thread_history" not in st.session_state:
    st.session_state["thread_history"] = retrive_all_thread(checkpoint) or []

add_thread_id(st.session_state["thread_id"])

# ══════════════════════════════════════════════════════════════════════════════
# NAVBAR
# ══════════════════════════════════════════════════════════════════════════════
col_brand, col_btn = st.columns([10, 1])
with col_brand:
    st.markdown(f"""
    <div class="navbar">
        <div class="navbar-left">
            <div class="navbar-logo">💬</div>
            <div>
                <div class="navbar-title">LangGraph Chat</div>
                <div class="navbar-thread">thread · {short_id(st.session_state["thread_id"])}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_btn:
    st.markdown("<div style='padding-top:0.6rem'>", unsafe_allow_html=True)
    if st.button("＋ New", key="new_chat_top"):
        reset_chat()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHAT AREA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="chat-area">', unsafe_allow_html=True)

with st.expander("🗂  Conversation history", expanded=False):
    if not st.session_state["thread_history"]:
        st.markdown('<div class="expander-empty">No conversations yet.</div>', unsafe_allow_html=True)
    else:
        for thread_id in reversed(st.session_state["thread_history"]):
            is_active = thread_id == st.session_state["thread_id"]
            label = short_id(thread_id)
            if is_active:
                st.markdown(
                    f'<div class="active-thread-label">▶ {label} <span style="opacity:0.4;font-size:0.65rem;">current</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button(label, key=f"thread_{thread_id}"):
                    msgs = load_conversation(thread_id)
                    st.session_state["messages"] = [
                        {"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": m.content}
                        for m in msgs
                    ]
                    st.session_state["thread_id"] = thread_id
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MESSAGES
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state["messages"]:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon-wrap">💬</div>
        <h3>Start a conversation</h3>
        <p>Ask anything to get started.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state["messages"]:
        render_bubble(msg["role"], msg["content"])

# ══════════════════════════════════════════════════════════════════════════════
# CHAT INPUT
# ══════════════════════════════════════════════════════════════════════════════
config = {"configurable": {"thread_id": str(st.session_state["thread_id"])}}
user_input = st.chat_input("Message LangGraph…")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    render_bubble("user", user_input)

    with st.chat_message("assistant"):
        bot_reply = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in workflow.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages",
            )
        )
    st.session_state["messages"].append({"role": "assistant", "content": bot_reply})

    st.rerun()