"""
Shared, cached data access for the UI.

The orchestrator (and its document index) is built once per server process, not on every
Streamlit rerun. Telemetry for the overview is read through the same TelemetryService the
orchestrator uses, so the dashboard and the answers always agree.
"""

from typing import Dict, List

import pandas as pd
import streamlit as st

from graph.neo4j_client import Neo4jClient
from llm.orchestrator import LLMOrchestrator
from telemetry.telemetry_analysis import TelemetryAnalyzer

DEFAULT_TELEMETRY_FILE = "sample_ahu_telemetry.csv"
ANOMALY_Z = 2.5

METRICS: Dict[str, Dict[str, str]] = {
    "supply_air_temperature": {"label": "Supply air temp", "unit": "°C"},
    "return_air_temperature": {"label": "Return air temp", "unit": "°C"},
    "humidity": {"label": "Humidity", "unit": "%"},
    "fan_rpm": {"label": "Fan speed", "unit": "RPM"},
    "energy_consumption": {"label": "Energy", "unit": "kWh"},
    "filter_pressure_drop": {"label": "Filter pressure drop", "unit": "Pa"},
}


@st.cache_resource(show_spinner=False)
def get_orchestrator() -> LLMOrchestrator:
    """One orchestrator per server process; its vector index survives reruns."""
    return LLMOrchestrator()


@st.cache_data(show_spinner=False)
def load_telemetry() -> pd.DataFrame:
    """Load the telemetry stream through the orchestrator's own TelemetryService."""
    return get_orchestrator().telemetry_service.load_stream(DEFAULT_TELEMETRY_FILE).copy()


@st.cache_data(show_spinner=False)
def telemetry_anomalies(metric: str) -> List[dict]:
    """Z-score anomalies for one metric, same threshold the orchestrator uses."""
    return TelemetryAnalyzer(load_telemetry()).detect_simple_anomalies(metric, z_threshold=ANOMALY_Z)


@st.cache_data(ttl=30, show_spinner=False)
def neo4j_status() -> Dict[str, str]:
    """Probe Neo4j once every 30 s; return state and a short detail line."""
    client = Neo4jClient()
    try:
        client.connect()
        return {"state": "ok", "detail": client.uri}
    except Exception as e:  # any failure means the graph is unavailable to the user
        reason = str(e).split(":")[-1].strip() or "unreachable"
        return {"state": "off", "detail": f"Unreachable at {client.uri} ({reason[:60]})"}
    finally:
        client.close()


def llm_status() -> Dict[str, str]:
    """Which language model backend will answer."""
    client = get_orchestrator().llm_client
    if client._gemini_client is not None:
        return {"state": "ok", "detail": "Gemini API key found"}
    if client._openai_client is not None:
        return {"state": "ok", "detail": f"OpenAI {client.model_name}"}
    return {"state": "warn", "detail": "No API key: local template engine"}


def document_status() -> Dict[str, str]:
    """Whether the OEM manual index is built yet (it builds on the first document question)."""
    svc = get_orchestrator().document_service
    if svc._is_indexed:
        return {"state": "ok", "detail": f"{len(svc.vector_store._chunks):,} chunks indexed"}
    return {"state": "idle", "detail": "Indexes on first manual question"}
