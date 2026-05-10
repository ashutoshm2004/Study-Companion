import sys, os, tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import streamlit as st
import streamlit.components.v1 as components
from frontend.api_client import get_mindmap
from frontend.styles import apply_styles, page_header, active_doc_chip

st.set_page_config(page_title="Mind Map", page_icon="🗺️", layout="wide")
apply_styles()
page_header("🗺️", "Mind Map", "Interactive concept graph — zoom, drag, and explore")

doc_id = st.session_state.get("doc_id")
if not doc_id:
    st.markdown('<div style="background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:2rem;text-align:center;color:#666">⬆ No document selected</div>', unsafe_allow_html=True)
    st.stop()
active_doc_chip(st.session_state.get("doc_name", doc_id), doc_id)

def build_graph(nodes, edges):
    from pyvis.network import Network
    net = Network(height="560px", width="100%", bgcolor="#1a1a1a", font_color="#cccccc", directed=False)
    net.set_options("""{
      "nodes":{"shadow":{"enabled":true,"color":"rgba(0,0,0,0.5)","size":8},"font":{"size":13,"color":"#e0e0e0","face":"Inter"},"borderWidth":1.5},
      "edges":{"color":{"color":"#333","highlight":"#888"},"smooth":{"type":"curvedCW","roundness":0.25},"font":{"size":10,"color":"#555","strokeWidth":0},"width":1.5},
      "physics":{"forceAtlas2Based":{"gravitationalConstant":-80,"centralGravity":0.003,"springLength":180,"springConstant":0.05},"solver":"forceAtlas2Based","stabilization":{"iterations":200}},
      "interaction":{"hover":true,"tooltipDelay":150}
    }""")
    palette = {"main":"#e2e8f0","sub":"#94a3b8","detail":"#475569"}
    bg      = {"main":"#2a2a2a","sub":"#1e1e1e","detail":"#191919"}
    for n in nodes:
        g = n.get("group","sub")
        net.add_node(n["id"], label=n["label"], color={"background":bg.get(g,"#1e1e1e"),"border":palette.get(g,"#555"),"highlight":{"background":"#333","border":"#fff"}},
                     size=n.get("size",20), title=f"{n['label']}", font={"color":palette.get(g,"#ccc")})
    for e in edges:
        net.add_edge(e["source"], e["target"], label=e.get("label",""), width=float(e.get("weight",1))*1.5, color={"color":"#2e2e2e","highlight":"#666"})
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
        net.save_graph(f.name)
        return open(f.name, encoding="utf-8").read()

if st.button("Generate Mind Map", use_container_width=True):
    with st.spinner("Analysing document and building graph…"):
        try:
            res = get_mindmap(doc_id)
            st.session_state["mm_data"] = res
        except Exception as e:
            st.error(str(e))

mm = st.session_state.get("mm_data")
if not mm:
    st.markdown('<div style="text-align:center;padding:3rem;color:#333">Click the button above to generate your mind map.</div>', unsafe_allow_html=True)
    st.stop()

nodes = mm.get("nodes",[])
edges = mm.get("edges",[])
st.markdown(f'<span class="chip">🗺️ {mm.get("title","Concept Map")}</span> <span class="chip">{len(nodes)} concepts</span> <span class="chip">{len(edges)} connections</span>', unsafe_allow_html=True)
st.markdown("")
c1,c2,c3 = st.columns(3)
c1.markdown('<span class="dot" style="background:#e2e8f0"></span><span style="color:#888;font-size:.85rem">Main topics</span>', unsafe_allow_html=True)
c2.markdown('<span class="dot" style="background:#94a3b8"></span><span style="color:#888;font-size:.85rem">Subtopics</span>', unsafe_allow_html=True)
c3.markdown('<span class="dot" style="background:#475569"></span><span style="color:#888;font-size:.85rem">Details</span>', unsafe_allow_html=True)

try:
    html = build_graph(nodes, edges)
    # Inject dark bg into the pyvis iframe
    html = html.replace('<body>', '<body style="background:#1a1a1a;margin:0;padding:0">')
    components.html(html, height=580)
except Exception as e:
    st.error(f"Render error: {e}")
    for n in nodes:
        st.markdown(f"- **{n['label']}** ({n.get('group','')})")

with st.expander("All concepts"):
    cols = st.columns(3)
    palette = {"main":"#e2e8f0","sub":"#94a3b8","detail":"#475569"}
    for i,n in enumerate(nodes):
        c = palette.get(n.get("group","sub"),"#666")
        cols[i%3].markdown(f'<span style="color:{c};font-size:.85rem">● {n["label"]}</span>', unsafe_allow_html=True)