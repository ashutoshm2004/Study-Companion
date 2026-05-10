import sys, os, random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import streamlit as st
from frontend.api_client import get_flashcards
from frontend.styles import apply_styles, page_header, active_doc_chip, section_label

st.set_page_config(page_title="Flashcards", page_icon="🃏", layout="wide")
apply_styles()
page_header("🃏", "Flashcards", "Auto-generated study cards — flip to reveal the answer")

doc_id = st.session_state.get("doc_id")
if not doc_id:
    st.markdown('<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:2rem;text-align:center;color:#666">⬆ No document selected</div>', unsafe_allow_html=True)
    st.stop()
active_doc_chip(st.session_state.get("doc_name", doc_id), doc_id)

with st.expander("⚙️ Configure", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1: num  = st.slider("Number of cards", 5, 30, 10)
    with c2: diff = st.selectbox("Difficulty", ["easy","medium","hard"], index=1)
    with c3: topic = st.text_input("Topic filter", placeholder="e.g. photosynthesis")
    if st.button("Generate Flashcards", use_container_width=True):
        with st.spinner("Generating…"):
            try:
                res = get_flashcards(doc_id, num, diff, topic or None)
                st.session_state.update({"fc_cards": res.get("cards",[]), "fc_topic": res.get("topic_covered",""), "fc_idx": 0, "fc_flipped": False})
            except Exception as e:
                st.error(str(e))

cards = st.session_state.get("fc_cards", [])
if not cards:
    st.markdown('<div style="text-align:center;padding:3rem;color:#333">Configure and generate cards above to begin.</div>', unsafe_allow_html=True)
    st.stop()

st.markdown(f'<span class="chip">📚 {len(cards)} cards</span> <span class="chip">Topic: {st.session_state.get("fc_topic","")}</span>', unsafe_allow_html=True)
st.markdown("")

idx     = st.session_state.get("fc_idx", 0)
flipped = st.session_state.get("fc_flipped", False)
card    = cards[idx]
dc      = {"easy":"#4ade80","medium":"#facc15","hard":"#f87171"}.get(card.get("difficulty","medium"),"#888")
body    = card.get("answer" if flipped else "question", "")
hint    = card.get("hint","")
side    = "ANSWER" if flipped else "QUESTION"

st.markdown(f"""
<div class="flashcard">
  <div class="fc-meta">Card {idx+1} / {len(cards)} &nbsp;·&nbsp; <span style="color:{dc}">{card.get('difficulty','medium').upper()}</span> &nbsp;·&nbsp; {side}</div>
  <div class="fc-body">{body}</div>
  {"" if flipped or not hint else f'<div class="fc-hint">💡 {hint}</div>'}
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
with c1:
    if st.button("← Prev", use_container_width=True, disabled=idx==0):
        st.session_state.update({"fc_idx": idx-1, "fc_flipped": False}); st.rerun()
with c2:
    lbl = "Show Question" if flipped else "Reveal Answer"
    if st.button(lbl, use_container_width=True):
        st.session_state["fc_flipped"] = not flipped; st.rerun()
with c3:
    if st.button("Next →", use_container_width=True, disabled=idx==len(cards)-1):
        st.session_state.update({"fc_idx": idx+1, "fc_flipped": False}); st.rerun()
with c4:
    if st.button("Shuffle", use_container_width=True):
        random.shuffle(st.session_state["fc_cards"])
        st.session_state.update({"fc_idx":0,"fc_flipped":False}); st.rerun()

st.progress((idx+1)/len(cards))

with st.expander("All cards"):
    for i,c in enumerate(cards):
        e = {"easy":"🟢","medium":"🟡","hard":"🔴"}.get(c.get("difficulty","medium"),"⚪")
        st.markdown(f"**{i+1}. {e} {c['question']}**")
        st.markdown(f"<span style='color:#777'>→ {c['answer']}</span>", unsafe_allow_html=True)
        if c.get("hint"): st.caption(f"💡 {c['hint']}")
        st.divider()