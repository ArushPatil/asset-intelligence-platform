"""
Answer Component Module.

Renders the synthesised answer as plain Markdown (no raw HTML, so model output cannot
inject markup), with the sources used, the backend that wrote it and the latency.
"""

import re

import streamlit as st

from llm.models import OrchestratorResponse

SOURCES = {"GraphService": "Graph", "TelemetryService": "Telemetry", "DocumentService": "Manuals"}


def _to_markdown(text: str) -> str:
    # "•" bullets are not Markdown lists; "$" would start LaTeX in Streamlit.
    text = re.sub(r"^\s*•\s*", "- ", text, flags=re.M)
    return text.replace("$", r"\$")


def render_ai_diagnosis(response: OrchestratorResponse) -> None:
    """Render the answer card."""
    pills = []
    for sc in response.service_calls:
        if sc.service in SOURCES:
            state = "ok" if sc.success else "crit"
            note = f"{sc.records_returned} records" if sc.success else "failed"
            pills.append(f"<span class='pill {state}'>{SOURCES[sc.service]} · {note}</span>")
    backend = "Local template (no API key)" if response.llm_backend == "local" else response.llm_backend
    pills.append(f"<span class='pill plain'>{backend}</span>")
    pills.append(f"<span class='pill plain'>{response.total_execution_time_ms / 1000:.1f} s</span>")

    with st.container(border=True):
        st.markdown("<div class='label'>Answer</div>", unsafe_allow_html=True)
        st.markdown(f"**{_to_markdown(response.user_question)}**")
        st.markdown(_to_markdown(response.final_answer))
        st.markdown(f"<div class='answer-meta'>{''.join(pills)}</div>", unsafe_allow_html=True)
