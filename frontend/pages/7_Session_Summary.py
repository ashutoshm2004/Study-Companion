import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import streamlit as st
from frontend.api_client import get_session_summary
from frontend.styles import apply_styles, page_header, active_doc_chip

st.set_page_config(page_title="Session Summary", page_icon="📊", layout="wide")
apply_styles()
page_header("📊", "Session Summary", "Smart recap — strong areas, weak spots, and next steps")

doc_id = st.session_state.get("doc_id")
if not doc_id:
    st.markdown('<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:2rem;text-align:center;color:#666">⬆ No document selected</div>', unsafe_allow_html=True)
    st.stop()
active_doc_chip(st.session_state.get("doc_name", doc_id), doc_id)

history = st.session_state.get("chat_history",[])
if len(history) < 2:
    st.markdown(f'<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:2rem;text-align:center;color:#555">Need at least 2 messages in Tutor Chat. You have {len(history)}.</div>', unsafe_allow_html=True)
    st.stop()

st.markdown(f'<span class="chip">💬 {len(history)} messages</span>', unsafe_allow_html=True)
if "quiz_score" in st.session_state:
    total = len(st.session_state.get("quiz_qs",[]))
    st.markdown(f'<span class="chip">📝 Quiz: {st.session_state["quiz_score"]}/{total}</span>', unsafe_allow_html=True)
st.markdown("")

quiz_scores = None
if "quiz_score" in st.session_state:
    quiz_scores = [{"score": st.session_state["quiz_score"], "total": len(st.session_state.get("quiz_qs",[]))}]

if st.button("Generate Session Summary", use_container_width=True):
    with st.spinner("Analysing session…"):
        try:
            api_history = [{"role": m["role"], "content": m["content"]} for m in history]
            st.session_state["ss_data"] = get_session_summary(doc_id, api_history, quiz_scores)
        except Exception as e:
            st.error(str(e))

data = st.session_state.get("ss_data")
if not data:
    st.markdown('<div style="text-align:center;padding:3rem;color:#333">Click above to generate your session summary.</div>', unsafe_allow_html=True)
    st.stop()

st.markdown("")
st.markdown(f'<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:1.4rem 1.8rem;margin-bottom:1.5rem"><p style="color:#e2e8f0;font-size:1rem;margin:0;line-height:1.7">{data.get("summary","")}</p></div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    topics = data.get("topics_covered",[])
    if topics:
        st.markdown('<p style="color:#555;font-size:.75rem;font-weight:600;letter-spacing:2px;text-transform:uppercase">Topics Covered</p>', unsafe_allow_html=True)
        for t in topics: st.markdown(f'<p style="color:#94a3b8;font-size:.9rem">◆ {t}</p>', unsafe_allow_html=True)
    strong = data.get("strong_areas",[])
    if strong:
        st.markdown('<p style="color:#4ade8066;font-size:.75rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;margin-top:1rem">Strong Areas</p>', unsafe_allow_html=True)
        for s in strong: st.markdown(f'<p style="color:#888;font-size:.9rem"><span style="color:#4ade80">✓</span> {s}</p>', unsafe_allow_html=True)
with c2:
    weak = data.get("weak_areas",[])
    if weak:
        st.markdown('<p style="color:#f8717166;font-size:.75rem;font-weight:600;letter-spacing:2px;text-transform:uppercase">Needs Work</p>', unsafe_allow_html=True)
        for w in weak: st.markdown(f'<p style="color:#888;font-size:.9rem"><span style="color:#f87171">⚠</span> {w}</p>', unsafe_allow_html=True)
    nxt = data.get("recommended_next",[])
    if nxt:
        st.markdown('<p style="color:#94a3b866;font-size:.75rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;margin-top:1rem">Next Steps</p>', unsafe_allow_html=True)
        for n in nxt: st.markdown(f'<p style="color:#888;font-size:.9rem"><span style="color:#94a3b8">→</span> {n}</p>', unsafe_allow_html=True)

st.divider()
if st.button("Start New Session", use_container_width=True):
    for k in ["chat_history","ss_data","quiz_qs","quiz_answers","quiz_submitted","quiz_score",
              "fc_cards","mq_qs","mq_ans","mq_evals","ta_data","mm_data"]:
        st.session_state.pop(k, None)
    st.success("Session cleared — ready for a new study session.")
    st.rerun()