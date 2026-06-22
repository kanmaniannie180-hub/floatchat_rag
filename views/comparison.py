import streamlit as st
import pandas as pd

from components.comparison_panel import (
    render_cycle_comparison_panel,
    render_first_vs_latest_panel,
    render_two_float_comparison_panel,
)
from core.analytics import compute_first_vs_latest_change


def render_comparison_page(
    profiles: pd.DataFrame,
    measurements: pd.DataFrame,
    selected_float: str,
    selected_cycle: int,
    selected_parameter: str,
    compare_mode: bool,
    comparison_type: str,
    comparison_cycle: int = None,
    second_float: str = None,
):
    st.title("📊 Comparison Dashboard")
    st.caption("Analyze differences across cycles and floats.")

    if not compare_mode:
        st.info("Enable comparison mode from the sidebar to start analysis.")
        return

    st.markdown("---")

    # -----------------------------
    # CYCLE VS CYCLE
    # -----------------------------
    if comparison_type == "Cycle vs Cycle":
        if comparison_cycle is None:
            st.warning("Please select a second cycle for comparison.")
            return

        render_cycle_comparison_panel(
            measurements=measurements,
            selected_float=selected_float,
            cycle_a=selected_cycle,
            cycle_b=comparison_cycle,
            parameter=selected_parameter,
        )

        st.markdown("---")

        render_first_vs_latest_panel(
            measurements=measurements,
            selected_float=selected_float,
            parameter=selected_parameter,
        )

        st.markdown("---")

        delta = compute_first_vs_latest_change(
            measurements=measurements,
            selected_float=selected_float,
            parameter=selected_parameter,
        )

        if delta:
            st.subheader("📈 Time Evolution Insight")

            parts = []

            s = delta.get("surface_change")
            d = delta.get("deep_change")

            if s is not None:
                if s > 0:
                    parts.append("surface values have increased over time")
                elif s < 0:
                    parts.append("surface values have decreased over time")
                else:
                    parts.append("surface values remained stable")

            if d is not None:
                if d > 0:
                    parts.append("deep-water values have increased")
                elif d < 0:
                    parts.append("deep-water values have decreased")
                else:
                    parts.append("deep-water values remained stable")

            if parts:
                st.success(
                    f"For Float {selected_float}, " + " and ".join(parts) + "."
                )

    # -----------------------------
    # FLOAT VS FLOAT
    # -----------------------------
    elif comparison_type == "Float vs Float":
        if second_float is None:
            st.warning("Please select a second float for comparison.")
            return

        render_two_float_comparison_panel(
            measurements=measurements,
            float_a=selected_float,
            float_b=second_float,
            parameter=selected_parameter,
            cycle=None,  # default = latest
        )

        st.markdown("---")

        st.subheader("🌍 Cross-Float Insight")

        st.info(
            "This comparison highlights spatial variability across different floats, "
            "which may reflect regional oceanographic differences or temporal shifts."
        )

    # -----------------------------
    # FALLBACK
    # -----------------------------
    else:
        st.warning("Invalid comparison type selected.")