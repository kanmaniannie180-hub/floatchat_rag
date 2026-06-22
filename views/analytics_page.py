import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.analytics import (
    prepare_heatmap_data,
    prepare_time_series,
    prepare_depth_series,
    compute_first_vs_latest_change,
)
from components.profile_plots import build_heatmap, build_time_series


def build_depth_time_series(depth_df: pd.DataFrame, selected_float: str):
    """
    Plot max depth over cycles.
    """
    if depth_df.empty:
        return None

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=depth_df["cycle_number"],
            y=depth_df["max_depth"],
            mode="lines+markers",
            name="Max Depth"
        )
    )

    fig.update_layout(
        title=f"Max Depth Over Time — Float {selected_float}",
        xaxis_title="Cycle Number",
        yaxis_title="Max Depth (dbar)",
        height=500,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


def render_analytics_page(
    profiles: pd.DataFrame,
    measurements: pd.DataFrame,
    selected_float: str,
    selected_parameter: str,
):
    st.title("📈 Analytics")
    st.caption("Explore time evolution, heatmaps, and deeper analytical summaries.")

    float_profiles = profiles[profiles["float_id"] == str(selected_float)]
    if float_profiles.empty:
        st.warning("No profiles available for the selected float.")
        return

    st.markdown("---")

    # HEATMAP
    st.subheader("🔥 Heatmap Across Cycles")

    heatmap_df = prepare_heatmap_data(
        measurements=measurements,
        selected_float=selected_float,
        parameter=selected_parameter,
    )

    heatmap_fig = build_heatmap(
        measurements=measurements,
        selected_float=selected_float,
        parameter=selected_parameter,
    )

    if heatmap_fig is not None and not heatmap_df.empty:
        st.plotly_chart(heatmap_fig, use_container_width=True)
        st.info(
            f"This heatmap shows how {selected_parameter} changes across cycle number and depth."
        )
    else:
        st.info("No valid heatmap data available.")

    st.markdown("---")

    # TIME SERIES
    st.subheader("⏱️ Surface vs Deep Time Series")

    ts_df = prepare_time_series(
        measurements=measurements,
        selected_float=selected_float,
        parameter=selected_parameter,
    )

    ts_fig = build_time_series(
        measurements=measurements,
        selected_float=selected_float,
        parameter=selected_parameter,
    )

    if ts_fig is not None and not ts_df.empty:
        st.plotly_chart(ts_fig, use_container_width=True)
        st.success(
            f"This chart compares surface and deep-water {selected_parameter} over time for Float {selected_float}."
        )
    else:
        st.info("No time-series data available.")

    st.markdown("---")

    # MAX DEPTH OVER TIME
    st.subheader("🌊 Max Depth Over Time")

    depth_df = prepare_depth_series(
        measurements=measurements,
        selected_float=selected_float,
    )

    depth_fig = build_depth_time_series(depth_df, selected_float)

    if depth_fig is not None and not depth_df.empty:
        st.plotly_chart(depth_fig, use_container_width=True)
        st.info(
            "This chart shows how the maximum sampled depth varies across cycles."
        )
    else:
        st.info("No max-depth trend data available.")

    st.markdown("---")

    # FIRST VS LATEST CHANGE
    st.subheader("🔁 First vs Latest Change Summary")

    delta = compute_first_vs_latest_change(
        measurements=measurements,
        selected_float=selected_float,
        parameter=selected_parameter,
    )

    if delta:
        c1, c2, c3, c4 = st.columns(4)

        c1.metric("First Cycle", delta["first_cycle"])
        c2.metric("Latest Cycle", delta["latest_cycle"])

        surface_change = delta.get("surface_change")
        deep_change = delta.get("deep_change")

        c3.metric(
            "Surface Change",
            f"{surface_change:.2f}" if surface_change is not None else "N/A"
        )
        c4.metric(
            "Deep Change",
            f"{deep_change:.2f}" if deep_change is not None else "N/A"
        )

        narrative = []

        if surface_change is not None:
            if surface_change > 0:
                narrative.append(f"surface {selected_parameter} has increased")
            elif surface_change < 0:
                narrative.append(f"surface {selected_parameter} has decreased")
            else:
                narrative.append(f"surface {selected_parameter} stayed stable")

        if deep_change is not None:
            if deep_change > 0:
                narrative.append(f"deep-water {selected_parameter} has increased")
            elif deep_change < 0:
                narrative.append(f"deep-water {selected_parameter} has decreased")
            else:
                narrative.append(f"deep-water {selected_parameter} stayed stable")

        if narrative:
            st.success(
                f"Across the available record for Float {selected_float}, " + " and ".join(narrative) + "."
            )
    else:
        st.info("Not enough data to compute first-vs-latest change.")