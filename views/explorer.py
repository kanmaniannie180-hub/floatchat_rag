import streamlit as st
import pandas as pd

from core.insights import (
    get_profile_stats,
    build_insight_box,
    detect_thermocline,
    get_depth_band_summaries,
    get_depth_band_interpretation,
    detect_anomaly_flags,
    get_profile_quality_indicator,
    generate_ocean_summary,
)
from core.region_classifier import classify_float_region
from components.maps import build_float_map
from components.profile_plots import build_profile_plot
from components.metrics import (
    render_profile_summary_cards,
    render_profile_quality_cards,
    render_anomaly_flags,
    render_thermocline_card,
)
from components.insight_cards import (
    render_region_card,
    render_ocean_summary,
    render_depth_band_table,
    render_depth_band_interpretation,
)
from components.downloads import (
    render_profile_download,
    render_metadata_download,
)


def render_explorer_page(
    profiles: pd.DataFrame,
    measurements: pd.DataFrame,
    selected_float: str,
    selected_cycle: int,
    selected_parameter: str,
):
    st.title("🔍 Float Explorer")
    st.caption("Inspect one float in detail with profile-level ocean intelligence.")

    float_profiles = profiles[profiles["float_id"] == str(selected_float)].sort_values("profile_date")
    if float_profiles.empty:
        st.warning("No profiles available for the selected float.")
        return

    selected_profile_rows = float_profiles[float_profiles["cycle_number"] == selected_cycle]
    if selected_profile_rows.empty:
        st.warning("No metadata found for the selected cycle.")
        return

    selected_profile = selected_profile_rows.iloc[0]

    profile_data = measurements[
        (measurements["float_id"] == str(selected_float)) &
        (measurements["cycle_number"] == selected_cycle)
    ].sort_values("pressure")

    if profile_data.empty:
        st.warning("No measurement data available for the selected float and cycle.")
        return

    region = classify_float_region(float_profiles)
    profile_stats = get_profile_stats(profile_data)
    thermocline = detect_thermocline(profile_data)
    depth_bands = get_depth_band_summaries(profile_data)
    depth_band_text = get_depth_band_interpretation(profile_data)
    anomaly_flags = detect_anomaly_flags(profile_data)
    quality = get_profile_quality_indicator(profile_data)
    ocean_summary = generate_ocean_summary(profile_data)
    quick_insight = build_insight_box(profile_data, selected_parameter)

    st.markdown("---")

    col1, col2 = st.columns([1.7, 1])

    with col1:
        st.subheader("Trajectory")
        fig_map = build_float_map(float_profiles, str(selected_float))
        if fig_map is not None:
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No trajectory map available.")

    with col2:
        st.subheader("Selected Profile Metadata")
        st.metric("Float ID", str(selected_float))
        st.metric("Cycle Number", int(selected_cycle))
        st.metric(
            "Latitude",
            f"{selected_profile['latitude']:.3f}" if pd.notna(selected_profile.get("latitude")) else "N/A"
        )
        st.metric(
            "Longitude",
            f"{selected_profile['longitude']:.3f}" if pd.notna(selected_profile.get("longitude")) else "N/A"
        )
        st.metric(
            "Levels",
            int(selected_profile["n_levels_clean"]) if pd.notna(selected_profile.get("n_levels_clean")) else 0
        )
        st.metric(
            "Date",
            str(selected_profile["profile_date"].date()) if pd.notna(selected_profile.get("profile_date")) else "N/A"
        )

    st.markdown("---")

    st.subheader("Profile Plot")
    fig_profile = build_profile_plot(
        profile_data=profile_data,
        parameter=selected_parameter,
        selected_float=str(selected_float),
        selected_cycle=int(selected_cycle),
    )
    if fig_profile is not None:
        st.plotly_chart(fig_profile, use_container_width=True)
    else:
        st.info("No profile plot available.")

    st.markdown("### Quick Insight")
    st.info(quick_insight)

    st.markdown("---")

    render_profile_summary_cards(profile_stats)

    st.markdown("---")

    left, right = st.columns(2)

    with left:
        render_profile_quality_cards(quality)
        st.markdown("---")
        render_anomaly_flags(anomaly_flags)

    with right:
        render_thermocline_card(thermocline)
        st.markdown("---")
        render_region_card(region)

    st.markdown("---")

    render_ocean_summary(ocean_summary)
    st.markdown("---")
    render_depth_band_table(depth_bands)
    st.markdown("---")
    render_depth_band_interpretation(depth_band_text)

    st.markdown("---")

    d1, d2 = st.columns(2)
    with d1:
        render_profile_download(profile_data, str(selected_float), int(selected_cycle))
    with d2:
        render_metadata_download(selected_profile, str(selected_float), int(selected_cycle))

    st.markdown("---")

    with st.expander("Show Raw Profile Data"):
        st.dataframe(profile_data.reset_index(drop=True), use_container_width=True)