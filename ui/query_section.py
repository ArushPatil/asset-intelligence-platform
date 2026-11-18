"""
Query Section Component Module.

Preset buttons near the top, plus the glass ask bar rendered last so it can stick to the
bottom of the main column. A preset runs straight away; a typed question is stored in
session state and run on the rerun, because the ask bar renders after the answer area.
"""

from typing import Optional

import streamlit as st

PRESETS = {
    "Why warm?": "Why is Conference Room A warmer than usual?",
    "Parts": "What components belong to AHU-01?",
    "Coil care": "What maintenance should be performed on the cooling coil?",
    "Supply temp": "What is the latest supply air temperature?",
    "Set points": "What are the recommended operating conditions?",
}


def render_presets() -> Optional[str]:
    """Render the preset buttons. Returns the chosen question, or None."""
    st.markdown("<div class='label'>Suggestions</div>", unsafe_allow_html=True)
    preset = None
    for col, (label, question) in zip(st.columns(len(PRESETS)), PRESETS.items()):
        if col.button(label, use_container_width=True, help=question):
            preset = question
    return preset


def render_ask_bar() -> None:
    """Render the ask bar (styles.py, .st-key-askbar). Call it last in the main column."""
    with st.container(key="askbar"), st.form("ask", border=False, clear_on_submit=True):
        col_input, col_btn = st.columns([6, 1], vertical_alignment="center")
        typed = col_input.text_input(
            "Question", label_visibility="collapsed",
            placeholder="Ask about AHU-01: why a room is warm, its parts, its manual…",
        )
        asked = col_btn.form_submit_button("Ask", type="primary", use_container_width=True)
    if asked:
        if typed.strip():
            st.session_state["pending"] = typed.strip()
            st.rerun()
        st.toast("Type a question first.")
