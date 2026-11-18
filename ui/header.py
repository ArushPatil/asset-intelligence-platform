"""
Header Component Module.

Page title, facility and asset, plus one overall status pill derived from the anomaly count.
"""

from html import escape

import streamlit as st


def render_header(facility: str, asset: str, anomaly_count: int) -> None:
    """Render the page header."""
    if anomaly_count:
        pill = f"<span class='pill warn'>{anomaly_count} anomalies in last 24 h</span>"
    else:
        pill = "<span class='pill ok'>No anomalies in last 24 h</span>"
    st.markdown(
        f"""
        <div class="ai-header">
            <div>
                <div class="ai-eyebrow">{escape(facility)}</div>
                <h1 class="ai-title">Asset Intelligence</h1>
                <div class="ai-sub">Ask about {escape(asset)}: its topology, sensors and OEM manuals, in one answer.</div>
            </div>
            {pill}
        </div>
        """,
        unsafe_allow_html=True,
    )
