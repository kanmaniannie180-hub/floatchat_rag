import pandas as pd
import plotly.express as px


# -----------------------------
# OVERVIEW MAP (ALL FLOATS)
# -----------------------------
def build_overview_map(profiles: pd.DataFrame):
    """
    Shows all float trajectories.
    Used in Overview page and query assistant.
    """

    if profiles.empty:
        return None

    fig = px.line_geo(
        profiles.sort_values(["float_id", "profile_date"]),
        lat="latitude",
        lon="longitude",
        color="float_id",
        hover_name="float_id",
        hover_data={
            "cycle_number": True,
            "profile_date": True,
            "latitude": ':.3f',
            "longitude": ':.3f'
        },
        title="ARGO Float Trajectories Overview"
    )

    fig.update_traces(
        mode="lines+markers",
        line=dict(width=2)
    )

    fig.update_geos(
        lataxis_range=[-40, 30],
        lonaxis_range=[30, 110],
        showcountries=True,
        showcoastlines=True,
        showland=True
    )

    fig.update_layout(
        showlegend=False,
        height=620,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


# -----------------------------
# SINGLE FLOAT MAP
# -----------------------------
def build_float_map(float_profiles: pd.DataFrame, selected_float: str):
    """
    Shows trajectory for one float.
    """

    if float_profiles.empty:
        return None

    fig = px.line_geo(
        float_profiles.sort_values("profile_date"),
        lat="latitude",
        lon="longitude",
        hover_name="float_id",
        hover_data={
            "cycle_number": True,
            "profile_date": True,
            "latitude": ':.3f',
            "longitude": ':.3f'
        },
        title=f"Trajectory for Float {selected_float}"
    )

    fig.update_traces(
        mode="lines+markers",
        line=dict(width=3)
    )

    fig.update_geos(
        lataxis_range=[-40, 30],
        lonaxis_range=[30, 110],
        showcountries=True,
        showcoastlines=True,
        showland=True
    )

    fig.update_layout(
        showlegend=False,
        height=620,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


# -----------------------------
# MULTI-FLOAT COMPARISON MAP (Phase 3 ready)
# -----------------------------
def build_multi_float_map(profiles: pd.DataFrame, float_ids: list[str]):
    """
    Compare multiple floats on same map.
    (Used later for two-float comparison feature)
    """

    df = profiles[profiles["float_id"].isin([str(fid) for fid in float_ids])]

    if df.empty:
        return None

    fig = px.line_geo(
        df.sort_values(["float_id", "profile_date"]),
        lat="latitude",
        lon="longitude",
        color="float_id",
        hover_name="float_id",
        hover_data={
            "cycle_number": True,
            "profile_date": True
        },
        title=f"Trajectory Comparison: {', '.join(float_ids)}"
    )

    fig.update_traces(
        mode="lines+markers",
        line=dict(width=3)
    )

    fig.update_geos(
        lataxis_range=[-40, 30],
        lonaxis_range=[30, 110],
        showcountries=True,
        showcoastlines=True,
        showland=True
    )

    fig.update_layout(
        height=620,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig