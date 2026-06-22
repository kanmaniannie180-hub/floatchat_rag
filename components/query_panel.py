import streamlit as st
import pandas as pd

from core.query_engine import parse_query, build_system_response, get_query_explanation
from components.maps import build_overview_map, build_float_map
from components.profile_plots import (
    build_profile_plot,
    build_comparison_plot,
    build_first_vs_latest
)
from core.insights import build_insight_box


# -----------------------------
# QUERY INPUT + PROMPTS
# -----------------------------
def render_query_input(selected_float: str):
    st.markdown("### 💬 Ask FloatChat")

    if "assistant_query" not in st.session_state:
        st.session_state.assistant_query = ""

    query = st.text_input(
        "Query input",
        value=st.session_state.assistant_query,
        placeholder="Try: show latest profile for float 2900257"
    )

    st.markdown("#### Guided Sample Prompts")

    c1, c2, c3, c4, c5 = st.columns(5)

    if c1.button("All trajectories", use_container_width=True):
        st.session_state.assistant_query = "show all trajectories"

    if c2.button(f"Float {selected_float}", use_container_width=True):
        st.session_state.assistant_query = f"show float {selected_float}"

    if c3.button("Compare cycles", use_container_width=True):
        st.session_state.assistant_query = "compare cycle 1 and 5"

    if c4.button("Latest profile", use_container_width=True):
        st.session_state.assistant_query = f"show latest profile for float {selected_float}"

    if c5.button("Salinity cycle", use_container_width=True):
        st.session_state.assistant_query = "show salinity for cycle 3"

    return st.session_state.assistant_query if st.session_state.assistant_query else query


# -----------------------------
# QUERY EXPLANATION UI
# -----------------------------
def render_query_explanation(parsed: dict):
    explanation = get_query_explanation(parsed)

    st.markdown("#### 🧠 Query Explanation")

    col1, col2, col3 = st.columns(3)

    col1.metric("Intent", explanation["intent"].replace("_", " ").title())
    col2.metric("Float", explanation["float"] if explanation["float"] else "Not detected")
    col3.metric("Parameter", explanation["parameter"] if explanation["parameter"] else "Not detected")

    col4, col5 = st.columns(2)

    if explanation["compare_cycles"]:
        col4.metric("Cycles", f"{explanation['compare_cycles'][0]} vs {explanation['compare_cycles'][1]}")
    else:
        col4.metric("Cycle", explanation["cycle"] if explanation["cycle"] else "Not detected")

    col5.metric("Confidence", f"{explanation['confidence']}%")

    # Confidence label
    if explanation["confidence"] >= 90:
        st.success("High confidence: query clearly understood.")
    elif explanation["confidence"] >= 70:
        st.info("Medium confidence: partial inference used.")
    else:
        st.warning("Low confidence: query may be ambiguous.")

    # Reasoning
    if explanation["reasoning"]:
        st.markdown("**Reasoning:**")
        for r in explanation["reasoning"]:
            st.write(f"- {r}")


# -----------------------------
# OUTPUT RENDERING
# -----------------------------
def render_query_output(
    parsed,
    profiles: pd.DataFrame,
    measurements: pd.DataFrame,
    selected_float: str,
    selected_parameter: str
):
    st.markdown("### 🤖 Assistant Output")

    render_query_explanation(parsed)

    st.markdown("#### System Response")
    st.info(build_system_response(parsed))

    st.markdown("#### Output")

    target_float = parsed["float_id"] or selected_float
    target_param = parsed["parameter"] or selected_parameter

    # -----------------------------
    # ALL TRAJECTORIES
    # -----------------------------
    if parsed["intent"] == "all_trajectories":
        fig = build_overview_map(profiles)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        return

    # -----------------------------
    # FLOAT TRAJECTORY
    # -----------------------------
    if parsed["intent"] == "float_trajectory":
        df = profiles[profiles["float_id"] == str(target_float)]
        fig = build_float_map(df, str(target_float))
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No trajectory data found.")
        return

    # -----------------------------
    # LATEST PROFILE
    # -----------------------------
    if parsed["intent"] == "latest_profile":
        cycle = parsed["cycle"]

        df = measurements[
            (measurements["float_id"] == str(target_float)) &
            (measurements["cycle_number"] == cycle)
        ].sort_values("pressure")

        if df.empty:
            st.warning("No latest profile data found.")
            return

        st.plotly_chart(
            build_profile_plot(df, target_param, str(target_float), cycle),
            use_container_width=True
        )

        st.success(build_insight_box(df, target_param))
        return

    # -----------------------------
    # COMPARE CYCLES
    # -----------------------------
    if parsed["intent"] == "compare_cycles":
        c1, c2 = parsed["compare_cycles"]

        fig = build_comparison_plot(
            measurements,
            str(target_float),
            c1,
            c2,
            target_param
        )

        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Comparison data not available.")

        return

    # -----------------------------
    # METRIC FOR CYCLE
    # -----------------------------
    if parsed["intent"] == "metric_for_cycle":
        cycle = parsed["cycle"]

        df = measurements[
            (measurements["float_id"] == str(target_float)) &
            (measurements["cycle_number"] == cycle)
        ].sort_values("pressure")

        if df.empty:
            st.warning("No data found for that cycle.")
            return

        st.plotly_chart(
            build_profile_plot(df, target_param, str(target_float), cycle),
            use_container_width=True
        )

        st.success(build_insight_box(df, target_param))
        return

    # -----------------------------
    # FALLBACK
    # -----------------------------
    st.warning("Try one of the sample prompts.")