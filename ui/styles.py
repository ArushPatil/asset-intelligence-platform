"""
UI Styles Module.

Apple-style dark theme, built to the HIG's two-layer model (apple-design skill, liquid-glass.md):
- Content layer: opaque cards on a softly coloured ground. No glass here.
- Functional layer: glass only on the floating chrome (sidebar, top edge, ask bar).
Colours are iOS dark-mode system colours (systemBlue, secondaryLabel, separator…), as listed
in sarunw.com/posts/dark-color-cheat-sheet; web has no API for them, so they are hard-coded.
"""

import streamlit as st

CSS = """
<style>
:root {
    --bg: #000000;
    --card: #1c1c1e;
    --fill: rgba(118, 118, 128, .24);
    --fill-strong: rgba(255, 255, 255, .16);
    --ink: #ffffff;
    --muted: rgba(235, 235, 245, .6);
    --line: rgba(84, 84, 88, .6);
    --accent: #0a84ff;
    --on-accent: #ffffff;
    --ok: #30d158;
    --warn: #ff9f0a;
    --crit: #ff453a;
    --radius: 22px;
    --glass-bg: rgba(30, 30, 34, .55);
    --glass-edge: rgba(255, 255, 255, .14);
    --glass-blur: blur(28px) saturate(1.5);
    --font: -apple-system, BlinkMacSystemFont, system-ui, "Segoe UI", sans-serif;
    --rounded: ui-rounded, "SF Pro Rounded", -apple-system, system-ui, sans-serif;
}

html, body, .stApp, button, input, textarea { font-family: var(--font); -webkit-font-smoothing: antialiased; }
code, .mono { font-family: ui-monospace, "SF Mono", Menlo, monospace; }
footer { visibility: hidden; }

/* Content layer: colour lives in the ground, so the glass above has something to pick up. */
.stApp {
    background:
        radial-gradient(55% 45% at 0% 0%, rgba(10, 132, 255, .18), transparent 70%),
        radial-gradient(45% 40% at 100% 0%, rgba(94, 92, 230, .18), transparent 70%),
        radial-gradient(60% 50% at 50% 110%, rgba(10, 132, 255, .10), transparent 70%),
        var(--bg);
    background-attachment: fixed;
}
.block-container { padding-top: 3.5rem; padding-bottom: 2rem; max-width: 1200px; }

/* Cards: opaque, rounded, no border. */
/* Cards are containers keyed "card_*" (Streamlit adds the class st-key-card_*). */
/* KPI row: equal-height cards. */
.st-key-kpis [data-testid="stHorizontalBlock"] { align-items: stretch; }
.st-key-kpis [data-testid="stColumn"] > div, .st-key-kpis [data-testid="stLayoutWrapper"], .st-key-kpis [class*="st-key-card"] { height: 100%; }
[class*="st-key-card"] { background: var(--card); border-radius: var(--radius) !important; border: none !important; padding: 18px 20px !important; }

/* ---------- Functional layer: Liquid Glass, three surfaces only ---------- */

/* 1. Top edge: a scroll-edge blur and fade, no solid bar. */
[data-testid="stHeader"] {
    background: linear-gradient(to bottom, rgba(0, 0, 0, .55), transparent);
    -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px);
    -webkit-mask-image: linear-gradient(to bottom, #000 55%, transparent);
    mask-image: linear-gradient(to bottom, #000 55%, transparent);
}

/* 2. Sidebar: a floating glass panel inset from the window edge. */
section[data-testid="stSidebar"] { background: transparent; border: none; }
section[data-testid="stSidebar"] > div:first-child {
    margin: 12px; width: calc(100% - 24px); height: calc(100% - 24px); border-radius: 26px;
    background: var(--glass-bg); border: 1px solid var(--glass-edge);
    -webkit-backdrop-filter: var(--glass-blur); backdrop-filter: var(--glass-blur);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .08), 0 20px 50px rgba(0, 0, 0, .35);
}

/* 3. Ask bar: a floating glass capsule at the bottom, like Safari's address bar.
   Sticky inside the main column (rendered last), so it never covers the sidebar. */
[data-testid="stLayoutWrapper"]:has(> .st-key-askbar) { position: sticky; bottom: 16px; z-index: 50; margin-top: 24px; }
.st-key-askbar {
    margin: 0 auto; width: min(760px, 100%);
    padding: 6px 6px 6px 18px; border-radius: 999px;
    background: var(--glass-bg); border: 1px solid var(--glass-edge);
    -webkit-backdrop-filter: var(--glass-blur); backdrop-filter: var(--glass-blur);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .10), 0 18px 40px rgba(0, 0, 0, .45);
}
.st-key-askbar [data-testid="stForm"] { padding: 0; border: none; }
/* Keep input and button on one row on phones (Streamlit stacks columns below 640px). */
.st-key-askbar [data-testid="stHorizontalBlock"] { flex-wrap: nowrap; }
.st-key-askbar [data-testid="stColumn"] { min-width: 0 !important; flex: 1 1 auto !important; width: auto !important; }
.st-key-askbar [data-testid="stColumn"]:last-child { flex: 0 0 84px !important; }
.st-key-askbar [data-testid="stTextInputRootElement"], .st-key-askbar [data-baseweb="input"],
.st-key-askbar [data-baseweb="base-input"], .st-key-askbar input { background: transparent !important; border: none !important; box-shadow: none !important; }
.st-key-askbar input { font-size: 17px; color: var(--ink); padding-left: 0; }
.st-key-askbar input::placeholder { color: var(--muted); }

/* Accessibility states: opaque glass when transparency is reduced, stronger edges for more contrast. */
@media (prefers-reduced-transparency: reduce) {
    section[data-testid="stSidebar"] > div:first-child, .st-key-askbar {
        background: var(--card); -webkit-backdrop-filter: none; backdrop-filter: none;
    }
}
@media (prefers-contrast: more) {
    :root { --glass-edge: rgba(255, 255, 255, .5); --muted: rgba(235, 235, 245, .8); }
    section[data-testid="stSidebar"] > div:first-child, .st-key-askbar { background: var(--card); }
}

/* ---------- Type ---------- */

.ai-header { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
.ai-eyebrow { font-size: 15px; font-weight: 600; color: var(--muted); }
.ai-title { font-size: 34px; line-height: 41px; font-weight: 700; letter-spacing: .01em; color: var(--ink); margin: 0; padding: 0; }
.ai-sub { font-size: 17px; color: var(--muted); margin-top: 6px; }
.label { font-size: 20px; font-weight: 600; color: var(--ink); margin: 2px 0 10px; }

/* Status: plain coloured text with a dot, never colour alone. */
.pill { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: var(--muted); white-space: nowrap; }
.pill::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
.pill.ok { color: var(--ok); }
.pill.warn { color: var(--warn); }
.pill.crit { color: var(--crit); }
.pill.plain::before { display: none; }

/* KPI widgets: rounded numerals are the one signature, as in Apple's Weather and Fitness widgets. */
[data-testid="stMetric"] label p { font-size: 15px; font-weight: 600; color: var(--muted); }
[data-testid="stMetricValue"] { font-family: var(--rounded); font-size: clamp(22px, 1.9vw, 30px); font-weight: 600; white-space: nowrap !important; font-variant-numeric: tabular-nums; }
[data-testid="stMetricDelta"] { background: transparent !important; padding: 0 !important; font-variant-numeric: tabular-nums; font-weight: 500; }
[data-testid="stMetric"] *, .stButton button * { white-space: normal !important; overflow: visible !important; text-overflow: clip !important; overflow-wrap: normal !important; word-break: normal !important; }
[data-testid="stMetricValue"] * { white-space: nowrap !important; }
[data-testid="stCaptionContainer"] { color: var(--muted); }

/* ---------- Controls ---------- */

/* Suggestion chips: grey capsules, monochrome. */
.stButton button {
    border-radius: 999px; min-height: 44px; border: none; background: var(--fill); color: var(--ink);
    font-size: 15px; font-weight: 500; transition: transform .12s ease, background .12s ease;
}
.stButton button:hover { background: var(--fill-strong); color: var(--ink); }
/* The one tinted control: the primary action colours its background, not its label. */
.stFormSubmitButton button {
    border-radius: 999px; min-height: 44px; border: none; background: var(--accent); color: var(--on-accent);
    font-size: 17px; font-weight: 600; transition: transform .12s ease;
}
.stFormSubmitButton button:hover { background: var(--accent); color: var(--on-accent); filter: brightness(1.08); }
.stButton button:active, .stFormSubmitButton button:active { transform: scale(.96); }

/* Segmented controls and tabs: iOS-style track with a raised thumb. */
[data-testid="stButtonGroup"] [role="radiogroup"], [role="tablist"] {
    background: var(--fill); border-radius: 18px; padding: 3px; gap: 2px; flex-wrap: wrap; width: fit-content; max-width: 100%;
}
[data-testid="stButtonGroup"] button p { font-size: 15px; }
[data-testid="stButtonGroup"] button { border: none !important; border-radius: 999px !important; background: transparent; color: var(--ink); min-height: 36px; padding: 0 14px; font-size: 15px; font-weight: 500; }
[data-testid="stButtonGroup"] button[aria-checked="true"] { background: var(--fill-strong) !important; color: var(--ink) !important; box-shadow: 0 2px 8px rgba(0, 0, 0, .3); }
[role="tablist"] [role="tab"] { border-radius: 999px; padding: 0 14px; min-height: 36px; height: 36px; border: none !important; box-shadow: none !important; }
[role="tablist"] [role="tab"][aria-selected="true"] { background: var(--fill-strong); box-shadow: 0 2px 8px rgba(0, 0, 0, .3) !important; }
[role="tablist"] [role="tab"] p { font-size: 15px; font-weight: 500; color: var(--ink) !important; }
[role="tablist"] [role="tab"]::after, [role="tablist"]::after { display: none !important; }

@media (prefers-reduced-motion: reduce) {
    .stButton button, .stFormSubmitButton button { transition: none; transform: none !important; }
}

/* ---------- Content details ---------- */

.answer-meta { display: flex; gap: 14px; flex-wrap: wrap; align-items: center; margin-top: 4px; }
.props { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px 24px; }
.prop-k { font-size: 13px; font-weight: 600; color: var(--muted); }
.prop-v { font-size: 17px; color: var(--ink); margin-top: 2px; }
.passage { border-left: 3px solid var(--line); padding: 4px 0 4px 14px; margin: 4px 0 18px; }
.passage-meta { font-size: 13px; color: var(--muted); margin-bottom: 6px; }
.passage-text { font-size: 15px; line-height: 1.55; color: var(--ink); white-space: pre-wrap; }

/* Sidebar rows: an inset grouped list. */
.src-list { background: rgba(255, 255, 255, .05); border-radius: 14px; padding: 0 14px; }
.src-row { display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 12px 0; border-bottom: 1px solid var(--line); }
.src-row:last-child { border-bottom: none; }
.src-name { font-size: 15px; font-weight: 600; color: var(--ink); }
.src-detail { font-size: 13px; color: var(--muted); margin-top: 2px; }
</style>
"""


def inject_custom_css() -> None:
    """Inject the shared stylesheet."""
    st.markdown(CSS, unsafe_allow_html=True)
