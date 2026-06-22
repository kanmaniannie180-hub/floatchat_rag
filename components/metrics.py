import streamlit as st
from typing import Dict, Any, Optional


# -----------------------------
# GLOBAL KPI CARDS
# -----------------------------
def render_global_kpis(kpis: Dict[str, Any]) -> None:
    """
    Render app-level KPI cards.
    Expected keys:
    - total_floats
    - total_profiles
    - total_measurements
    - avg_levels
    - max_depth
    """
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Total Floats", kpis.get("total_floats", 0))
    c2.metric("Total Profiles", kpis.get("total_profiles", 0))
    c3.metric("Total Measurements", kpis.get("total_measurements", 0))

    avg_levels = kpis.get("avg_levels")
    c4.metric("Avg Valid Levels", f"{avg_levels:.2f}" if avg_levels is not None else "N/A")

    max_depth = kpis.get("max_depth")
    c5.metric("Max Observed Depth", f"{max_depth:.0f} dbar" if max_depth is not None else "N/A")


# -----------------------------
# SELECTED PROFILE SUMMARY CARDS
# -----------------------------
def render_profile_summary_cards(stats: Optional[Dict[str, Any]]) -> None:
    """
    Render surface/deep profile summary cards.
    Expected keys:
    - surface_temp
    - deep_temp
    - surface_sal
    - deep_sal
    - max_pressure
    """
    st.markdown("### Quick Profile Stats")

    if not stats:
        st.info("No profile summary statistics available.")
        return

    c1, c2, c3, c4, c5 = st.columns(5)

    surface_temp = stats.get("surface_temp")
    deep_temp = stats.get("deep_temp")
    surface_sal = stats.get("surface_sal")
    deep_sal = stats.get("deep_sal")
    max_pressure = stats.get("max_pressure")

    c1.metric("Surface Temp", f"{surface_temp:.2f} °C" if surface_temp is not None else "N/A")
    c2.metric("Deep Temp", f"{deep_temp:.2f} °C" if deep_temp is not None else "N/A")
    c3.metric("Surface Salinity", f"{surface_sal:.2f} PSU" if surface_sal is not None else "N/A")
    c4.metric("Deep Salinity", f"{deep_sal:.2f} PSU" if deep_sal is not None else "N/A")
    c5.metric("Max Depth", f"{max_pressure:.0f} dbar" if max_pressure is not None else "N/A")


# -----------------------------
# PROFILE QUALITY CARDS
# -----------------------------
def render_profile_quality_cards(quality: Dict[str, Any]) -> None:
    """
    Render profile quality / completeness indicators.
    Expected keys:
    - valid_levels
    - missing_temp_pct
    - missing_sal_pct
    - status
    """
    st.markdown("### Profile Quality")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Valid Levels", quality.get("valid_levels", 0))

    missing_temp = quality.get("missing_temp_pct")
    c2.metric(
        "Missing Temp",
        f"{missing_temp:.2f}%" if missing_temp is not None else "N/A"
    )

    missing_sal = quality.get("missing_sal_pct")
    c3.metric(
        "Missing Salinity",
        f"{missing_sal:.2f}%" if missing_sal is not None else "N/A"
    )

    c4.metric("Quality Status", quality.get("status", "Unknown"))


# -----------------------------
# ANOMALY FLAGS
# -----------------------------
def render_anomaly_flags(anomaly_result: Dict[str, Any]) -> None:
    """
    Render anomaly / scientific flag badges.
    Expected keys:
    - flags: list[str]
    - count: int
    """
    st.markdown("### Scientific Flags")

    flags = anomaly_result.get("flags", [])

    if not flags:
        st.info("No anomaly flags available.")
        return

    for flag in flags:
        if flag == "No major anomaly flags detected":
            st.success(flag)
        elif "warning" in flag.lower():
            st.warning(flag)
        else:
            st.info(flag)


# -----------------------------
# THERMOCLINE CARD
# -----------------------------
def render_thermocline_card(thermo: Dict[str, Any]) -> None:
    """
    Render thermocline detection summary.
    Expected keys:
    - detected
    - label
    - confidence
    - max_gradient
    - depth_start
    - depth_end
    - reasoning
    """
    st.markdown("### Thermocline Detection")

    c1, c2, c3 = st.columns(3)

    c1.metric("Detection", "Yes" if thermo.get("detected") else "No")
    c2.metric("Label", thermo.get("label", "Unknown"))
    c3.metric("Confidence", thermo.get("confidence", "Unknown"))

    c4, c5 = st.columns(2)

    max_gradient = thermo.get("max_gradient")
    c4.metric(
        "Max Gradient",
        f"{max_gradient:.3f} °C/dbar" if max_gradient is not None else "N/A"
    )

    if thermo.get("depth_start") is not None and thermo.get("depth_end") is not None:
        c5.metric(
            "Depth Range",
            f"{thermo['depth_start']:.0f}–{thermo['depth_end']:.0f} dbar"
        )
    else:
        c5.metric("Depth Range", "N/A")

    reasoning = thermo.get("reasoning")
    if reasoning:
        if thermo.get("detected"):
            st.success(reasoning)
        else:
            st.info(reasoning)