"""
Evidence Views Component Module.

Tabs for the evidence behind an answer: telemetry chart, asset graph, manual passages and
the execution trace. Every tab shows only what the backend returned; when a source was not
used or failed, the tab says so instead of showing placeholder data.
"""

from html import escape
from typing import Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from llm.models import AssetContext, DocumentContext, OrchestratorResponse

from .data import METRICS, load_telemetry, telemetry_anomalies

# Dark-surface steps validated with the dataviz skill's validate_palette.js (surface #171a1f).
ACCENT, ANOMALY, SURFACE, GRID, INK, MUTED = "#1f9e8f", "#e5534b", "#171a1f", "#262a31", "#c3c7ce", "#9aa1ab"


def render_telemetry_chart(metric: str, key: str) -> None:
    """Line chart of one metric with its z-score anomalies marked."""
    df = load_telemetry()
    meta = METRICS[metric]
    anomalies = telemetry_anomalies(metric)
    fig = go.Figure(go.Scatter(
        x=df["timestamp"], y=df[metric], mode="lines", name=meta["label"],
        line=dict(color=ACCENT, width=2),
        hovertemplate=f"%{{x|%d %b %H:%M}}<br>%{{y:.2f}} {meta['unit']}<extra></extra>",
    ))
    fig.add_hline(y=df[metric].mean(), line=dict(color=MUTED, dash="dot", width=1),
                  annotation_text="24 h avg", annotation_position="top left")
    if anomalies:
        a = pd.DataFrame(anomalies)
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(a["timestamp"]), y=a["value"], mode="markers", name="Anomaly",
            marker=dict(color=ANOMALY, size=9, line=dict(color=SURFACE, width=2)),
            customdata=a["z_score"],
            hovertemplate=f"%{{x|%d %b %H:%M}}<br>%{{y:.2f}} {meta['unit']} · z %{{customdata}}<extra></extra>",
        ))
    fig.update_layout(
        height=320, margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", x=0, y=1.08, font=dict(color=INK)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color=MUTED), hovermode="x unified",
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=GRID, font=dict(color=INK)),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, title_text=meta["unit"])
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.caption(f"{len(anomalies)} readings beyond 2.5 standard deviations of the 24 h mean."
               if anomalies else "No readings beyond 2.5 standard deviations of the 24 h mean.")


def _metric_picker(key: str, default: str) -> str:
    return st.segmented_control(
        "Metric", list(METRICS), default=default, key=key,
        format_func=lambda m: METRICS[m]["label"], label_visibility="collapsed",
    ) or default


def _props(items: Dict[str, str]) -> str:
    cells = "".join(
        f"<div><div class='prop-k'>{escape(k)}</div><div class='prop-v'>{escape(str(v))}</div></div>"
        for k, v in items.items() if v
    )
    return f"<div class='props'>{cells}</div>"


def _names(rows: List[dict]) -> str:
    return ", ".join(str(r.get("name")) for r in rows if r.get("name"))


def _asset_tab(ctx: Optional[AssetContext], error: Optional[str]) -> None:
    if ctx is None:
        st.info(f"Knowledge graph unavailable: {error}" if error else "This question did not need the knowledge graph.")
        return
    info = ctx.asset_info or {}
    health = ctx.health_status or {}
    st.markdown(_props({
        "Asset": info.get("name", ctx.asset_id),
        "Type": info.get("assetType"),
        "Manufacturer": (ctx.manufacturer or {}).get("name"),
        "Operating state": (ctx.operating_state or {}).get("name"),
        "Health": " · ".join(str(x) for x in (health.get("status"), health.get("score")) if x is not None),
        "Serves": _names(ctx.served_spaces),
        "Components": _names(ctx.components),
    }), unsafe_allow_html=True)
    if ctx.maintenance_history:
        st.markdown("<div class='label' style='margin-top:20px'>Maintenance history</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(ctx.maintenance_history), hide_index=True, use_container_width=True)


def _documents_tab(ctx: Optional[DocumentContext], error: Optional[str]) -> None:
    if not ctx or not ctx.retrieved_chunks:
        st.info(f"Manual search failed: {error}" if error else "No manual passages were retrieved for this question.")
        return
    for i, chunk in enumerate(ctx.retrieved_chunks[:3], 1):
        name = str(chunk.source_document).replace("\\", "/").split("/")[-1]
        st.markdown(
            f"<div class='passage'><div class='passage-meta'>#{i} · {escape(name)} · page {chunk.page_number}"
            f" · match {chunk.similarity_score:.2f}</div>"
            f"<div class='passage-text'>{escape(chunk.text.strip())}</div></div>",
            unsafe_allow_html=True,
        )


def _execution_tab(response: OrchestratorResponse) -> None:
    if response.execution_plan:
        st.markdown(f"**Plan:** {response.execution_plan.goal}")
    calls = pd.DataFrame([{
        "Service": sc.service,
        "Status": "OK" if sc.success else "Failed",
        "Time (ms)": round(sc.execution_time_ms, 1),
        "Records": sc.records_returned,
        "Error": sc.error_message or "",
    } for sc in response.service_calls])
    st.dataframe(calls, hide_index=True, use_container_width=True)
    st.caption(f"Total {response.total_execution_time_ms:,.0f} ms")
    with st.expander("Prompt sent to the model"):
        st.code(response.prompt_used, language=None, wrap_lines=True)


def render_evidence_section(response: OrchestratorResponse) -> None:
    """Render the evidence tabs for one answer."""
    errors = {sc.service: sc.error_message for sc in response.service_calls if not sc.success}
    tel, asset, docs, trace = st.tabs(["Telemetry", "Asset", "Manuals", "Trace"])
    with tel:
        default = response.intent.target_metric if response.intent.target_metric in METRICS else "supply_air_temperature"
        render_telemetry_chart(_metric_picker("evidence_metric", default), key="evidence_chart")
    with asset:
        _asset_tab(response.graph_context, errors.get("GraphService"))
    with docs:
        _documents_tab(response.document_context, errors.get("DocumentService"))
    with trace:
        _execution_tab(response)
