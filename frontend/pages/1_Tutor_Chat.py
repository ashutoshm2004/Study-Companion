import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import streamlit as st
from frontend.api_client import chat
from frontend.styles import apply_styles, page_header, active_doc_chip

st.set_page_config(page_title="Tutor Chat", page_icon="💬", layout="wide")
apply_styles()
page_header("💬", "Tutor Chat", "Ask anything — explained like a patient, knowledgeable teacher")

doc_id = st.session_state.get("doc_id")
if not doc_id:
    st.markdown('<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:2rem;text-align:center;color:#666">⬆ No document selected — go to Home and upload one</div>', unsafe_allow_html=True)
    st.stop()

active_doc_chip(st.session_state.get("doc_name", doc_id), doc_id)

c1, c2 = st.columns([1, 5])
with c1:
    show_src = st.toggle("Sources", False)
with c2:
    if st.button("Clear chat", key="clear"):
        st.session_state.chat_history = []
        st.rerun()

st.divider()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if not st.session_state.chat_history:
    st.markdown('<div style="text-align:center;padding:3rem 0;color:#333;font-size:.95rem">Start by asking a question about your document…</div>', unsafe_allow_html=True)

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and show_src and msg.get("sources"):
            with st.expander(f"📎 {len(msg['sources'])} sources used"):
                for i, s in enumerate(msg["sources"], 1):
                    st.markdown(f'<span class="chip">Chunk {i}</span> <span class="chip">Page {s.get("page","?")}</span> <span class="chip">Score {s.get("relevance_score",0):.2f}</span>', unsafe_allow_html=True)
                    st.caption(s["text"][:400] + "...")

if prompt := st.chat_input("Ask about your document…"):
    with st.chat_message("user"):
        st.markdown(prompt)
    history_api = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]
    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                res = chat(doc_id, prompt, history_api)
                st.markdown(res["response"])
                st.markdown(f'<span class="chip">🔢 {res.get("tokens_used",0)} tokens</span>', unsafe_allow_html=True)
                if show_src and res.get("sources"):
                    with st.expander(f"📎 {len(res['sources'])} sources"):
                        for i, s in enumerate(res["sources"], 1):
                            st.markdown(f'<span class="chip">Chunk {i}</span> <span class="chip">Page {s.get("page","?")}</span> <span class="chip">Score {s.get("relevance_score",0):.2f}</span>', unsafe_allow_html=True)
                            st.caption(s["text"][:400] + "...")
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.session_state.chat_history.append({"role": "assistant", "content": res["response"], "sources": res.get("sources",[])})
            except Exception as e:
                st.error(f"Error: {e}")