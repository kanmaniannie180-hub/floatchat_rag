import streamlit as st
import pandas as pd
from typing import Dict, Any

from core.utils import get_available_cycles


def render_sidebar(
    profiles: pd.DataFrame,
    measurements: pd.DataFrame
) -> Dict[str, Any]:
    st.sidebar.header("Controls")

    float_ids = sorted(profiles["float_id"].astype(str).unique().tolist())

    selected_float = st.sidebar.selectbox(
        "Select Float ID",
        float_ids
    )

    float_profiles = profiles[profiles["float_id"] == str(selected_float)].copy()

    cycle_options = get_available_cycles(float_profiles)

    selected_cycle = st.sidebar.selectbox(
        "Select Cycle Number",
        cycle_options if cycle_options else [None]
    )

    selected_parameter = st.sidebar.selectbox(
        "Select Parameter",
        ["temperature", "salinity"]
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Comparison Mode")

    compare_mode = st.sidebar.checkbox("Enable Comparison")

    comparison_type = None
    comparison_cycle = None
    second_float = None

    if compare_mode:
        comparison_type = st.sidebar.radio(
            "Comparison Type",
            ["Cycle vs Cycle", "Float vs Float"]
        )

        if comparison_type == "Cycle vs Cycle":
            other_cycles = [c for c in cycle_options if c != selected_cycle]

            if other_cycles:
                comparison_cycle = st.sidebar.selectbox(
                    "Select Second Cycle",
                    other_cycles
                )
            else:
                st.sidebar.warning("Not enough cycles for comparison.")

        elif comparison_type == "Float vs Float":
            other_floats = [f for f in float_ids if f != selected_float]

            if other_floats:
                second_float = st.sidebar.selectbox(
                    "Select Second Float",
                    other_floats
                )
            else:
                st.sidebar.warning("No other floats available.")

    return {
        "selected_float": selected_float,
        "selected_cycle": selected_cycle,
        "selected_parameter": selected_parameter,
        "compare_mode": compare_mode,
        "comparison_type": comparison_type,
        "comparison_cycle": comparison_cycle,
        "second_float": second_float,
    }