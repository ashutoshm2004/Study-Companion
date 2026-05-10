import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import streamlit as st
import plotly.graph_objects as go
from frontend.api_client import get_topics
from frontend.styles import apply_styles, page_header, active_doc_chip

st.set_page_config(page_title="Topic Analysis", page_icon="🔍", layout="wide")
apply_styles()
page_header("🔍", "Topic Analysis", "Importance-ranked breakdown of every topic and key term")

doc_id = st.session_state.get("doc_id")
if not doc_id:
    st.markdown('<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:2rem;text-align:center;color:#666">⬆ No document selected</div>', unsafe_allow_html=True)
    st.stop()
active_doc_chip(st.session_state.get("doc_name", doc_id), doc_id)

if st.button("Analyse Topics", use_container_width=True):
    with st.spinner("Analysing…"):
        try:
            st.session_state["ta_data"] = get_topics(doc_id)
        except Exception as e:
            st.error(str(e))

data = st.session_state.get("ta_data")
if not data:
    st.markdown('<div style="text-align:center;padding:3rem;color:#333">Click above to analyse your document.</div>', unsafe_allow_html=True)
    st.stop()

topics  = data.get("topics", [])
summary = data.get("document_summary","")
st.markdown(f'<span class="chip">📚 {len(topics)} topics</span>', unsafe_allow_html=True)
if summary:
    st.markdown(f'<p style="color:#888;margin-top:.8rem">{summary}</p>', unsafe_allow_html=True)
st.markdown("")

if topics:
    fig = go.Figure(go.Bar(
        x=[t.get("importance_score",0)*100 for t in topics],
        y=[t.get("name","") for t in topics],
        orientation="h",
        marker=dict(color=[t.get("importance_score",0)*100 for t in topics],
                    colorscale=[[0,"#2a2a2a"],[0.5,"#555"],[1,"#e2e8f0"]],
                    line=dict(color="#333",width=0)),
        text=[f"{t.get('importance_score',0)*100:.0f}%" for t in topics],
        textposition="outside",
        textfont=dict(color="#888", size=12),
    ))
    fig.update_layout(
        paper_bgcolor="#141414", plot_bgcolor="#1a1a1a",
        font=dict(color="#888", family="Inter"),
        xaxis=dict(gridcolor="#222", tickfont=dict(color="#555"), title="Importance (%)", titlefont=dict(color="#555")),
        yaxis=dict(gridcolor="#222", tickfont=dict(color="#ccc"), autorange="reversed"),
        height=max(280, len(topics)*46),
        margin=dict(l=180,r=80,t=30,b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
for i, t in enumerate(topics):
    score = t.get("importance_score",0)
    bar_color = "#e2e8f0" if score>0.7 else "#94a3b8" if score>0.4 else "#475569"
    with st.expander(f"**{t.get('name','')}**  ·  {score*100:.0f}%", expanded=i<2):
        st.markdown(f'<div class="imp-bar-bg"><div class="imp-bar-fill" style="width:{int(score*100)}%;background:{bar_color}"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#aaa">{t.get("summary","")}</p>', unsafe_allow_html=True)
        subs = t.get("subtopics",[])
        if subs:
            st.markdown('<p style="color:#666;font-size:.8rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:.4rem">Subtopics</p>', unsafe_allow_html=True)
            cols = st.columns(min(len(subs),2))
            for j,s in enumerate(subs):
                cols[j%2].markdown(f'<p style="color:#888;font-size:.9rem"><span style="color:#555">●</span> <strong style="color:#ccc">{s.get("name","")}</strong> — {s.get("summary","")}</p>', unsafe_allow_html=True)
        terms = t.get("key_terms",[])
        if terms:
            st.markdown('<p style="color:#666;font-size:.8rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin:.8rem 0 .4rem">Key Terms</p>', unsafe_allow_html=True)
            st.markdown(" ".join(f'<span class="chip">{x}</span>' for x in terms), unsafe_allow_html=True)