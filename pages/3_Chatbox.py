"""
pages/3_Chatbox.py
Simple Chatbox dengan Qwen2.5:3B via Ollama
Tanpa konteks data dulu — basic Q&A
"""

# pyrefly: ignore [missing-import]
import streamlit as st
import requests
from components.ui import render_navbar, COLORS, SPACING

st.set_page_config(page_title="AI Chatbox | DataBuddy", page_icon="💬", layout="wide")

render_navbar()

st.markdown(f"""
<div style="margin-bottom: {SPACING['lg']};">
    <h1 style="
        font-size: 2.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        line-height: 1.2;
        letter-spacing: -0.02em;
    ">💬 AI Chatbox</h1>
    <p style="color: #64748b; margin-top: 0.5rem; font-size: 1.15rem; font-weight: 400; line-height: 1.6;">
        Chat dengan Qwen2.5:3B — Local LLM via Ollama
    </p>
</div>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════
# CONFIG
# ═════════════════════════════════════════════════════════════════════

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"

# ═════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═════════════════════════════════════════════════════════════════════

if "messages" not in st.session_state:
    st.session_state.messages = []

# ═════════════════════════════════════════════════════════════════════
# SIDEBAR - SETTINGS
# ═════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### ⚙️ Settings")

    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.slider("Max Tokens", 100, 2000, 500, 100)

    st.markdown("---")
    st.markdown(f"**Model:** {MODEL}")
    st.markdown(f"**URL:** {OLLAMA_URL}")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("""
    ### 📝 Tips
    - Tanya apa saja dalam Bahasa Indonesia
    - Untuk coding, tanya spesifik
    - Temperature rendah = lebih fokus
    - Temperature tinggi = lebih kreatif
    """)

# ═════════════════════════════════════════════════════════════════════
# MAIN CHAT AREA
# ═════════════════════════════════════════════════════════════════════

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ═════════════════════════════════════════════════════════════════════
# USER INPUT
# ═════════════════════════════════════════════════════════════════════

if prompt := st.chat_input("Tanya apa saja..."):

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Berpikir..."):
            try:
                response = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        }
                    },
                    timeout=120
                )
                response.raise_for_status()
                result = response.json()

                assistant_message = result.get("response", "Maaf, ada error.")

            except requests.exceptions.ConnectionError:
                assistant_message = "❌ **Ollama tidak terkoneksi.** Pastikan Ollama service jalan: `brew services start ollama`"

            except Exception as e:
                assistant_message = f"❌ **Error:** {e}"

        st.markdown(assistant_message)

    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
