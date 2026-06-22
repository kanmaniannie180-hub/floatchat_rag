import pandas as pd
from typing import Dict, Any, Optional

from core.utils import split_depth_bands, safe_float


def build_insight_box(profile_data: pd.DataFrame, parameter: str) -> str:
    """
    Simple profile interpretation used in explorer + query assistant.
    """
    if profile_data.empty:
        return "No data available for the selected profile."

    profile_data = profile_data.sort_values("pressure").copy()
    surface = profile_data.iloc[0]
    deep = profile_data.iloc[-1]

    if parameter == "temperature":
        s = surface["temperature"]
        d = deep["temperature"]
        delta = s - d

        if pd.isna(s) or pd.isna(d):
            return "Temperature data is incomplete for this profile."

        if delta > 8:
            summary = "A strong thermocline is visible, with rapid cooling from surface to deeper waters."
        elif delta > 3:
            summary = "A moderate temperature gradient is present through the water column."
        elif delta > 0:
            summary = "Temperature decreases gradually with depth."
        else:
            summary = "An unusual temperature inversion or weak gradient is present."

        return (
            f"Surface temperature is about **{s:.2f}°C**, while deep-water temperature is about **{d:.2f}°C**. "
            f"Overall change is **{delta:.2f}°C**. {summary}"
        )

    s = surface["salinity"]
    d = deep["salinity"]
    delta = d - s

    if pd.isna(s) or pd.isna(d):
        return "Salinity data is incomplete for this profile."

    if abs(delta) > 1.0:
        summary = "A strong salinity gradient is observed across the depth profile."
    elif abs(delta) > 0.3:
        summary = "A moderate salinity change is observed with depth."
    else:
        summary = "Salinity remains relatively stable across the profile."

    return (
        f"Surface salinity is about **{s:.2f} PSU**, while deep-water salinity is about **{d:.2f} PSU**. "
        f"Overall change is **{delta:.2f} PSU**. {summary}"
    )


