"""
Streamlit Web UI for Deep Research Agent.
"""

import asyncio
import os
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Must be first Streamlit call
st.set_page_config(
    page_title="Deep Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS ---
st.markdown("""
<style>
    .step-box {
        padding: 0.5rem 1rem;
        border-left: 3px solid #4CAF50;
        margin: 0.3rem 0;
        background: #f9f9f9;
        font-size: 0.85rem;
        color: #333;
    }
    .step-box.critic { border-color: #FF9800; }
    .step-box.synthesizer { border-color: #2196F3; }
    .step-box.orchestrator { border-color: #9C27B0; }
    .agent-tag {
        font-weight: bold;
        text-transform: uppercase;
        font-size: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)


def get_api_key() -> str | None:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        key = st.session_state.get("api_key", "")
    return key or None


def run_pipeline(topic: str, api_key: str, log_container, result_container):
    """Run the async pipeline, updating Streamlit in real time."""
    from src.agents.orchestrator import ResearchPipeline

    steps_log = []

    def on_step(step: str, msg: str):
        steps_log.append((step, msg))
        with log_container:
            for s, m in steps_log[-15:]:
                css_class = s.lower()
                short_msg = m[:200].replace("\n", " ")
                st.markdown(
                    f'<div class="step-box {css_class}">'
                    f'<span class="agent-tag">{s}</span> — {short_msg}'
                    f"</div>",
                    unsafe_allow_html=True,
                )

    base_url = os.getenv("ANTHROPIC_BASE_URL")
    pipeline = ResearchPipeline(api_key=api_key, base_url=base_url)

    result = asyncio.run(pipeline.run(topic, on_step=on_step))
    return result


# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Settings")

    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        value=st.session_state.get("api_key", ""),
        placeholder="sk-ant-...",
        help="Get your key at console.anthropic.com",
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input

    st.markdown("---")
    st.markdown("**Architecture**")
    st.markdown("""
```
Orchestrator
    ↓ decomposes
[Researcher × N]  ← parallel
    ↓ findings
  Critic
    ↓ evaluation
 Synthesizer
    ↓
 Final Report
```
""")
    st.markdown("---")
    st.markdown("**Stack**: Claude claude-sonnet-4-6 · Anthropic SDK · Streamlit")
    st.markdown("**Source**: [GitHub](https://github.com)")


# --- Main ---
st.title("🔬 Deep Research Agent")
st.caption("Multi-agent AI research system powered by Claude")

topic = st.text_area(
    "Research question",
    placeholder="e.g. What are the latest advances in multi-agent LLM systems in 2025?",
    height=80,
)

col1, col2 = st.columns([1, 4])
with col1:
    run_btn = st.button("🚀 Research", type="primary", use_container_width=True)
with col2:
    if st.button("🗑 Clear", use_container_width=False):
        for key in ["last_result", "last_topic"]:
            st.session_state.pop(key, None)
        st.rerun()


if run_btn:
    api_key = get_api_key()

    if not topic.strip():
        st.error("Enter a research question.")
    elif not api_key:
        st.error("Anthropic API key required. Enter it in the sidebar.")
    else:
        st.session_state["last_topic"] = topic

        log_col, _ = st.columns([1, 0])

        with st.expander("📡 Live agent log", expanded=True):
            log_container = st.container()

        with st.spinner("Agents working..."):
            start = time.time()
            try:
                result = run_pipeline(topic, api_key, log_container, None)
                st.session_state["last_result"] = result
                elapsed = time.time() - start
                st.success(f"Research complete in {elapsed:.1f}s")
            except Exception as e:
                st.error(f"Pipeline error: {e}")
                st.stop()


# --- Display result ---
if "last_result" in st.session_state:
    result = st.session_state["last_result"]

    st.markdown("---")
    st.markdown(f"## 📄 Report: {result['topic']}")

    tab_report, tab_findings, tab_critique = st.tabs(
        ["📑 Final Report", "🔍 Raw Findings", "⚠️ Critique"]
    )

    with tab_report:
        st.markdown(result["report"])

        report_bytes = result["report"].encode("utf-8")
        st.download_button(
            "⬇️ Download Report (Markdown)",
            data=report_bytes,
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_findings:
        for i, (q, findings) in enumerate(result["findings"], 1):
            with st.expander(f"Sub-query {i}: {q}"):
                st.markdown(findings)

    with tab_critique:
        st.markdown(result["critique"])
