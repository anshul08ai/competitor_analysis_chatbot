
import streamlit as st
from pathlib import Path
import sys

utils_path = Path.cwd().parent / "src" / "graph"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

from workflow import compiled

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Chatbot Interface")

if 'output' not in st.session_state:
    st.session_state.output = None

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

## Query ##
prompt = st.chat_input("Type your message...")


if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        response=compiled.invoke({'query':prompt})['output']
        for chunk in response:
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
 