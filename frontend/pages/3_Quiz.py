import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import streamlit as st
from frontend.api_client import get_quiz
from frontend.styles import apply_styles, page_header, active_doc_chip

st.set_page_config(page_title="Quiz", page_icon="📝", layout="wide")
apply_styles()
page_header("📝", "Quiz Mode", "Multiple-choice questions with instant graded feedback")

doc_id = st.session_state.get("doc_id")
if not doc_id:
    st.markdown('<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:2rem;text-align:center;color:#666">⬆ No document selected</div>', unsafe_allow_html=True)
    st.stop()
active_doc_chip(st.session_state.get("doc_name", doc_id), doc_id)

with st.expander("⚙️ Configure", expanded=True):
    c1,c2,c3 = st.columns(3)
    with c1: num  = st.slider("Questions", 3, 20, 5)
    with c2: diff = st.selectbox("Difficulty", ["easy","medium","hard"], index=1)
    with c3: topic = st.text_input("Topic focus", placeholder="optional")
    if st.button("Generate Quiz", use_container_width=True):
        with st.spinner("Generating…"):
            try:
                res = get_quiz(doc_id, num, diff, topic or None)
                st.session_state.update({"quiz_qs": res.get("questions",[]), "quiz_topic": res.get("topic",""),
                                         "quiz_answers": {}, "quiz_submitted": False})
                st.session_state.pop("quiz_score", None)
            except Exception as e:
                st.error(str(e))

qs = st.session_state.get("quiz_qs", [])
if not qs:
    st.markdown('<div style="text-align:center;padding:3rem;color:#333">Configure and generate a quiz above.</div>', unsafe_allow_html=True)
    st.stop()

submitted = st.session_state.get("quiz_submitted", False)
answers   = st.session_state.get("quiz_answers", {})
st.markdown(f'<span class="chip">📚 {len(qs)} questions</span> <span class="chip">{st.session_state.get("quiz_topic","")}</span>', unsafe_allow_html=True)
st.markdown("")

for i, q in enumerate(qs):
    opts    = q.get("options", [])
    correct = q.get("correct_index", 0)
    st.markdown(f'<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:1.2rem 1.5rem;margin:.6rem 0"><p style="color:#fff!important;font-weight:600;margin:0 0 .8rem">Q{i+1}. {q["question"]}</p>', unsafe_allow_html=True)
    if not submitted:
        chosen = st.radio(f"q{i}", opts, index=None, key=f"r{i}", label_visibility="collapsed")
        if chosen is not None:
            answers[i] = opts.index(chosen)
            st.session_state["quiz_answers"] = answers
    else:
        user = answers.get(i, -1)
        for j, opt in enumerate(opts):
            if j == correct:
                st.markdown(f'<p style="color:#4ade80!important;margin:.2rem 0">✓ {opt}</p>', unsafe_allow_html=True)
            elif j == user and user != correct:
                st.markdown(f'<p style="color:#f87171!important;margin:.2rem 0;text-decoration:line-through">✗ {opt}</p>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p style="color:#555!important;margin:.2rem 0">&nbsp;&nbsp;{opt}</p>', unsafe_allow_html=True)
        if q.get("explanation"):
            st.markdown(f'<p style="color:#888!important;font-size:.85rem;margin-top:.6rem;padding-top:.6rem;border-top:1px solid #2a2a2a">💡 {q["explanation"]}</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if not submitted:
    answered = sum(1 for v in answers.values() if v is not None)
    st.markdown("")
    st.progress(answered / len(qs) if qs else 0)
    st.caption(f"{answered} / {len(qs)} answered")
    if st.button("Submit Quiz", use_container_width=True, disabled=answered < len(qs)):
        score = sum(1 for i,q in enumerate(qs) if answers.get(i) == q.get("correct_index"))
        st.session_state.update({"quiz_submitted": True, "quiz_score": score})
        st.rerun()
else:
    score = st.session_state.get("quiz_score", 0)
    pct   = score / len(qs) * 100
    color = "#4ade80" if pct>=70 else "#facc15" if pct>=50 else "#f87171"
    grade = "A" if pct>=90 else "B" if pct>=80 else "C" if pct>=70 else "D" if pct>=60 else "F"
    st.markdown(f'<div class="score-badge" style="background:{color}22;border:1px solid {color}44"><h2 style="color:{color}!important">Score: {score}/{len(qs)} &nbsp;·&nbsp; {pct:.0f}% &nbsp;·&nbsp; Grade {grade}</h2></div>', unsafe_allow_html=True)
    if st.button("Start New Quiz", use_container_width=True):
        for k in ["quiz_qs","quiz_topic","quiz_answers","quiz_submitted","quiz_score"]:
            st.session_state.pop(k, None)
        st.rerun()