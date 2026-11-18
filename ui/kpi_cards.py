"""
KPI Cards Component Module.

Latest reading per key sensor, with the change against the 24 h average.
All values come from the telemetry stream; nothing is hard-coded.
"""

import pandas as pd
import streamlit as st

from .data import METRICS, telemetry_anomalies

KPI_METRICS = ["supply_air_temperature", "return_air_temperature", "filter_pressure_drop", "fan_rpm"]
# For these, a rise is bad, so Streamlit should colour an increase red.
RISE_IS_BAD = {"supply_air_temperature", "return_air_temperature", "filter_pressure_drop"}


def render_kpi_cards(df: pd.DataFrame) -> None:
    """Render one metric card per key sensor."""
    cols = st.container(key="kpis").columns(len(KPI_METRICS))
    latest = df.iloc[-1]
    for col, metric in zip(cols, KPI_METRICS):
        meta = METRICS[metric]
        value = float(latest[metric])
        avg = float(df[metric].mean())
        n_anom = len(telemetry_anomalies(metric))
        with col, st.container(border=True, key=f"card_{metric}"):
            st.metric(
                label=meta["label"],
                value=f"{value:,.1f} {meta['unit']}",
                delta=f"{value - avg:+,.1f} ({(value - avg) / avg:+.1%})" if avg else f"{value - avg:+,.1f}",
                # A "+0.0" change is not a rise; grey it out instead of colouring it.
                delta_color="off" if abs(value - avg) < 0.05 else "inverse" if metric in RISE_IS_BAD else "normal",
            )
            note = f"{n_anom} anomalies" if n_anom else "No anomalies"
            st.caption(f"vs 24 h avg · {note} · {latest['timestamp']:%H:%M}")
