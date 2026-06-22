import pandas as pd
from typing import Dict, Any, Optional, Tuple

from core.utils import (
    get_latest_cycle,
    get_first_vs_latest_cycles,
    safe_float,
)


def prepare_heatmap_data(
    measurements: pd.DataFrame,
    selected_float: str,
    parameter: str
) -> pd.DataFrame:
    """
    Prepare long-form data for heatmap:
    cycle_number, pressure, parameter
    """
    df = measurements[measurements["float_id"] == str(selected_float)].copy()

    if df.empty:
        return df

    df = df.sort_values(["cycle_number", "pressure"])
    return df[["cycle_number", "pressure", parameter]].dropna()


def prepare_time_series(
    measurements: pd.DataFrame,
    selected_float: str,
    parameter: str
) -> pd.DataFrame:
    """
    Surface + deep value per cycle.
    """
    df = measurements[measurements["float_id"] == str(selected_float)].copy()

    if df.empty:
        return df

    df = df.sort_values(["cycle_number", "pressure"])

    surface = df.groupby("cycle_number").first().reset_index()
    deep = df.groupby("cycle_number").last().reset_index()

    result = pd.DataFrame({
        "cycle_number": surface["cycle_number"],
        "surface_value": surface[parameter],
        "deep_value": deep[parameter],
    })

    return result


def prepare_depth_series(
    measurements: pd.DataFrame,
    selected_float: str
) -> pd.DataFrame:
    """
    Max pressure per cycle.
    """
    df = measurements[measurements["float_id"] == str(selected_float)].copy()

    if df.empty:
        return df

    depth = df.groupby("cycle_number")["pressure"].max().reset_index()
    depth.rename(columns={"pressure": "max_depth"}, inplace=True)
    return depth


def compute_first_vs_latest_change(
    measurements: pd.DataFrame,
    selected_float: str,
    parameter: str
) -> Optional[Dict[str, Any]]:
    """
    Compute surface/deep change from earliest to latest cycle.
    """
    df = measurements[measurements["float_id"] == str(selected_float)].copy()

    if df.empty:
        return None

    first_cycle, latest_cycle = get_first_vs_latest_cycles(df)

    if first_cycle is None or latest_cycle is None:
        return None

    first_df = df[df["cycle_number"] == first_cycle].sort_values("pressure")
    latest_df = df[df["cycle_number"] == latest_cycle].sort_values("pressure")

    if first_df.empty or latest_df.empty:
        return None

    surface_first = first_df.iloc[0][parameter]
    surface_latest = latest_df.iloc[0][parameter]

    deep_first = first_df.iloc[-1][parameter]
    deep_latest = latest_df.iloc[-1][parameter]

    return {
        "first_cycle": int(first_cycle),
        "latest_cycle": int(latest_cycle),
        "surface_change": safe_float(surface_latest - surface_first),
        "deep_change": safe_float(deep_latest - deep_first),
    }


def prepare_two_float_comparison(
    measurements: pd.DataFrame,
    float_a: str,
    float_b: str,
    parameter: str,
    cycle: Optional[int] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract comparable data for two floats.
    If cycle is None, use each float's latest cycle.
    """
    df_a = measurements[measurements["float_id"] == str(float_a)].copy()
    df_b = measurements[measurements["float_id"] == str(float_b)].copy()

    if cycle is not None:
        df_a = df_a[df_a["cycle_number"] == cycle]
        df_b = df_b[df_b["cycle_number"] == cycle]
    else:
        cycle_a = get_latest_cycle(df_a)
        cycle_b = get_latest_cycle(df_b)

        if cycle_a is not None:
            df_a = df_a[df_a["cycle_number"] == cycle_a]
        if cycle_b is not None:
            df_b = df_b[df_b["cycle_number"] == cycle_b]

    df_a = df_a.sort_values("pressure")
    df_b = df_b.sort_values("pressure")

    return df_a, df_b


def compute_kpis(
    profiles: pd.DataFrame,
    measurements: pd.DataFrame
) -> Dict[str, Any]:
    """
    Global dashboard KPIs.
    """
    total_floats = profiles["float_id"].nunique()
    total_profiles = len(profiles)
    total_measurements = len(measurements)

    avg_levels = (
        profiles["n_levels_clean"].mean()
        if "n_levels_clean" in profiles.columns else None
    )

    max_depth = (
        measurements["pressure"].max()
        if "pressure" in measurements.columns else None
    )

    return {
        "total_floats": int(total_floats),
        "total_profiles": int(total_profiles),
        "total_measurements": int(total_measurements),
        "avg_levels": round(avg_levels, 2) if pd.notna(avg_levels) else None,
        "max_depth": safe_float(max_depth),
    }