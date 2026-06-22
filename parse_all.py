from pathlib import Path
import os
import xarray as xr
import pandas as pd
import numpy as np

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

MIN_LEVELS = 10  # skip weak/incomplete profiles


def clean_platform_number(value):
    if isinstance(value, bytes):
        return value.decode().strip()
    return str(value).strip()


def to_scalar(value):
    if isinstance(value, np.ndarray):
        if value.size == 1:
            return value.item()
    return value


def valid_number(x):
    return x is not None and not pd.isna(x)


def parse_file(file_path: Path):
    ds = xr.open_dataset(file_path)

    required_vars = [
        "PLATFORM_NUMBER",
        "CYCLE_NUMBER",
        "JULD",
        "LATITUDE",
        "LONGITUDE",
        "PRES",
        "TEMP",
        "PSAL",
    ]

    missing = [v for v in required_vars if v not in ds.variables]
    if missing:
        raise ValueError(f"Missing required variables: {missing}")

    platform = ds["PLATFORM_NUMBER"].values
    cycle = ds["CYCLE_NUMBER"].values
    juld = ds["JULD"].values
    lat = ds["LATITUDE"].values
    lon = ds["LONGITUDE"].values
    pres = ds["PRES"].values
    temp = ds["TEMP"].values
    psal = ds["PSAL"].values

    float_id = file_path.name.replace("_prof.nc", "").replace(".nc", "")

    profiles = []
    measurements = []

    n_prof = pres.shape[0]
    n_levels_total = pres.shape[1]

    for i in range(n_prof):
        pres_i = pres[i]

        # Convert masked arrays / invalid values to NaN-friendly form
        pres_i = np.array(pres_i, dtype=float)
        temp_i = np.array(temp[i], dtype=float)
        psal_i = np.array(psal[i], dtype=float)

        valid_pres_mask = ~np.isnan(pres_i)
        n_levels = int(np.sum(valid_pres_mask))

        # Skip weak profiles
        if n_levels < MIN_LEVELS:
            continue

        platform_num = clean_platform_number(to_scalar(platform[i]))
        cycle_num = to_scalar(cycle[i])
        profile_date = str(to_scalar(juld[i]))
        latitude = to_scalar(lat[i])
        longitude = to_scalar(lon[i])

        profiles.append({
            "float_id": float_id,
            "platform_number": platform_num,
            "cycle_number": int(cycle_num) if valid_number(cycle_num) else None,
            "profile_date": profile_date,
            "latitude": float(latitude) if valid_number(latitude) else None,
            "longitude": float(longitude) if valid_number(longitude) else None,
            "n_levels": n_levels,
            "source_file": file_path.name,
        })

        for j in range(n_levels_total):
            pressure = pres_i[j]

            if np.isnan(pressure):
                continue

            temperature = temp_i[j] if j < len(temp_i) else np.nan
            salinity = psal_i[j] if j < len(psal_i) else np.nan

            measurements.append({
                "float_id": float_id,
                "platform_number": platform_num,
                "cycle_number": int(cycle_num) if valid_number(cycle_num) else None,
                "profile_date": profile_date,
                "latitude": float(latitude) if valid_number(latitude) else None,
                "longitude": float(longitude) if valid_number(longitude) else None,
                "pressure": float(pressure),
                "temperature": float(temperature) if not np.isnan(temperature) else None,
                "salinity": float(salinity) if not np.isnan(salinity) else None,
                "source_file": file_path.name,
            })

    ds.close()
    return pd.DataFrame(profiles), pd.DataFrame(measurements)


def main():
    files = sorted(RAW_DIR.glob("*.nc"))

    if not files:
        print("No .nc files found in data/raw")
        return

    all_profiles = []
    all_measurements = []

    parsed_files = 0
    failed_files = 0

    for file_path in files:
        try:
            profiles_df, measurements_df = parse_file(file_path)

            if not profiles_df.empty:
                all_profiles.append(profiles_df)

            if not measurements_df.empty:
                all_measurements.append(measurements_df)

            parsed_files += 1
            print(
                f"Parsed: {file_path.name} | "
                f"profiles={len(profiles_df)} | measurements={len(measurements_df)}"
            )

        except Exception as e:
            failed_files += 1
            print(f"Failed: {file_path.name} -> {e}")

    if not all_profiles:
        print("No valid profiles extracted.")
        return

    profiles = pd.concat(all_profiles, ignore_index=True)
    measurements = pd.concat(all_measurements, ignore_index=True)

    # Optional extra cleanup
    profiles = profiles.drop_duplicates().reset_index(drop=True)
    measurements = measurements.drop_duplicates().reset_index(drop=True)

    # Save CSV
    profiles.to_csv(PROCESSED_DIR / "profiles_all.csv", index=False)
    measurements.to_csv(PROCESSED_DIR / "measurements_all.csv", index=False)

    # Save Parquet
    profiles.to_parquet(PROCESSED_DIR / "profiles_all.parquet", index=False)
    measurements.to_parquet(PROCESSED_DIR / "measurements_all.parquet", index=False)

    print("\nDone.")
    print(f"Files parsed successfully: {parsed_files}")
    print(f"Files failed: {failed_files}")
    print(f"Total profiles: {len(profiles)}")
    print(f"Total measurements: {len(measurements)}")
    print("\nSaved:")
    print("data/processed/profiles_all.csv")
    print("data/processed/measurements_all.csv")
    print("data/processed/profiles_all.parquet")
    print("data/processed/measurements_all.parquet")


if __name__ == "__main__":
    main()