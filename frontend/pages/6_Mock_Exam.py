import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import streamlit as st
from frontend.api_client import get_mock_questions, evaluate_answer
from frontend.styles import apply_styles, page_header, active_doc_chip

st.set_page_config(page_title="Mock Exam", page_icon="📋", layout="wide")
apply_styles()
page_header("📋", "Mock Exam", "Exam-style questions with AI grading and model answers")

doc_id = st.session_state.get("doc_id")
if not doc_id:
    st.markdown('<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:2rem;text-align:center;color:#666">⬆ No document selected</div>', unsafe_allow_html=True)
    st.stop()
active_doc_chip(st.session_state.get("doc_name", doc_id), doc_id)

with st.expander("⚙️ Configure", expanded=True):
    c1, c2 = st.columns(2)
    with c1: num   = st.slider("Questions", 1, 10, 3)
    with c2: qtype = st.selectbox("Type", ["essay","short_answer","case_study"])
    if st.button("Generate Questions", use_container_width=True):
        with st.spinner("Generating…"):
            try:
                res = get_mock_questions(doc_id, num, qtype)
                st.session_state.update({"mq_qs": res.get("questions",[]), "mq_topic": res.get("topic",""), "mq_ans": {}, "mq_evals": {}})
            except Exception as e:
                st.error(str(e))

qs = st.session_state.get("mq_qs",[])
if not qs:
    st.markdown('<div style="text-align:center;padding:3rem;color:#333">Configure and generate questions above.</div>', unsafe_allow_html=True)
    st.stop()

st.markdown(f'<span class="chip">📚 {len(qs)} questions</span> <span class="chip">{st.session_state.get("mq_topic","")}</span>', unsafe_allow_html=True)
st.markdown("")

for i, q in enumerate(qs):
    st.markdown(f"""
    <div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:1.4rem 1.6rem;margin:.8rem 0">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.6rem">
        <span style="color:#555;font-size:.78rem;text-transform:uppercase;letter-spacing:1px">Question {i+1}</span>
        <span class="chip">{q.get('marks',10)} marks</span>
      </div>
      <p style="color:#e0e0e0!important;font-size:1rem;font-weight:500;margin:0">{q['question']}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Marking guidance"):
        st.markdown(f'<p style="color:#888">{q.get("guidance","")}</p>', unsafe_allow_html=True)

    ans = st.text_area(f"Your answer", value=st.session_state.get("mq_ans",{}).get(i,""),
                       height=160, key=f"ma_{i}", placeholder="Write your answer here…", label_visibility="collapsed")
    if ans:
        st.session_state.setdefault("mq_ans",{})[i] = ans
    st.caption(f"{'📝 ' + str(len(ans.split())) + ' words' if ans else '📝 0 words'}")

    if st.button(f"Submit & Grade", key=f"sub_{i}", disabled=len(ans.strip())<20):
        with st.spinner("Grading…"):
            try:
                ev = evaluate_answer(doc_id, q["question"], ans, q.get("marks",10))
                st.session_state.setdefault("mq_evals",{})[i] = ev
            except Exception as e:
                st.error(str(e))

    ev = st.session_state.get("mq_evals",{}).get(i)
    if ev:
        pct   = ev.get("percentage",0)
        color = "#4ade80" if pct>=70 else "#facc15" if pct>=50 else "#f87171"
        grade = ev.get("grade","?")
        st.markdown(f'<div style="background:{color}18;border:1px solid {color}33;border-radius:10px;padding:1rem 1.4rem;margin:.6rem 0"><span style="color:{color};font-weight:700;font-size:1.1rem">Score: {ev.get("score",0)}/{ev.get("max_score",10)} · {pct:.0f}% · Grade {grade}</span></div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<p style="color:#4ade80;font-size:.8rem;font-weight:600;letter-spacing:1px;text-transform:uppercase">Strengths</p>', unsafe_allow_html=True)
            for s in ev.get("strengths",[]): st.markdown(f'<p style="color:#888;font-size:.9rem">✓ {s}</p>', unsafe_allow_html=True)
        with c2:
            st.markdown('<p style="color:#f87171;font-size:.8rem;font-weight:600;letter-spacing:1px;text-transform:uppercase">Improvements</p>', unsafe_allow_html=True)
            for s in ev.get("improvements",[]): st.markdown(f'<p style="color:#888;font-size:.9rem">→ {s}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#777;font-size:.9rem;margin-top:.6rem">{ev.get("feedback","")}</p>', unsafe_allow_html=True)
        with st.expander("Model Answer"):
            st.markdown(f'<p style="color:#aaa">{ev.get("model_answer","")}</p>', unsafe_allow_html=True)
    st.markdown("")