import streamlit as st
from typing import Dict, Any

from core.region_classifier import get_region_description


# -----------------------------
# REGION CARD
# -----------------------------
def render_region_card(region: str):
    """
    Display region classification with explanation.
    """

    st.markdown("### 🌍 Region Classification")

    if not region or region == "Unknown":
        st.warning("Region could not be determined.")
        return

    st.metric("Detected Region", region)

    description = get_region_description(region)

    if description:
        st.caption(description)


# -----------------------------
# OCEAN SUMMARY (🔥 KEY FEATURE)
# -----------------------------
def render_ocean_summary(summary_text: str):
    """
    Explainable Ocean AI summary.
    """

    st.markdown("### 🧠 Ocean Summary")

    if not summary_text:
        st.info("No summary available.")
        return

    st.success(summary_text)


# -----------------------------
# DEPTH BAND TABLE
# -----------------------------
def render_depth_band_table(bands: Dict[str, Dict[str, Any]]):
    """
    Show depth band averages in a table.
    """

    st.markdown("### 🌊 Depth Band Summary")

    if not bands:
        st.info("No depth band data available.")
        return

    table_data = []

    for band, values in bands.items():
        table_data.append({
            "Depth Band": band,
            "Temperature (°C)": (
                f"{values['temperature']:.2f}"
                if values.get("temperature") is not None else "N/A"
            ),
            "Salinity (PSU)": (
                f"{values['salinity']:.2f}"
                if values.get("salinity") is not None else "N/A"
            )
        })

    st.dataframe(table_data, use_container_width=True)


# -----------------------------
# DEPTH BAND INTERPRETATION
# -----------------------------
def render_depth_band_interpretation(text: str):
    """
    Show scientific explanation of depth bands.
    """

    st.markdown("### 📊 Depth Band Interpretation")

    if not text:
        st.info("No interpretation available.")
        return

    st.info(text)


# -----------------------------
# COMBINED INSIGHT PANEL (optional helper)
# -----------------------------
def render_full_insight_panel(
    region: str,
    ocean_summary: str,
    depth_bands: Dict[str, Dict[str, Any]],
    band_text: str
):
    """
    Render everything together (use in explorer page).
    """

    render_region_card(region)
    render_ocean_summary(ocean_summary)
    render_depth_band_table(depth_bands)
    render_depth_band_interpretation(band_text)