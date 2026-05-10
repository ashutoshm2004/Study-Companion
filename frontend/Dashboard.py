import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from frontend.api_client import health, upload_document, list_documents, delete_document
from frontend.styles import apply_styles, section_label

st.set_page_config(page_title="Study Companion", page_icon="🎓", layout="wide")
apply_styles()

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:

    ok = health()
    status_text = "Backend online" if ok else "Backend offline"
    status_class = "status-online" if ok else "status-offline"

    # Premium branding
    st.markdown(
        f"""
<div class="sidebar-brand">

<div class="brand-logo">
    🎓
</div>

<div class="brand-content">

<div class="brand-title">
    Study Companion
</div>

<div class="brand-subtitle">
    AI-Powered Learning
</div>

<div class="backend-status">
    <span class="{status_class}"></span>
    {status_text}
</div>

</div>

</div>
""",
        unsafe_allow_html=True
    )

    if not ok:
        st.code(
            "uvicorn backend.main:app --reload --port 8000",
            language="bash"
        )
    st.divider()
    section_label("Upload Document")
    uploaded = st.file_uploader("PDF · DOCX · TXT", type=["pdf","docx","doc","txt"], label_visibility="collapsed")
    if uploaded and st.button("Process Document", use_container_width=True):
        with st.spinner("Processing..."):
            try:
                res = upload_document(uploaded.read(), uploaded.name)
                st.success(res["message"])
                st.session_state["doc_id"]   = res["document_id"]
                st.session_state["doc_name"] = res["filename"]
                st.rerun()
            except Exception as e:
                st.error(f"Upload failed: {e}")

    st.divider()

    section_label("Your Documents")

    try:
        docs = list_documents()

        if not docs:
            st.markdown(
                """
                <p style="
                    color:#6B7280;
                    font-size:.85rem;
                ">
                    No documents uploaded yet.
                </p>
                """,
                unsafe_allow_html=True
            )

        for d in docs:
            active = (
                d["document_id"]
                == st.session_state.get("doc_id")
            )

            c1, c2 = st.columns([5, 1])

            with c1:
                label = (
                    ("✓ " if active else "")
                    + d["filename"][:24]
                )

                if st.button(
                    label,
                    key=f"s_{d['document_id']}",
                    use_container_width=True
                ):
                    st.session_state["doc_id"] = d["document_id"]
                    st.session_state["doc_name"] = d["filename"]
                    st.rerun()

            with c2:
                if st.button(
                    "✕",
                    key=f"d_{d['document_id']}"
                ):
                    delete_document(d["document_id"])

                    if (
                        st.session_state.get("doc_id")
                        == d["document_id"]
                    ):
                        st.session_state.pop("doc_id", None)
                        st.session_state.pop("doc_name", None)

                    st.rerun()

    except Exception as e:
        st.warning(str(e))

# ── Hero ───────────────────────────────────────────────────────────────────
doc_id   = st.session_state.get("doc_id")
doc_name = st.session_state.get("doc_name", "")

st.markdown(f"""
<div class="hero-card">
  <div style="flex:1;min-width:0">
    <p class="section-label">AI-Powered · Free · Local Embeddings</p>
    <div class="hero-text">
      <h1>Master Any Subject<br>With AI Tutoring</h1>
      <p>Upload your course materials and unlock seven AI-powered study tools — from conversational tutoring to exam simulation. Powered by Groq's Llama 3.3 70B, completely free.</p>
    </div>
    {"<span class='chip'>📖 " + doc_name + "</span>" if doc_id else "<span class='chip'>⬆ Upload a document from sidebar to begin</span>"}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Feature grid ───────────────────────────────────────────
section_label("Study Tools")

tools = [
    ("💬", "Tutor Chat",
     "Ask anything — explained with analogies, examples, and follow-up questions.",
     "RAG · Source citations",
     "/Tutor_Chat"),

    ("🃏", "Flashcards",
     "One-click generation of study cards at Easy, Medium, or Hard difficulty.",
     "Flip · Shuffle · Filter",
     "/Flashcards"),

    ("📝", "Quiz Mode",
     "Multiple-choice questions with instant graded feedback and explanations.",
     "Score tracking · Difficulty",
     "/Quiz"),

    ("🗺️", "Mind Map",
     "Interactive concept graph — zoom, drag, and explore topic relationships.",
     "pyvis · Draggable nodes",
     "/Mind_Map"),

    ("🔍", "Topic Analysis",
     "Importance-ranked breakdown of every topic, subtopic, and key term.",
     "Plotly chart · Key terms",
     "/Topic_Analysis"),

    ("📋", "Mock Exam",
     "Essay and short-answer questions with AI grading and model answers.",
     "LLM-as-judge · Rubric",
     "/Mock_Exam"),
]

cols = st.columns(3)

for i, (icon, title, desc, tag, route) in enumerate(tools):
    with cols[i % 3]:

        st.markdown(
f"""
<a href="{route}" target="_self"
style="text-decoration:none;">

<div class="feat-card">
<div class="icon">{icon}</div>

<div class="card-title">
{title}
</div>

<p>{desc}</p>

<div class="tag">
{tag}
</div>
</div>

</a>
""",
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#333;font-size:.78rem">Study Companion v2 · Groq llama-3.3-70b-versatile · sentence-transformers · ChromaDB · FastAPI · Streamlit</p>', unsafe_allow_html=True)