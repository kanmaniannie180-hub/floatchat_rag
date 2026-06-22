import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional

from core.analytics import prepare_two_float_comparison, compute_first_vs_latest_change
from core.insights import build_insight_box, get_profile_stats
from components.profile_plots import build_comparison_plot, build_first_vs_latest


def build_two_float_profile_plot(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    float_a: str,
    float_b: str,
    parameter: str,
    cycle_label_a: Optional[int] = None,
    cycle_label_b: Optional[int] = None,
):
    """
    Build a side-by-side float comparison plot for the same parameter.
    """
    if df_a.empty or df_b.empty:
        return None

    label = "Temperature (°C)" if parameter == "temperature" else "Salinity (PSU)"

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_a[parameter],
            y=df_a["pressure"],
            mode="lines+markers",
            name=f"Float {float_a}" + (f" (Cycle {cycle_label_a})" if cycle_label_a is not None else "")
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_b[parameter],
            y=df_b["pressure"],
            mode="lines+markers",
            name=f"Float {float_b}" + (f" (Cycle {cycle_label_b})" if cycle_label_b is not None else "")
        )
    )

    fig.update_layout(
        title=f"{label} Comparison — Float {float_a} vs Float {float_b}",
        xaxis_title=label,
        yaxis_title="Pressure (dbar)",
        height=560,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    fig.update_yaxes(autorange="reversed")

    return fig


def render_cycle_comparison_panel(
    measurements: pd.DataFrame,
    selected_float: str,
    cycle_a: int,
    cycle_b: int,
    parameter: str,
):
    """
    Render same-float cycle vs cycle comparison.
    """
    st.markdown("### 📊 Cycle Comparison")

    fig = build_comparison_plot(
        measurements=measurements,
        selected_float=selected_float,
        cycle_a=cycle_a,
        cycle_b=cycle_b,
        parameter=parameter,
    )

    if fig is None:
        st.warning("Comparison data not available for the selected cycles.")
        return

    st.plotly_chart(fig, use_container_width=True)

    df_a = measurements[
        (measurements["float_id"] == str(selected_float)) &
        (measurements["cycle_number"] == cycle_a)
    ].sort_values("pressure")

    df_b = measurements[
        (measurements["float_id"] == str(selected_float)) &
        (measurements["cycle_number"] == cycle_b)
    ].sort_values("pressure")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### Cycle {cycle_a} Insight")
        st.info(build_insight_box(df_a, parameter))

    with col2:
        st.markdown(f"#### Cycle {cycle_b} Insight")
        st.info(build_insight_box(df_b, parameter))


def render_first_vs_latest_panel(
    measurements: pd.DataFrame,
    selected_float: str,
    parameter: str,
):
    """
    Render earliest vs latest cycle comparison for one float.
    """
    st.markdown("### 🔁 First vs Latest Comparison")

    fig = build_first_vs_latest(
        measurements=measurements,
        selected_float=selected_float,
        parameter=parameter,
    )

    if fig is None:
        st.warning("Not enough cycles are available for first-vs-latest comparison.")
        return

    st.plotly_chart(fig, use_container_width=True)

    delta = compute_first_vs_latest_change(
        measurements=measurements,
        selected_float=selected_float,
        parameter=parameter,
    )

    if not delta:
        st.info("Could not compute first-vs-latest changes.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("First Cycle", delta["first_cycle"])
    col2.metric("Latest Cycle", delta["latest_cycle"])

    surface_change = delta.get("surface_change")
    deep_change = delta.get("deep_change")

    col3.metric(
        "Surface Change",
        f"{surface_change:.2f}" if surface_change is not None else "N/A"
    )
    col4.metric(
        "Deep Change",
        f"{deep_change:.2f}" if deep_change is not None else "N/A"
    )

    direction_text = []
    if surface_change is not None:
        if surface_change > 0:
            direction_text.append(f"surface {parameter} increased")
        elif surface_change < 0:
            direction_text.append(f"surface {parameter} decreased")
        else:
            direction_text.append(f"surface {parameter} remained stable")

    if deep_change is not None:
        if deep_change > 0:
            direction_text.append(f"deep-water {parameter} increased")
        elif deep_change < 0:
            direction_text.append(f"deep-water {parameter} decreased")
        else:
            direction_text.append(f"deep-water {parameter} remained stable")

    if direction_text:
        st.success(
            f"Across the available record for Float {selected_float}, "
            + " and ".join(direction_text) + "."
        )


def render_two_float_comparison_panel(
    measurements: pd.DataFrame,
    float_a: str,
    float_b: str,
    parameter: str,
    cycle: Optional[int] = None,
):
    """
    Render comparison between two floats using same cycle if provided,
    else latest available cycle for each float.
    """
    st.markdown("### 🌐 Two-Float Comparison")

    df_a, df_b = prepare_two_float_comparison(
        measurements=measurements,
        float_a=float_a,
        float_b=float_b,
        parameter=parameter,
        cycle=cycle,
    )

    if df_a.empty or df_b.empty:
        st.warning("Insufficient data available for two-float comparison.")
        return

    cycle_label_a = None
    cycle_label_b = None

    if not df_a.empty and "cycle_number" in df_a.columns:
        cycle_label_a = int(df_a["cycle_number"].dropna().iloc[0]) if not df_a["cycle_number"].dropna().empty else None

    if not df_b.empty and "cycle_number" in df_b.columns:
        cycle_label_b = int(df_b["cycle_number"].dropna().iloc[0]) if not df_b["cycle_number"].dropna().empty else None

    fig = build_two_float_profile_plot(
        df_a=df_a,
        df_b=df_b,
        float_a=float_a,
        float_b=float_b,
        parameter=parameter,
        cycle_label_a=cycle_label_a,
        cycle_label_b=cycle_label_b,
    )

    if fig is None:
        st.warning("Could not generate two-float comparison plot.")
        return

    st.plotly_chart(fig, use_container_width=True)

    stats_a = get_profile_stats(df_a)
    stats_b = get_profile_stats(df_b)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"#### Float {float_a} Summary")
        st.info(build_insight_box(df_a, parameter))
        if stats_a:
            st.metric("Max Depth", f"{stats_a['max_pressure']:.0f} dbar" if stats_a["max_pressure"] is not None else "N/A")

    with c2:
        st.markdown(f"#### Float {float_b} Summary")
        st.info(build_insight_box(df_b, parameter))
        if stats_b:
            st.metric("Max Depth", f"{stats_b['max_pressure']:.0f} dbar" if stats_b["max_pressure"] is not None else "N/A")

    summary_parts = []

    if stats_a and stats_b:
        if parameter == "temperature":
            a_surface = stats_a.get("surface_temp")
            b_surface = stats_b.get("surface_temp")
        else:
            a_surface = stats_a.get("surface_sal")
            b_surface = stats_b.get("surface_sal")

        if a_surface is not None and b_surface is not None:
            diff = a_surface - b_surface
            if abs(diff) < 0.2:
                summary_parts.append("Both floats show very similar surface conditions.")
            elif diff > 0:
                summary_parts.append(f"Float {float_a} has higher surface {parameter} than Float {float_b}.")
            else:
                summary_parts.append(f"Float {float_b} has higher surface {parameter} than Float {float_a}.")

    if cycle is not None:
        summary_parts.append(f"Comparison was made at Cycle {cycle}.")
    else:
        summary_parts.append("Comparison was made using the latest available cycle for each float.")

    st.markdown("#### Comparison Summary")
    st.success(" ".join(summary_parts))