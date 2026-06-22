import re
import pandas as pd
from typing import List, Tuple, Optional


# -----------------------------
# TEXT / QUERY HELPERS
# -----------------------------
def normalize_text(text: str) -> str:
    """
    Lowercase + strip + remove extra spaces.
    """
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.lower().strip())


def extract_numbers(text: str) -> List[int]:
    """
    Extract all integer numbers from text.
    Example: "cycle 1 and 5" → [1, 5]
    """
    return [int(x) for x in re.findall(r"\d+", text)]


# -----------------------------
# SAFE VALUE HELPERS
# -----------------------------
def safe_float(val) -> Optional[float]:
    try:
        if pd.isna(val):
            return None
        return float(val)
    except Exception:
        return None


def safe_int(val) -> Optional[int]:
    try:
        if pd.isna(val):
            return None
        return int(val)
    except Exception:
        return None


# -----------------------------
# CYCLE UTILITIES
# -----------------------------
def get_available_cycles(df: pd.DataFrame) -> List[int]:
    return sorted(
        df["cycle_number"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )


def get_latest_cycle(df: pd.DataFrame) -> Optional[int]:
    cycles = get_available_cycles(df)
    return cycles[-1] if cycles else None


def get_earliest_cycle(df: pd.DataFrame) -> Optional[int]:
    cycles = get_available_cycles(df)
    return cycles[0] if cycles else None


def get_first_vs_latest_cycles(df: pd.DataFrame) -> Tuple[Optional[int], Optional[int]]:
    cycles = get_available_cycles(df)
    if len(cycles) >= 2:
        return cycles[0], cycles[-1]
    elif len(cycles) == 1:
        return cycles[0], cycles[0]
    return None, None


# -----------------------------
# DEPTH BAND UTILITIES (Phase 2+)
# -----------------------------
def split_depth_bands(df: pd.DataFrame):
    """
    Returns depth band slices:
    0–50, 50–200, 200–1000, 1000+
    """
    return {
        "0-50": df[df["pressure"] <= 50],
        "50-200": df[(df["pressure"] > 50) & (df["pressure"] <= 200)],
        "200-1000": df[(df["pressure"] > 200) & (df["pressure"] <= 1000)],
        "1000+": df[df["pressure"] > 1000],
    }


# -----------------------------
# DATA FILTER HELPERS
# -----------------------------
def filter_float(df: pd.DataFrame, float_id: str) -> pd.DataFrame:
    return df[df["float_id"] == str(float_id)]


def filter_cycle(df: pd.DataFrame, float_id: str, cycle: int) -> pd.DataFrame:
    return df[
        (df["float_id"] == str(float_id)) &
        (df["cycle_number"] == cycle)
    ].sort_values("pressure")


# -----------------------------
# CONFIDENCE HELPERS (Phase 1 AI)
# -----------------------------
def clamp_confidence(score: int) -> int:
    return max(0, min(score, 99))


def confidence_label(score: int) -> str:
    if score >= 90:
        return "High"
    elif score >= 70:
        return "Medium"
    else:
        return "Low"


# -----------------------------
# VALIDATION HELPERS
# -----------------------------
def has_valid_profile(df: pd.DataFrame) -> bool:
    return not df.empty and df["pressure"].notna().any()


def ensure_non_empty(df: pd.DataFrame, message: str = "No data available"):
    if df.empty:
        raise ValueError(message)