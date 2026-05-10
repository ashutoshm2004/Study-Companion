"""
Premium Dark Emerald AI Dashboard Theme
Drop-in replacement for styles.py
"""

STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ==========================================================
   COLOR SYSTEM
========================================================== */
:root {
    --bg: #0B0F0D;
    --sidebar: #0F1412;
    --surface: #111714;
    --card: #151C18;

    --primary: #34D399;
    --primary-hover: #10B981;
    --primary-soft: rgba(52,211,153,.10);

    --text: #F3F4F6;
    --text-muted: #9CA3AF;

    --border: #243129;
    --border-light: rgba(255,255,255,.05);

    --shadow:
        0 10px 40px rgba(0,0,0,.35);

    --radius: 24px;
}

/* ==========================================================
   APP
========================================================== */
html, body,
[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}

/* ==========================================================
   STREAMLIT HEADER FIX
   keep sidebar icon
========================================================== */

/* Hide menu + footer */
#MainMenu,
footer {
    visibility: hidden;
}

/* Make header transparent */
header[data-testid="stHeader"] {
    background: transparent !important;
    border: none !important;
}

/* Remove top decoration line */
[data-testid="stDecoration"] {
    display: none !important;
}

/* Hide deploy button */
button[title="Deploy"],
button[aria-label="Deploy"] {
    display: none !important;
}

/* Hide running spinner / status */
[data-testid="stStatusWidget"] {
    display: none !important;
}

/* Hide kebab menu (top right menu) */
button[title="Main menu"] {
    display: none !important;
}

/* KEEP toolbar alive for sidebar toggle */
[data-testid="stToolbar"] {
    background: transparent !important;
}

/* Move sidebar button nicely */
[data-testid="collapsedControl"] {
    top: 1rem !important;
    left: 1rem !important;
    z-index: 99999 !important;
}
/* ==========================================================
   MAIN LAYOUT (FIXES CRAMPING)
========================================================== */
.main .block-container {
    max-width: 1320px !important;
    padding-top: 3rem !important;
    padding-left: 4rem !important;
    padding-right: 4rem !important;
    padding-bottom: 4rem !important;
}

/* add spacing between sections */
.element-container {
    margin-bottom: 1rem;
}

/* ==========================================================
   SIDEBAR
========================================================== */
[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebarContent"] {
    padding: 2rem 1.25rem !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* nav */
[data-testid="stSidebarNav"] {
    padding-top: 1rem !important;
}

[data-testid="stSidebarNav"] a {
    border-radius: 16px !important;
    padding: .85rem 1rem !important;
    margin-bottom: .45rem !important;

    color: var(--text-muted) !important;

    border: 1px solid transparent;
    transition: .2s ease;
}

[data-testid="stSidebarNav"] a:hover {
    background: var(--primary-soft) !important;
    border: 1px solid rgba(52,211,153,.18);
    transform: translateX(3px);
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(52,211,153,.12) !important;
    border: 1px solid rgba(52,211,153,.22);
    color: white !important;
}

/* ==========================================================
   TYPOGRAPHY
========================================================== */
h1,h2,h3,h4 {
    color: white !important;
    letter-spacing: -.03em;
}

h1 {
    font-size: 3rem !important;
    font-weight: 800 !important;
    line-height: 1.05 !important;
    margin-bottom: 1rem !important;
}

h2 {
    font-size: 2rem !important;
    font-weight: 700 !important;
}

h3 {
    font-size: 1.15rem !important;
    font-weight: 600 !important;
}

p, span, label, li {
    color: var(--text-muted) !important;
}

/* ==========================================================
   PAGE HEADER
========================================================== */
.page-header {
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}

.page-header h2 {
    margin: 0 !important;
}

.page-header p {
    margin-top: .45rem !important;
    font-size: .96rem;
}

/* ==========================================================
   CARD SYSTEM
========================================================== */
.hero-card,
.feat-card,
.flashcard,
[data-testid="stChatMessage"],
[data-testid="stAlert"],
[data-testid="stExpander"],
div[data-testid="stForm"] {

    background: linear-gradient(
        180deg,
        rgba(21,28,24,.98),
        rgba(16,22,19,.98)
    ) !important;

    border: 1px solid var(--border);
    border-radius: var(--radius) !important;

    box-shadow: var(--shadow);

    padding: 1.5rem !important;
}

/* spacing between cards */
.feat-card {
    padding: 2rem !important;
    min-height: 220px;
    transition: .2s ease;
}

.feat-card:hover {
    transform: translateY(-4px);
    border-color: rgba(52,211,153,.18);
}

/* ==========================================================
   HERO SECTION (FIXED)
========================================================== */
.hero-card {
    padding: 3rem !important;
    margin-bottom: 2.5rem !important;
}

.hero-text h1 {
    font-size: 4rem !important;
    max-width: 700px;
}

.hero-text p {
    max-width: 900px;
    line-height: 1.9;
    font-size: 1.05rem;
}

/* ==========================================================
   BUTTONS
========================================================== */
.stButton > button {
    background: rgba(14, 20, 17, 0.95) !important;
    color: #D1D5DB !important;

    border: 1px solid rgba(52,211,153,.18) !important;
    border-radius: 16px !important;

    font-weight: 600 !important;
    font-size: .95rem !important;

    padding: .8rem 1.4rem !important;

    transition: .2s ease;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.03),
        0 0 12px rgba(52,211,153,.05);
}

