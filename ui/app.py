"""
Streamlit Web UI for Deep Research Agent.
Design: Vercel-inspired (open-design/vercel DESIGN.md)
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
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'Geist', Arial, sans-serif;
    font-feature-settings: "liga";
    color: #171717;
    background: #ffffff;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #fafafa;
    border-right: 1px solid #ebebeb;
  }
  section[data-testid="stSidebar"] > div { padding-top: 24px; }

  /* Hide Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 40px; padding-bottom: 80px; max-width: 900px; }

  /* Typography */
  h1 { font-size: 32px; font-weight: 600; letter-spacing: -1.28px; line-height: 1.25; color: #171717; margin-bottom: 4px; }
  h2 { font-size: 24px; font-weight: 600; letter-spacing: -0.96px; color: #171717; }
  h3 { font-size: 18px; font-weight: 600; letter-spacing: -0.32px; color: #171717; }
  p, li { font-size: 16px; font-weight: 400; line-height: 1.5; color: #4d4d4d; }
  code, pre { font-family: 'Geist Mono', ui-monospace, SFMono-Regular, monospace; font-size: 13px; }

  /* Buttons */
  .stButton > button {
    background: #171717;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-family: 'Geist', Arial, sans-serif;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s ease;
  }
  .stButton > button:hover { background: #333333; }
  .stButton > button[kind="secondary"] {
    background: #ffffff;
    color: #171717;
    box-shadow: rgb(235,235,235) 0px 0px 0px 1px;
  }
  .stButton > button[kind="secondary"]:hover { background: #fafafa; }

  /* Text input */
  .stTextInput input, .stTextArea textarea {
    font-family: 'Geist', Arial, sans-serif;
    font-size: 14px;
    border-radius: 6px;
    border: 1px solid #ebebeb;
    color: #171717;
    background: #ffffff;
    box-shadow: rgba(0,0,0,0.04) 0px 2px 2px;
    transition: border 0.15s;
  }
  .stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #0072f5;
    outline: none;
    box-shadow: 0 0 0 2px hsla(212,100%,48%,0.2);
  }

  /* Cards */
  .card {
    background: #ffffff;
    border-radius: 8px;
    box-shadow: rgba(0,0,0,0.08) 0px 0px 0px 1px,
                rgba(0,0,0,0.04) 0px 2px 2px,
                #fafafa 0px 0px 0px 1px;
    padding: 20px 24px;
    margin: 12px 0;
  }

  /* Step log entries */
  .step {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: 8px 0;
    border-bottom: 1px solid #ebebeb;
    font-size: 13px;
  }
  .step:last-child { border-bottom: none; }
  .step-tag {
    font-family: 'Geist Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 2px 8px;
    border-radius: 9999px;
    white-space: nowrap;
    flex-shrink: 0;
  }
  .tag-orchestrator { background: #f0e6ff; color: #7928ca; }
  .tag-researcher   { background: #e6f0ff; color: #0068d6; }
  .tag-critic       { background: #fff3e6; color: #d97706; }
  .tag-synthesizer  { background: #e6ffe6; color: #16a34a; }
  .step-msg { color: #4d4d4d; line-height: 1.4; }

  /* Badge */
  .badge {
    display: inline-block;
    background: #ebf5ff;
    color: #0068d6;
    font-size: 12px;
    font-weight: 500;
    padding: 2px 10px;
    border-radius: 9999px;
    margin-right: 6px;
  }

  /* Expander */
  .streamlit-expanderHeader {
    font-family: 'Geist', Arial, sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: #171717;
    background: #fafafa;
    border-radius: 6px;
    border: 1px solid #ebebeb;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid #ebebeb;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: 'Geist', Arial, sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: #666666;
    padding: 8px 16px;
    border-radius: 6px 6px 0 0;
  }
  .stTabs [aria-selected="true"] {
    color: #171717;
    border-bottom: 2px solid #171717;
    background: transparent;
  }

  /* Alert boxes */
  .stAlert { border-radius: 6px; font-size: 14px; }

  /* Divider */
  hr { border: none; border-top: 1px solid #ebebeb; margin: 24px 0; }
</style>
""", unsafe_allow_html=True)


def get_api_key() -> str | None:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        key = st.session_state.get("api_key", "")
    return key or None


