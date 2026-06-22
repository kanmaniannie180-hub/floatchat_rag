import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# -----------------------------
# SINGLE PROFILE PLOT
# -----------------------------
def build_profile_plot(
    profile_data: pd.DataFrame,
    parameter: str,
    selected_float: str,
    selected_cycle: int
):
    """
    Temperature / Salinity vs Pressure
    """

    if profile_data.empty:
        return None

    label = "Temperature (°C)" if parameter == "temperature" else "Salinity (PSU)"

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=profile_data[parameter],
            y=profile_data["pressure"],
            mode="lines+markers",
            name=label
        )
    )

    fig.update_layout(
        title=f"{label} vs Pressure — Float {selected_float}, Cycle {selected_cycle}",
        xaxis_title=label,
        yaxis_title="Pressure (dbar)",
        height=560,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    # Reverse depth axis (important for ocean plots)
    fig.update_yaxes(autorange="reversed")

    return fig


# -----------------------------
# CYCLE COMPARISON PLOT
# -----------------------------
def build_comparison_plot(
    measurements: pd.DataFrame,
    selected_float: str,
    cycle_a: int,
    cycle_b: int,
    parameter: str
):
    """
    Compare two cycles (same float)
    """

    label = "Temperature (°C)" if parameter == "temperature" else "Salinity (PSU)"

    data_a = measurements[
        (measurements["float_id"] == str(selected_float)) &
        (measurements["cycle_number"] == cycle_a)
    ].sort_values("pressure")

    data_b = measurements[
        (measurements["float_id"] == str(selected_float)) &
        (measurements["cycle_number"] == cycle_b)
    ].sort_values("pressure")

    if data_a.empty or data_b.empty:
        return None

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data_a[parameter],
        y=data_a["pressure"],
        mode="lines+markers",
        name=f"Cycle {cycle_a}"
    ))

    fig.add_trace(go.Scatter(
        x=data_b[parameter],
        y=data_b["pressure"],
        mode="lines+markers",
        name=f"Cycle {cycle_b}"
    ))

    fig.update_layout(
        title=f"{label} Comparison — Float {selected_float}",
        xaxis_title=label,
        yaxis_title="Pressure (dbar)",
        height=560,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    fig.update_yaxes(autorange="reversed")

    return fig


# -----------------------------
# HEATMAP ACROSS CYCLES (🔥 KEY FEATURE)
# -----------------------------
def build_heatmap(
    measurements: pd.DataFrame,
    selected_float: str,
    parameter: str
):
    """
    X = cycle
    Y = pressure
    Color = temperature/salinity
    """

    df = measurements[measurements["float_id"] == str(selected_float)].copy()

    if df.empty:
        return None

    df = df.sort_values(["cycle_number", "pressure"])

    fig = px.density_heatmap(
        df,
        x="cycle_number",
        y="pressure",
        z=parameter,
        histfunc="avg",
        color_continuous_scale="Viridis"
    )

    fig.update_layout(
        title=f"{parameter.title()} Heatmap Across Cycles — Float {selected_float}",
        xaxis_title="Cycle Number",
        yaxis_title="Pressure (dbar)",
        height=600,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    fig.update_yaxes(autorange="reversed")

    return fig


# -----------------------------
# TIME SERIES (SURFACE / DEEP)
# -----------------------------
def build_time_series(
    measurements: pd.DataFrame,
    selected_float: str,
    parameter: str
):
    """
    Surface and deep trends over cycles
    """

    df = measurements[measurements["float_id"] == str(selected_float)].copy()

    if df.empty:
        return None

    df = df.sort_values(["cycle_number", "pressure"])

    # Surface = shallowest point
    surface = df.groupby("cycle_number").first().reset_index()

    # Deep = deepest point
    deep = df.groupby("cycle_number").last().reset_index()

    label = "Temperature (°C)" if parameter == "temperature" else "Salinity (PSU)"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=surface["cycle_number"],
        y=surface[parameter],
        mode="lines+markers",
        name="Surface"
    ))

    fig.add_trace(go.Scatter(
        x=deep["cycle_number"],
        y=deep[parameter],
        mode="lines+markers",
        name="Deep"
    ))

    fig.update_layout(
        title=f"{label} Over Time — Float {selected_float}",
        xaxis_title="Cycle Number",
        yaxis_title=label,
        height=500,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


# -----------------------------
# FIRST VS LATEST COMPARISON (🔥 STORY FEATURE)
# -----------------------------
def build_first_vs_latest(
    measurements: pd.DataFrame,
    selected_float: str,
    parameter: str
):
    """
    Compare earliest vs latest cycle
    """

    df = measurements[measurements["float_id"] == str(selected_float)].copy()

    if df.empty:
        return None

    cycles = sorted(df["cycle_number"].dropna().unique())

    if len(cycles) < 2:
        return None

    first = int(cycles[0])
    latest = int(cycles[-1])

    return build_comparison_plot(
        measurements,
        selected_float,
        first,
        latest,
        parameter
    )