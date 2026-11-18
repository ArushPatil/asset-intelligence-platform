"""
Sidebar Component Module.

Shows the real state of each data source, probed at render time rather than hard-coded.
"""

from html import escape

import streamlit as st

from .data import document_status, llm_status, load_telemetry, neo4j_status

STATE_TEXT = {"ok": "Online", "warn": "Fallback", "off": "Offline", "idle": "Idle", "crit": "Error"}


def _row(name: str, status: dict) -> str:
    state = status["state"]
    return (
        f"<div class='src-row'><div><div class='src-name'>{escape(name)}</div>"
        f"<div class='src-detail'>{escape(status['detail'])}</div></div>"
        f"<span class='pill {state}'>{STATE_TEXT[state]}</span></div>"
    )


def _telemetry_status() -> dict:
    try:
        df = load_telemetry()
        span = df["timestamp"].max() - df["timestamp"].min()
        hours = span.total_seconds() / 3600
        return {"state": "ok", "detail": f"{len(df):,} readings over {hours:.0f} h"}
    except Exception as e:
        return {"state": "crit", "detail": str(e)[:80]}


def render_sidebar() -> None:
    """Render data source status in the sidebar."""
    with st.sidebar:
        st.markdown("<div class='label'>Data sources</div>", unsafe_allow_html=True)
        rows = [
            _row("Knowledge graph", neo4j_status()),
            _row("Telemetry", _telemetry_status()),
            _row("OEM manuals", document_status()),
            _row("Language model", llm_status()),
        ]
        st.markdown("".join(rows), unsafe_allow_html=True)
        st.caption("Offline sources are skipped; answers use whatever is available.")
