from typing import Dict, Optional
import pandas as pd


# -----------------------------
# REGION BOUNDARIES (simple rule-based)
# -----------------------------
def classify_region(latitude: float, longitude: float) -> str:
    """
    Classify a single point into ocean region.

    Bounds are approximate but effective for demo + interpretability.
    """

    if latitude is None or longitude is None:
        return "Unknown"

    # Arabian Sea
    if (5 <= latitude <= 25) and (50 <= longitude <= 75):
        return "Arabian Sea"

    # Bay of Bengal
    if (5 <= latitude <= 25) and (80 <= longitude <= 100):
        return "Bay of Bengal"

    # Equatorial Indian Ocean
    if (-5 <= latitude <= 5) and (40 <= longitude <= 100):
        return "Equatorial Indian Ocean"

    # Southern Indian Ocean
    if (-40 <= latitude < -5) and (30 <= longitude <= 110):
        return "Southern Indian Ocean"

    return "Other Ocean Region"


# -----------------------------
# PROFILE LEVEL REGION
# -----------------------------
def classify_profile_region(profile_row: pd.Series) -> str:
    """
    Classify region for a single profile row.
    """
    lat = profile_row.get("latitude")
    lon = profile_row.get("longitude")

    return classify_region(lat, lon)


# -----------------------------
# FLOAT LEVEL REGION (majority logic)
# -----------------------------
def classify_float_region(float_profiles: pd.DataFrame) -> str:
    """
    Assign a dominant region to a float based on majority of its profiles.
    """

    if float_profiles.empty:
        return "Unknown"

    regions = float_profiles.apply(classify_profile_region, axis=1)

    if regions.empty:
        return "Unknown"

    return regions.value_counts().idxmax()


# -----------------------------
# ADD REGION COLUMN (vectorized)
# -----------------------------
def add_region_column(profiles: pd.DataFrame) -> pd.DataFrame:
    """
    Add region label to entire profiles dataframe.
    """

    df = profiles.copy()

    df["region"] = df.apply(
        lambda row: classify_region(row["latitude"], row["longitude"]),
        axis=1
    )

    return df


# -----------------------------
# REGION SUMMARY STATS
# -----------------------------
def get_region_distribution(profiles: pd.DataFrame) -> Dict[str, int]:
    """
    Count how many profiles fall into each region.
    """

    if "region" not in profiles.columns:
        profiles = add_region_column(profiles)

    return profiles["region"].value_counts().to_dict()


# -----------------------------
# REGION INTERPRETATION (for UI)
# -----------------------------
def get_region_description(region: str) -> str:
    """
    Provide scientific context for region (used in UI).
    """

    descriptions = {
        "Arabian Sea": "The Arabian Sea is known for strong seasonal monsoon-driven circulation and high biological productivity.",
        "Bay of Bengal": "The Bay of Bengal features strong freshwater influence and stratification due to river discharge.",
        "Equatorial Indian Ocean": "Equatorial waters are typically warm and show relatively weak vertical gradients.",
        "Southern Indian Ocean": "Southern Indian Ocean waters are cooler and often exhibit deeper mixing and weaker stratification.",
        "Other Ocean Region": "This region falls outside the primary classification zones used in FloatChat.",
        "Unknown": "Region could not be determined due to missing location data."
    }

    return descriptions.get(region, "No description available.")