def get_profile_stats(profile_data: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    Core summary stats for one selected profile.
    """
    if profile_data.empty:
        return None

    profile_data = profile_data.sort_values("pressure").copy()
    surface = profile_data.iloc[0]
    deep = profile_data.iloc[-1]

    return {
        "surface_temp": safe_float(surface.get("temperature")),
        "deep_temp": safe_float(deep.get("temperature")),
        "surface_sal": safe_float(surface.get("salinity")),
        "deep_sal": safe_float(deep.get("salinity")),
        "max_pressure": safe_float(profile_data["pressure"].max()),
    }


def detect_thermocline(profile_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Detect strongest temperature gradient and identify whether a thermocline exists.

    Logic:
    - sort by pressure
    - compute dT/dz approximately using diff
    - look for strongest negative temperature gradient
    - emphasize upper 200 m for classic thermocline detection
    """
    result = {
        "detected": False,
        "label": "No clear thermocline",
        "confidence": "Low",
        "max_gradient": None,
        "depth_start": None,
        "depth_end": None,
        "reasoning": "Insufficient evidence for a strong upper-ocean thermocline."
    }

    if profile_data.empty:
        result["reasoning"] = "No profile data available."
        return result

    df = profile_data.sort_values("pressure").copy()
    df = df[["pressure", "temperature"]].dropna()

    if len(df) < 3:
        result["reasoning"] = "Not enough valid temperature points to detect a thermocline."
        return result

    df["dT"] = df["temperature"].diff()
    df["dz"] = df["pressure"].diff()
    df["gradient"] = df["dT"] / df["dz"]

    grad_df = df.dropna(subset=["gradient"]).copy()

    if grad_df.empty:
        result["reasoning"] = "Gradient could not be computed."
        return result

    upper_df = grad_df[grad_df["pressure"] <= 200].copy()
    if upper_df.empty:
        result["reasoning"] = "No valid upper-ocean temperature gradient data available."
        return result

    strongest = upper_df.loc[upper_df["gradient"].idxmin()]

    max_gradient = float(strongest["gradient"])
    depth_end = float(strongest["pressure"])

    prev_rows = df[df["pressure"] < depth_end]
    depth_start = float(prev_rows["pressure"].iloc[-1]) if not prev_rows.empty else depth_end

    result["max_gradient"] = max_gradient
    result["depth_start"] = depth_start
    result["depth_end"] = depth_end

    # Simple thresholds
    if max_gradient <= -0.08:
        result["detected"] = True
        result["label"] = "Strong Thermocline"
        result["confidence"] = "High"
        result["reasoning"] = (
            f"A strong temperature drop is detected between approximately {depth_start:.0f} and {depth_end:.0f} dbar, "
            f"with gradient {max_gradient:.3f} °C/dbar."
        )
    elif max_gradient <= -0.03:
        result["detected"] = True
        result["label"] = "Moderate Thermocline"
        result["confidence"] = "Medium"
        result["reasoning"] = (
            f"A moderate upper-ocean temperature gradient is detected between approximately {depth_start:.0f} and "
            f"{depth_end:.0f} dbar, with gradient {max_gradient:.3f} °C/dbar."
        )
    else:
        result["reasoning"] = (
            f"The strongest upper-ocean gradient is {max_gradient:.3f} °C/dbar, which does not indicate a strong thermocline."
        )

    return result


def get_depth_band_summaries(profile_data: pd.DataFrame) -> Dict[str, Dict[str, Optional[float]]]:
    """
    Compute average temperature/salinity in key depth bands.
    """
    if profile_data.empty:
        return {
            "0-50": {"temperature": None, "salinity": None},
            "50-200": {"temperature": None, "salinity": None},
            "200-1000": {"temperature": None, "salinity": None},
            "1000+": {"temperature": None, "salinity": None},
        }

    df = profile_data.sort_values("pressure").copy()
    bands = split_depth_bands(df)

    output = {}
    for band_name, band_df in bands.items():
        output[band_name] = {
            "temperature": safe_float(band_df["temperature"].mean()) if "temperature" in band_df.columns and not band_df.empty else None,
            "salinity": safe_float(band_df["salinity"].mean()) if "salinity" in band_df.columns and not band_df.empty else None,
        }

    return output


def get_depth_band_interpretation(profile_data: pd.DataFrame) -> str:
    """
    Explain band-level structure in a scientific but demo-friendly way.
    """
    bands = get_depth_band_summaries(profile_data)

    upper_temp = bands["0-50"]["temperature"]
    mid_temp = bands["50-200"]["temperature"]
    deep_temp = bands["200-1000"]["temperature"]

    messages = []

    if upper_temp is not None and mid_temp is not None:
        if upper_temp - mid_temp > 3:
            messages.append("Upper-ocean waters are much warmer than subsurface waters, indicating clear stratification.")
        elif upper_temp - mid_temp > 1:
            messages.append("A moderate upper-ocean temperature contrast is present.")
        else:
            messages.append("Upper-ocean temperature remains relatively uniform into the subsurface.")

    if deep_temp is not None and mid_temp is not None:
        if abs(mid_temp - deep_temp) < 1:
            messages.append("Deeper waters remain comparatively stable.")
        else:
            messages.append("Temperature continues changing below the upper ocean, suggesting deeper vertical structure.")

    upper_sal = bands["0-50"]["salinity"]
    mid_sal = bands["50-200"]["salinity"]
    if upper_sal is not None and mid_sal is not None:
        if abs(upper_sal - mid_sal) > 0.5:
            messages.append("Salinity also varies meaningfully across shallow depth bands.")
        else:
            messages.append("Salinity is relatively consistent across upper depth bands.")

    if not messages:
        return "Depth-band interpretation is limited because the profile has insufficient valid measurements."

    return " ".join(messages)


def detect_anomaly_flags(profile_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Simple rule-based anomaly detection for presentation + explainability.
    """
    flags = []

    if profile_data.empty:
        return {"flags": ["No valid profile data"], "count": 1}

    df = profile_data.sort_values("pressure").copy()
    stats = get_profile_stats(df)

    if stats is None:
        return {"flags": ["No valid profile summary available"], "count": 1}

    surface_temp = stats["surface_temp"]
    deep_temp = stats["deep_temp"]
    surface_sal = stats["surface_sal"]
    deep_sal = stats["deep_sal"]
    max_pressure = stats["max_pressure"]

    if max_pressure is not None and max_pressure < 200:
        flags.append("Shallow profile warning")

    if surface_temp is not None and surface_temp > 30:
        flags.append("Unusually high surface temperature")

    if surface_temp is not None and deep_temp is not None:
        temp_diff = surface_temp - deep_temp
        if temp_diff < 1:
            flags.append("Very weak stratification")
        elif temp_diff > 8:
            flags.append("Strong thermal stratification")

    if surface_sal is not None and deep_sal is not None:
        sal_diff = abs(deep_sal - surface_sal)
        if sal_diff > 1.0:
            flags.append("Sharp salinity jump")

    if not flags:
        flags.append("No major anomaly flags detected")

    return {
        "flags": flags,
        "count": len(flags)
    }


def get_profile_quality_indicator(profile_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Simple quality / readiness indicator for the current profile.
    """
    if profile_data.empty:
        return {
            "valid_levels": 0,
            "missing_temp_pct": None,
            "missing_sal_pct": None,
            "status": "No Data"
        }

    df = profile_data.copy()
    valid_levels = int(len(df))

    missing_temp_pct = float(df["temperature"].isna().mean() * 100) if "temperature" in df.columns else None
    missing_sal_pct = float(df["salinity"].isna().mean() * 100) if "salinity" in df.columns else None

    if valid_levels >= 50 and (missing_temp_pct or 0) < 20 and (missing_sal_pct or 0) < 20:
        status = "High Quality"
    elif valid_levels >= 20:
        status = "Usable"
    else:
        status = "Limited"

    return {
        "valid_levels": valid_levels,
        "missing_temp_pct": round(missing_temp_pct, 2) if missing_temp_pct is not None else None,
        "missing_sal_pct": round(missing_sal_pct, 2) if missing_sal_pct is not None else None,
        "status": status
    }


def generate_ocean_summary(profile_data: pd.DataFrame) -> str:
    """
    Explainable Ocean AI style summary for judges/demo.
    """
    if profile_data.empty:
        return "No ocean summary can be generated because the selected profile has no valid data."

    stats = get_profile_stats(profile_data)
    thermo = detect_thermocline(profile_data)
    anomalies = detect_anomaly_flags(profile_data)
    band_text = get_depth_band_interpretation(profile_data)

    parts = []

    if stats:
        if stats["surface_temp"] is not None and stats["deep_temp"] is not None:
            parts.append(
                f"Surface waters are around {stats['surface_temp']:.2f}°C, while deeper waters are around {stats['deep_temp']:.2f}°C."
            )
        if stats["surface_sal"] is not None and stats["deep_sal"] is not None:
            parts.append(
                f"Surface salinity is {stats['surface_sal']:.2f} PSU and deep-water salinity is {stats['deep_sal']:.2f} PSU."
            )

    if thermo["detected"]:
        parts.append(
            f"{thermo['label']} detected between about {thermo['depth_start']:.0f} and {thermo['depth_end']:.0f} dbar."
        )
    else:
        parts.append("No strong thermocline is detected in the upper ocean.")

    parts.append(band_text)

    major_flags = [f for f in anomalies["flags"] if f != "No major anomaly flags detected"]
    if major_flags:
        parts.append("Key detected flags: " + ", ".join(major_flags) + ".")

    return " ".join(parts)