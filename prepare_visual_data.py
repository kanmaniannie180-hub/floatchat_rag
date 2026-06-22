import pandas as pd

profiles = pd.read_parquet("data/processed/profiles_all.parquet")
measurements = pd.read_parquet("data/processed/measurements_all.parquet")

# Keep scientifically reasonable ranges for visualization
measurements_clean = measurements[
    (measurements["pressure"] >= 0) &
    (measurements["pressure"] <= 2500) &
    (measurements["temperature"] >= -2) &
    (measurements["temperature"] <= 40) &
    (measurements["salinity"] >= 0) &
    (measurements["salinity"] <= 50)
].copy()

# Recompute level counts after filtering
level_counts = (
    measurements_clean
    .groupby(["float_id", "cycle_number"])
    .size()
    .reset_index(name="n_levels_clean")
)

profiles_clean = profiles.merge(
    level_counts,
    on=["float_id", "cycle_number"],
    how="inner"
)

# Optional: keep only profiles with enough cleaned levels
profiles_clean = profiles_clean[profiles_clean["n_levels_clean"] >= 10].copy()

measurements_clean.to_parquet("data/processed/measurements_visual.parquet", index=False)
profiles_clean.to_parquet("data/processed/profiles_visual.parquet", index=False)

measurements_clean.to_csv("data/processed/measurements_visual.csv", index=False)
profiles_clean.to_csv("data/processed/profiles_visual.csv", index=False)

print("Saved cleaned visualization datasets.")
print("Profiles:", profiles_clean.shape)
print("Measurements:", measurements_clean.shape)