.stButton > button:hover {
    background: rgba(20, 28, 24, 1) !important;
    border-color: rgba(52,211,153,.35) !important;

    color: #ECFDF5 !important;
    transform: translateY(-2px);
}
/* ==========================================================
   INPUTS
========================================================== */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox > div > div {

    background: rgba(255,255,255,.03) !important;
    color: white !important;

    border: 1px solid var(--border) !important;
    border-radius: 16px !important;

    padding: .85rem !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: rgba(52,211,153,.4) !important;
    box-shadow: none !important;
}

/* ==========================================================
   FILE UPLOADER (MUCH CLEANER)
========================================================== */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,.02);
    border: 2px dashed rgba(52,211,153,.20);

    border-radius: 22px;
    padding: 1.5rem;

    margin-top: .75rem;
    margin-bottom: 1rem;
}

/* ==========================================================
   CHAT
========================================================== */
[data-testid="stChatMessage"] {
    margin-bottom: 1rem !important;
    padding: 1.25rem !important;
}

/* ==========================================================
   CHIPS
========================================================== */
.chip {
    display: inline-block;
    background: rgba(52,211,153,.10);
    border: 1px solid rgba(52,211,153,.14);

    color: var(--primary) !important;

    border-radius: 999px;
    padding: .45rem .95rem;
    margin: .2rem;
}

/* ==========================================================
   PROGRESS BAR
========================================================== */
.stProgress > div > div > div {
    background: var(--primary) !important;
}

/* ==========================================================
   SECTION LABEL
========================================================== */
.section-label {
    text-transform: uppercase;
    letter-spacing: 2px;
    font-size: .78rem;
    font-weight: 700;

    color: var(--primary) !important;

    margin-bottom: .8rem;
}

/* ==========================================================
   SCROLLBAR
========================================================== */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #1C2822;
    border-radius: 999px;
}

::-webkit-scrollbar-thumb:hover {
    background: #2E473D;
}

/* ==========================================================
   DOCUMENT BUTTONS
========================================================== */

/* document selector buttons */
[data-testid="stSidebar"] .stButton button {
    background: #151C18 !important;
    color: #D1D5DB !important;

    border: 1px solid #243129 !important;
    border-radius: 16px !important;

    box-shadow: none !important;
    font-weight: 500 !important;
}

/* hover */
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(52,211,153,.08) !important;
    border-color: rgba(52,211,153,.18) !important;
    color: white !important;
}

/* selected/active doc */
[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: rgba(52,211,153,.12) !important;
    border: 1px solid rgba(52,211,153,.20) !important;
    color: #34D399 !important;
}

/* ==========================================================
   PAGE LINK AS INVISIBLE CARD OVERLAY
========================================================== */

/* parent */
div[data-testid="stPageLink"] {
    position: relative !important;
    margin-bottom: -240px !important;
    z-index: 999 !important;
}

