"""
UI Styles Module.

Dark theme. One small stylesheet on top of the Streamlit theme in .streamlit/config.toml.
Colours live as CSS tokens on :root so every component draws from the same set.
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --ink: #e8eaed;
    --muted: #9aa1ab;
    --line: #262a31;
    --surface: #171a1f;
    --ground: #0f1115;
    --accent: #2dd4bf;
    --accent-soft: rgba(45, 212, 191, .12);
    --ok: #4ade80;
    --warn: #fbbf24;
    --warn-soft: rgba(251, 191, 36, .12);
    --crit: #f87171;
    --crit-soft: rgba(248, 113, 113, .12);
    --radius: 10px;
}

/* Not [class*="st-"]: that also hits Streamlit's icon spans and shows icon names as text. */
html, body, .stApp, button, input, textarea {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
code, .mono { font-family: "JetBrains Mono", ui-monospace, monospace; }

.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1280px; }
footer { visibility: hidden; }
.stApp { background: var(--ground); }
[data-testid="stVerticalBlockBorderWrapper"] { background: var(--surface); }

/* Header */
.ai-header { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; }
.ai-eyebrow { font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); }
.ai-title { font-size: 28px; font-weight: 700; letter-spacing: -0.02em; color: var(--ink); margin: 2px 0 0; line-height: 1.2; }
.ai-sub { font-size: 14px; color: var(--muted); margin-top: 4px; }

/* Pills */
.pill { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 999px; border: 1px solid var(--line); background: transparent; color: var(--ink); white-space: nowrap; }
.pill::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
.pill.ok { color: var(--ok); background: rgba(74, 222, 128, .10); border-color: transparent; }
.pill.warn { color: var(--warn); background: var(--warn-soft); border-color: transparent; }
.pill.crit { color: var(--crit); background: var(--crit-soft); border-color: transparent; }
.pill.off, .pill.idle { color: var(--muted); }
.pill.plain::before { display: none; }

/* Metric cards (st.metric inside bordered containers) */
[data-testid="stMetric"] label p { font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
[data-testid="stMetricValue"] { font-size: clamp(18px, 1.9vw, 26px); font-weight: 700; letter-spacing: -0.01em; }

/* Narrow screens: wrap labels instead of cutting them off with an ellipsis. */
[data-testid="stMetric"] *, .stButton button * { white-space: normal !important; overflow: visible !important; text-overflow: clip !important; overflow-wrap: normal !important; word-break: normal !important; }

/* Section labels */
.label { font-size: 12px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); margin: 8px 0 8px; }

/* Answer */
.answer-meta { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 4px; }

/* Property grid for the asset tab */
.props { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 14px 24px; }
.prop-k { font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
.prop-v { font-size: 14px; color: var(--ink); margin-top: 2px; }

/* Document passages */
.passage { border-left: 3px solid var(--accent); padding: 4px 0 4px 14px; margin: 4px 0 18px; }
.passage-meta { font-size: 12px; color: var(--muted); margin-bottom: 6px; }
.passage-text { font-size: 14px; line-height: 1.6; color: var(--ink); white-space: pre-wrap; }

/* Sidebar */
section[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--line); }
.src-row { display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 10px 0; border-bottom: 1px solid var(--line); }
.src-name { font-size: 14px; font-weight: 600; color: var(--ink); }
.src-detail { font-size: 12px; color: var(--muted); margin-top: 2px; }

/* Buttons */
div.stButton > button, div.stFormSubmitButton > button { border-radius: 8px; font-weight: 600; min-height: 44px; transition: transform .12s ease, box-shadow .12s ease; }
div.stButton > button:hover { transform: translateY(-1px); }
div.stButton > button:active, div.stFormSubmitButton > button:active { transform: translateY(0); }

@media (prefers-reduced-motion: reduce) {
    div.stButton > button { transition: none; }
}
</style>
"""


def inject_custom_css() -> None:
    """Inject the shared stylesheet."""
    st.markdown(CSS, unsafe_allow_html=True)