def run_pipeline(topic: str, api_key: str, log_placeholder):
    from src.agents.orchestrator import ResearchPipeline

    steps_log = []

    tag_map = {
        "orchestrator": "tag-orchestrator",
        "researcher":   "tag-researcher",
        "critic":       "tag-critic",
        "synthesizer":  "tag-synthesizer",
    }

    def render_log():
        html = '<div class="card" style="padding:16px 20px">'
        for s, m in steps_log[-20:]:
            tag_cls = tag_map.get(s.lower(), "tag-orchestrator")
            msg = m[:180].replace("<", "&lt;").replace(">", "&gt;").replace("\n", " ")
            html += (
                f'<div class="step">'
                f'<span class="step-tag {tag_cls}">{s}</span>'
                f'<span class="step-msg">{msg}</span>'
                f'</div>'
            )
        html += "</div>"
        log_placeholder.markdown(html, unsafe_allow_html=True)

    def on_step(step: str, msg: str):
        steps_log.append((step, msg))
        render_log()

    base_url = os.getenv("ANTHROPIC_BASE_URL")
    pipeline = ResearchPipeline(api_key=api_key, base_url=base_url)
    return asyncio.run(pipeline.run(topic, on_step=on_step))


# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⬡ Deep Research Agent")
    st.markdown('<hr>', unsafe_allow_html=True)

    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        value=st.session_state.get("api_key", ""),
        placeholder="sk-ant-...",
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input

    if os.getenv("ANTHROPIC_API_KEY"):
        st.markdown(
            '<span class="badge">✓ API key loaded from env</span>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown("**Pipeline**")
    st.markdown("""
```
Orchestrator
  └─ decomposes query
Researcher × N  (parallel)
  └─ web search + fetch
Critic
  └─ gaps & issues
Synthesizer
  └─ final report
```
""")
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown(
        "**Stack:** Claude claude-sonnet-4-6 · Anthropic SDK · asyncio · Streamlit\n\n"
        "[GitHub](https://github.com/daY0k/deep-research-agent)"
    )


# ── Main ─────────────────────────────────────────────────
st.markdown("# Deep Research Agent")
st.markdown(
    '<span class="badge">Multi-Agent</span>'
    '<span class="badge">Claude claude-sonnet-4-6</span>'
    '<span class="badge">Web Search</span>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="color:#666;margin-top:8px">Ask any question — parallel agents research, critique, and synthesize a structured report.</p>',
    unsafe_allow_html=True,
)

st.markdown('<hr>', unsafe_allow_html=True)

topic = st.text_area(
    "Research question",
    placeholder="e.g. What are the best practices for building production AI agents in 2025?",
    height=72,
    label_visibility="collapsed",
)

col_run, col_clear, col_pad = st.columns([1, 1, 6])
with col_run:
    run_btn = st.button("Research →", type="primary", use_container_width=True)
with col_clear:
    if st.button("Clear", use_container_width=True):
        st.session_state.pop("last_result", None)
        st.session_state.pop("last_topic", None)
        st.rerun()


if run_btn:
    api_key = get_api_key()

    if not topic.strip():
        st.error("Enter a research question.")
    elif not api_key:
        st.error("API key required — enter it in the sidebar.")
    else:
        st.session_state["last_topic"] = topic
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown("**Agent log**")
        log_placeholder = st.empty()

        with st.spinner(""):
            start = time.time()
            try:
                result = run_pipeline(topic, api_key, log_placeholder)
                st.session_state["last_result"] = result
                elapsed = time.time() - start
                st.success(f"Done in {elapsed:.1f}s")
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()


if "last_result" in st.session_state:
    result = st.session_state["last_result"]

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown(f"## {result['topic']}")

    tab_report, tab_findings, tab_critique = st.tabs([
        "Report", "Raw Findings", "Critique"
    ])

    with tab_report:
        st.markdown(result["report"])
        st.download_button(
            "Download .md",
            data=result["report"].encode("utf-8"),
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_findings:
        for i, (q, findings) in enumerate(result["findings"], 1):
            with st.expander(f"{i}. {q}"):
                st.markdown(findings)

    with tab_critique:
        st.markdown(result["critique"])
