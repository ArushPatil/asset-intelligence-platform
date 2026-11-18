"""
Query Section Component Module.

A form for free-text questions plus preset buttons. A preset runs straight away; the old
version only changed session state, which the keyed text input then ignored.
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


def render_query_section() -> Optional[str]:
    """Render the question form and presets. Returns the question to run, or None."""
    with st.form("ask", border=False):
        col_input, col_btn = st.columns([6, 1], vertical_alignment="bottom")
        typed = col_input.text_input(
            "Question",
            placeholder="Ask about AHU-01: why a room is warm, its parts, its sensors, its manual…",
        )
        asked = col_btn.form_submit_button("Ask", type="primary", use_container_width=True)

    preset = None
    cols = st.columns(len(PRESETS))
    for col, (label, question) in zip(cols, PRESETS.items()):
        if col.button(label, use_container_width=True, help=question):
            preset = question

    if preset:
        return preset
    if asked:
        if typed.strip():
            return typed.strip()
        st.warning("Type a question first.")
    return None
