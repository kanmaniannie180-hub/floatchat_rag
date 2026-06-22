from pathlib import Path
import pandas as pd


def get_data_dir() -> Path:
    """
    Returns the absolute path to:
    floatchat/views/data/processed
    """
    return Path(__file__).resolve().parents[1] / "views" / "data" / "processed"


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    df_name: str
) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"{df_name} is missing required columns: {missing}")


def clean_measurements(measurements: pd.DataFrame) -> pd.DataFrame:
    measurements = measurements.copy()

    measurements = measurements[
        (measurements["pressure"] >= 0) &
        (measurements["pressure"] <= 2500)
    ]

    measurements = measurements[
        (measurements["temperature"].isna()) |
        ((measurements["temperature"] >= -2) & (measurements["temperature"] <= 40))
    ]

    measurements = measurements[
        (measurements["salinity"].isna()) |
        ((measurements["salinity"] >= 0) & (measurements["salinity"] <= 50))
    ]

    return measurements


def normalize_types(
    profiles: pd.DataFrame,
    measurements: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    profiles = profiles.copy()
    measurements = measurements.copy()

    profiles["profile_date"] = pd.to_datetime(profiles["profile_date"], errors="coerce")
    measurements["profile_date"] = pd.to_datetime(measurements["profile_date"], errors="coerce")

    profiles["float_id"] = profiles["float_id"].astype(str)
    measurements["float_id"] = measurements["float_id"].astype(str)

    profiles["cycle_number"] = pd.to_numeric(profiles["cycle_number"], errors="coerce")
    measurements["cycle_number"] = pd.to_numeric(measurements["cycle_number"], errors="coerce")

    numeric_cols = ["latitude", "longitude", "pressure", "temperature", "salinity"]

    for col in numeric_cols:
        if col in profiles.columns:
            profiles[col] = pd.to_numeric(profiles[col], errors="coerce")
        if col in measurements.columns:
            measurements[col] = pd.to_numeric(measurements[col], errors="coerce")

    return profiles, measurements


def keep_profiles_with_valid_measurements(
    profiles: pd.DataFrame,
    measurements: pd.DataFrame
) -> pd.DataFrame:
    valid_profiles = measurements[["float_id", "cycle_number"]].drop_duplicates()

    profiles = profiles.merge(
        valid_profiles,
        on=["float_id", "cycle_number"],
        how="inner"
    )
    return profiles


def attach_clean_level_counts(
    profiles: pd.DataFrame,
    measurements: pd.DataFrame
) -> pd.DataFrame:
    level_counts = (
        measurements.groupby(["float_id", "cycle_number"])
        .size()
        .reset_index(name="n_levels_clean")
    )

    profiles = profiles.merge(
        level_counts,
        on=["float_id", "cycle_number"],
        how="left"
    )
    return profiles


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    data_dir = get_data_dir()
    profiles_path = data_dir / "profiles_all.parquet"
    measurements_path = data_dir / "measurements_all.parquet"

    if not profiles_path.exists():
        raise FileNotFoundError(f"Missing file: {profiles_path}")
    if not measurements_path.exists():
        raise FileNotFoundError(f"Missing file: {measurements_path}")

    profiles = pd.read_parquet(profiles_path)
    measurements = pd.read_parquet(measurements_path)

    validate_required_columns(
        profiles,
        ["float_id", "cycle_number", "profile_date", "latitude", "longitude"],
        "profiles"
    )

    validate_required_columns(
        measurements,
        ["float_id", "cycle_number", "profile_date", "pressure", "temperature", "salinity"],
        "measurements"
    )

    profiles, measurements = normalize_types(profiles, measurements)
    measurements = clean_measurements(measurements)
    profiles = keep_profiles_with_valid_measurements(profiles, measurements)
    profiles = attach_clean_level_counts(profiles, measurements)

    return profiles, measurements