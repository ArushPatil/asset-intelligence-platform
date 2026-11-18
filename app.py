"""
Asset Intelligence Platform: Streamlit web application.

Run with:  streamlit run app.py

The orchestrator is cached per server process (ui/data.py), a question runs only when the
user asks one, and the last answer is kept in session state so reruns don't repeat the work.
"""

from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.set_page_config(
    page_title="Asset Intelligence · AHU-01",
    layout="wide",
    initial_sidebar_state="auto",
)

from ui import (  # noqa: E402  (set_page_config must come first)
    inject_custom_css,
    render_ai_diagnosis,
    render_evidence_section,
    render_header,
    render_kpi_cards,
    render_ask_bar,
    render_presets,
    render_sidebar,
    render_telemetry_chart,
)
from ui.data import METRICS, get_orchestrator, load_telemetry, telemetry_anomalies  # noqa: E402

FACILITY, ASSET = "Bommanahalli Office", "AHU-01"


def run_query(question: str) -> None:
    """Run one question through the pipeline and keep the result in session state."""
    with st.status("Working on it…", expanded=False) as status:
        status.write("Loading services (first run builds the manual index)…")
        orchestrator = get_orchestrator()
        status.write("Classifying the question, querying sources, writing the answer…")
        try:
            response = orchestrator.process_query(question)
        except Exception as e:
            status.update(label="Something went wrong", state="error")
            st.error(f"The query failed: {e}")
            return
        for sc in response.service_calls:
            status.write(f"{'✓' if sc.success else '✗'} {sc.service} · {sc.execution_time_ms:,.0f} ms")
        status.update(label=f"Answered in {response.total_execution_time_ms / 1000:.1f} s", state="complete")
    st.session_state["response"] = response


def main() -> None:
    inject_custom_css()

    try:
        df = load_telemetry()
    except Exception as e:
        st.error(f"Telemetry could not be loaded: {e}")
        render_sidebar()
        st.stop()

    anomaly_count = sum(len(telemetry_anomalies(m)) for m in METRICS)
    render_header(FACILITY, ASSET, anomaly_count)
    render_kpi_cards(df)
    st.write("")

    # A typed question is stored by the ask bar (rendered last) and run on the rerun.
    question = render_presets() or st.session_state.pop("pending", None)
    if question:
        run_query(question)

    response = st.session_state.get("response")
    if response:
        render_ai_diagnosis(response)
        render_evidence_section(response)
    else:
        with st.container(border=True, key="card_chart"):
            st.markdown("<div class='label'>Last 24 hours</div>", unsafe_allow_html=True)
            metric = st.segmented_control(
                "Metric", list(METRICS), default="supply_air_temperature", key="landing_metric",
                format_func=lambda m: METRICS[m]["label"], label_visibility="collapsed",
            ) or "supply_air_temperature"
            render_telemetry_chart(metric, key="landing_chart")

    render_ask_bar()
    # Last, so it reflects anything this run loaded (e.g. the manual index).
    render_sidebar()


main()
