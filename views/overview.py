import streamlit as st
import pandas as pd

from core.analytics import compute_kpis
from core.region_classifier import get_region_distribution
from components.metrics import render_global_kpis
from components.maps import build_overview_map


def render_overview_page(
    profiles: pd.DataFrame,
    measurements: pd.DataFrame
):
    # -----------------------------
    # TITLE + PROBLEM FRAMING
    # -----------------------------
    st.title("🌊 FloatChat — Ocean Intelligence Dashboard")

    st.markdown(
        """
        **Problem:** Oceanographic data from ARGO floats is complex, fragmented, and difficult to interpret.

        **Solution:** FloatChat transforms raw ocean data into an interactive, explainable, and query-driven system for exploration and analysis.
        """
    )

    st.markdown("---")

    # -----------------------------
    # KPI CARDS
    # -----------------------------
    kpis = compute_kpis(profiles, measurements)
    render_global_kpis(kpis)

    st.markdown("---")

    # -----------------------------
    # TRAJECTORY MAP
    # -----------------------------
    st.subheader("Global Float Trajectories")

    fig = build_overview_map(profiles)

    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No trajectory data available.")

    st.markdown("---")

    # -----------------------------
    # REGION DISTRIBUTION
    # -----------------------------
    st.subheader("Region Distribution")

    region_counts = get_region_distribution(profiles)

    if region_counts:
        df = pd.DataFrame({
            "Region": list(region_counts.keys()),
            "Profiles": list(region_counts.values())
        }).sort_values("Profiles", ascending=False)

        st.bar_chart(df.set_index("Region"))
    else:
        st.info("No region data available.")

    st.markdown("---")

    # -----------------------------
    # SYSTEM CAPABILITIES
    # -----------------------------
    st.subheader("System Capabilities")

    st.markdown(
        """
        - Natural language query assistant for ocean data exploration  
        - Thermocline and gradient detection  
        - Depth-based ocean structure analysis  
        - Multi-cycle and multi-float comparison  
        - Heatmaps and time-series analytics  
        - Explainable ocean insights and summaries  
        """
    )