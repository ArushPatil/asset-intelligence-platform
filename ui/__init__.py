"""
UI Package for Asset Intelligence Platform.

Provides modular UI components for the Streamlit dashboard.
"""

from .styles import inject_custom_css
from .sidebar import render_sidebar
from .header import render_header
from .kpi_cards import render_kpi_cards
from .query_section import render_query_section
from .ai_diagnosis import render_ai_diagnosis
from .evidence_views import render_evidence_section, render_telemetry_chart

__all__ = [
    "inject_custom_css",
    "render_sidebar",
    "render_header",
    "render_kpi_cards",
    "render_query_section",
    "render_ai_diagnosis",
    "render_evidence_section",
    "render_telemetry_chart",
]
