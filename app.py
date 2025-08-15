import os
from dotenv import load_dotenv
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# ---------- 1) Config & Keys ----------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY is missing. Add it to your .env file.")
    st.stop()

# ---------- 2) Page UI ----------
st.set_page_config(
    page_title="AI Q&A (LangChain + Streamlit)", page_icon="💬", layout="centered"
)
st.title("💬 AI-Powered Q&A")
st.caption("Built with LangChain + OpenAI + Streamlit")

# Sidebar settings
with st.sidebar:
    st.subheader("Settings")
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.3, 0.1)
    model_name = st.selectbox(
        "OpenAI model",
        # use current chat models; gpt-4o-mini is fast & capable
        ["gpt-4o-mini", "gpt-4o"],
        index=0,
    )
    st.markdown("---")
    st.caption("Your API key is loaded from .env and never sent to GitHub.")

# ---------- 3) Session State for Memory ----------
# We keep chain & memory in Streamlit session, so it persists across user turns.
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True)

if "chain" not in st.session_state:
    llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model_name=model_name,
        temperature=temperature,
    )
    st.session_state.chain = ConversationChain(
        llm=llm,
        memory=st.session_state.memory,
        verbose=False,
    )


# If user changes model/temperature mid-session, rebuild the chain
def rebuild_chain():
    llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model_name=model_name,
        temperature=temperature,
    )
    st.session_state.chain = ConversationChain(
        llm=llm,
        memory=st.session_state.memory,
        verbose=False,
    )


# Detect config changes (simple approach: rebuild every render in case options changed)
rebuild_chain()

# ---------- 4) Chat UI ----------
# Display prior messages from memory
if st.session_state.memory.chat_memory.messages:
    for msg in st.session_state.memory.chat_memory.messages:
        role = "User" if msg.type == "human" else "AI"
        with st.chat_message(role):
            st.write(msg.content)

# Input box at the bottom
user_input = st.chat_input("Ask a question...")
if user_input:
    # Show user message
    with st.chat_message("User"):
        st.write(user_input)

    # Run the chain (LangChain keeps the chat history in memory)
    try:
        ai_response = st.session_state.chain.run(user_input)
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

    # Show AI response
    with st.chat_message("AI"):
        st.write(ai_response)

# ---------- 5) Optional: Memory viewer for learning ----------
with st.expander("🧠 Show raw conversation memory (for learning)"):
    msgs = st.session_state.memory.chat_memory.messages
    st.write(msgs)