/* invisible clickable overlay */
div[data-testid="stPageLink"] a {
    position: absolute !important;
    inset: 0 !important;

    width: 100% !important;
    height: 240px !important;

    opacity: 0 !important;
    background: transparent !important;
    border: none !important;

    cursor: pointer !important;
}

/* card hover */
.feat-card {
    transition: .2s ease;
    cursor: pointer;
}

.feat-card:hover {
    transform: translateY(-5px);
    border-color: rgba(52,211,153,.22);
}

/* clickable card link */
.feat-card {
    transition: .2s ease;
    cursor: pointer;
}

.feat-card:hover {
    transform: translateY(-5px);
    border-color: rgba(52,211,153,.22);
}

/* title inside card */
.card-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: white;
    margin-bottom: .7rem;
}

/* ==========================================================
   FEATURE CARD LINK FIX
========================================================== */

/* remove browser link styling inside cards */
.feat-card a,
.feat-card a:visited,
.feat-card a:hover,
.feat-card a:active {
    color: inherit !important;
    text-decoration: none !important;
}

/* fix tag color */
.feat-card .tag {
    color: #E5E7EB !important;
    font-size: .92rem;
    font-weight: 500;
    margin-top: 1rem;
}

/* keep title white */
.card-title {
    color: white !important;
}

/* description muted */
.feat-card p {
    color: #A1A1AA !important;
}

/* ==========================================================
   SIDEBAR BRANDING
========================================================== */

.sidebar-brand {
    display: flex;
    align-items: flex-start;
    gap: .9rem;

    padding: .5rem 0 1.25rem 0;
}

/* icon */
.brand-logo {
    font-size: 1.5rem;
    margin-top: .15rem;
}

/* title */
.brand-title {
    font-family: 'Playfair Display', serif !important;

    font-size: 1.55rem;
    font-weight: 700;
    color: #FFFFFF;

    letter-spacing: -.02em;
    line-height: 1.05;
}

/* subtitle */
.brand-subtitle {
    margin-top: .18rem;

    font-size: .82rem;
    color: #7C8794;
}

/* backend status row */
.backend-status {
    display: flex;
    align-items: center;
    gap: .5rem;

    margin-top: .9rem;

    font-size: .82rem;
    color: #D1D5DB;
}

/* blinking online dot */
.status-online {
    width: 9px;
    height: 9px;

    border-radius: 999px;
    background: #34D399;

    display: inline-block;

    animation: pulseGreen 1.6s infinite;
}

/* offline */
.status-offline {
    width: 9px;
    height: 9px;

    border-radius: 999px;
    background: #EF4444;

    display: inline-block;
}

/* pulse animation */
@keyframes pulseGreen {
    0% {
        box-shadow: 0 0 0 0 rgba(52,211,153,.7);
    }

    70% {
        box-shadow: 0 0 0 8px rgba(52,211,153,0);
    }

    100% {
        box-shadow: 0 0 0 0 rgba(52,211,153,0);
    }
}

/* hero upload button */
button[kind="primary"] {
    background:
    rgba(52,211,153,.10) !important;

    border:
    1px solid
    rgba(52,211,153,.16) !important;

    color:
    #34D399 !important;

    border-radius:
    999px !important;

    padding:
    .85rem 1.25rem !important;

    font-weight:
    600 !important;

    transition:
    .2s ease !important;
}

button[kind="primary"]:hover {
    background:
    rgba(52,211,153,.16) !important;

    transform:
    translateY(-2px);
}
</style>
"""

def apply_styles():
    import streamlit as st
    st.markdown(STYLES, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = ""):
    import streamlit as st
    st.markdown(f'''
    <div class="page-header">
        <h2>{icon} {title}</h2>
        {"<p>" + subtitle + "</p>" if subtitle else ""}
    </div>
    ''', unsafe_allow_html=True)


def active_doc_chip(doc_name: str, doc_id: str):
    import streamlit as st
    st.markdown(
        f'<span class="chip">📖 {doc_name}</span> '
        f'<span class="chip">ID: {doc_id}</span>',
        unsafe_allow_html=True
    )


def section_label(text: str):
    import streamlit as st
    st.markdown(
        f'<p class="section-label">{text}</p>',
        unsafe_allow_html=True
    )