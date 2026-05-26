"""
Streamlit Web UI — Deep Research Agent
"""

import asyncio
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

st.set_page_config(
    page_title="Deep Research Agent",
    page_icon="🔬",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* hide default streamlit header/footer */
#MainMenu, footer { display: none; }
header[data-testid="stHeader"] { display: none; }

/* main container */
.block-container {
    padding: 2rem 2rem 4rem !important;
    max-width: 800px !important;
}

/* sidebar */
section[data-testid="stSidebar"] {
    background: #fafafa !important;
    border-right: 1px solid #e5e5e5 !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}

/* textarea */
textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
    border-radius: 8px !important;
    border: 1px solid #d4d4d4 !important;
    background: #fff !important;
    color: #171717 !important;
    padding: 12px 14px !important;
    resize: vertical !important;
}
textarea:focus {
    border-color: #171717 !important;
    box-shadow: 0 0 0 3px rgba(23,23,23,0.08) !important;
    outline: none !important;
}

/* primary button */
.stButton > button[kind="primary"],
.stButton > button {
    background: #171717 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.25rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    letter-spacing: -0.1px !important;
    cursor: pointer !important;
    transition: opacity 0.15s !important;
    width: auto !important;
    min-width: 110px !important;
}
.stButton > button:hover {
    opacity: 0.8 !important;
    color: #fff !important;
}

/* secondary / clear button */
button[data-testid="baseButton-secondary"] {
    background: #fff !important;
    color: #525252 !important;
    border: 1px solid #d4d4d4 !important;
    border-radius: 6px !important;
    font-size: 14px !important;
    font-weight: 400 !important;
}
button[data-testid="baseButton-secondary"]:hover {
    background: #f5f5f5 !important;
    color: #171717 !important;
}

/* download button */
.stDownloadButton > button {
    background: #fff !important;
    color: #171717 !important;
    border: 1px solid #d4d4d4 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 0.4rem 1rem !important;
}
.stDownloadButton > button:hover {
    background: #f5f5f5 !important;
    border-color: #a3a3a3 !important;
}

/* tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important;
    border-bottom: 1px solid #e5e5e5 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #737373 !important;
    padding: 8px 16px !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
}
.stTabs [aria-selected="true"] {
    color: #171717 !important;
    border-bottom: 2px solid #171717 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.25rem !important;
}

/* expanders */
details {
    border: 1px solid #e5e5e5 !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
    overflow: hidden !important;
}
summary {
    padding: 10px 14px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #171717 !important;
    cursor: pointer !important;
    background: #fafafa !important;
}
summary:hover { background: #f0f0f0 !important; }

/* agent log card */
.log-card {
    background: #fafafa;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 8px;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.6;
}
.log-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 5px 0;
    border-bottom: 1px solid #efefef;
    color: #404040;
}
.log-row:last-child { border-bottom: none; }
.log-tag {
    flex-shrink: 0;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 2px 7px;
    border-radius: 4px;
    min-width: 90px;
    text-align: center;
}
.log-tag.orchestrator { background: #ede9fe; color: #5b21b6; }
.log-tag.researcher   { background: #dbeafe; color: #1d4ed8; }
.log-tag.critic       { background: #fef3c7; color: #92400e; }
.log-tag.synthesizer  { background: #dcfce7; color: #166534; }
.log-msg { color: #525252; word-break: break-word; }

/* hero */
.hero-title {
    font-size: 28px;
    font-weight: 600;
    color: #171717;
    letter-spacing: -0.5px;
    margin: 0 0 6px;
    line-height: 1.2;
}
.hero-sub {
    font-size: 15px;
    color: #737373;
    margin: 0 0 20px;
    line-height: 1.5;
}
.badge-row { margin-bottom: 20px; }
.badge {
    display: inline-block;
    background: #f5f5f5;
    color: #404040;
    font-size: 11px;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 4px;
    border: 1px solid #e5e5e5;
    margin-right: 6px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.02em;
}
.divider { border: none; border-top: 1px solid #e5e5e5; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_api_key() -> str | None:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        key = st.session_state.get("api_key", "")
    return key or None


TAG_CSS = {
    "orchestrator": "orchestrator",
    "researcher":   "researcher",
    "critic":       "critic",
    "synthesizer":  "synthesizer",
}


def run_pipeline(topic: str, api_key: str, log_slot):
    from src.agents.orchestrator import ResearchPipeline

    log: list[tuple[str, str]] = []

    def render():
        rows = ""
        for role, msg in log[-25:]:
            cls = TAG_CSS.get(role.lower(), "orchestrator")
            safe = msg[:200].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", " ")
            rows += (
                f'<div class="log-row">'
                f'<span class="log-tag {cls}">{role}</span>'
                f'<span class="log-msg">{safe}</span>'
                f'</div>'
            )
        log_slot.markdown(f'<div class="log-card">{rows}</div>', unsafe_allow_html=True)

    def on_step(role: str, msg: str):
        log.append((role, msg))
        render()

    base_url = os.getenv("ANTHROPIC_BASE_URL")
    pipeline = ResearchPipeline(api_key=api_key, base_url=base_url)
    return asyncio.run(pipeline.run(topic, on_step=on_step))


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("**Deep Research Agent**")
    st.caption("Multi-agent research on Claude")
    st.divider()

    key_in_env = bool(os.getenv("ANTHROPIC_API_KEY"))

    if key_in_env:
        st.success("API key loaded from environment", icon="✓")
    else:
        api_key_input = st.text_input(
            "Anthropic API Key",
            type="password",
            value=st.session_state.get("api_key", ""),
            placeholder="sk-ant-...",
        )
        if api_key_input:
            st.session_state["api_key"] = api_key_input

    st.divider()
    st.markdown("**How it works**")
    st.markdown("""
1. **Orchestrator** splits your question into sub-queries
2. **Researchers** (parallel) search the web and read pages
3. **Critic** reviews findings for gaps
4. **Synthesizer** writes the final report
""")
    st.divider()
    st.markdown(
        "Claude claude-sonnet-4-6 · Anthropic SDK · Streamlit\n\n"
        "→ [GitHub](https://github.com/daY0k/deep-research-agent)"
    )


# ── Main page ─────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">Deep Research Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Ask any question — parallel agents search, critique, and write a structured report.</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="badge-row">'
    '<span class="badge">claude-sonnet-4-6</span>'
    '<span class="badge">multi-agent</span>'
    '<span class="badge">web search</span>'
    '<span class="badge">tool use</span>'
    '</div>',
    unsafe_allow_html=True,
)

topic = st.text_area(
    "question",
    placeholder="e.g. What are the best practices for building production AI agents in 2025?",
    height=80,
    label_visibility="collapsed",
)

col_run, col_clear = st.columns([2, 1])
with col_run:
    run_btn = st.button("Run research", type="primary", use_container_width=True)
with col_clear:
    clear_btn = st.button("Clear", use_container_width=True)

if clear_btn:
    st.session_state.pop("last_result", None)
    st.rerun()

if run_btn:
    api_key = get_api_key()
    if not topic.strip():
        st.warning("Enter a question first.")
    elif not api_key:
        st.error("API key required. Enter it in the sidebar or set ANTHROPIC_API_KEY env var.")
    else:
        st.session_state["last_topic"] = topic
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("**Agent log**")
        log_slot = st.empty()

        with st.spinner("Agents working…"):
            t0 = time.time()
            try:
                result = run_pipeline(topic, api_key, log_slot)
                st.session_state["last_result"] = result
                st.success(f"Done in {time.time() - t0:.1f}s")
            except Exception as exc:
                st.error(f"Pipeline error: {exc}")
                st.stop()

# ── Results ───────────────────────────────────────────────────────────────────
if "last_result" in st.session_state:
    res = st.session_state["last_result"]

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(f"### {res['topic']}")

    tab_rep, tab_raw, tab_crit = st.tabs(["Report", "Raw findings", "Critique"])

    with tab_rep:
        st.markdown(res["report"])
        st.download_button(
            "Download report (.md)",
            data=res["report"].encode(),
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_raw:
        for i, (q, text) in enumerate(res["findings"], 1):
            with st.expander(f"{i}. {q}"):
                st.markdown(text)

    with tab_crit:
        st.markdown(res["critique"])
