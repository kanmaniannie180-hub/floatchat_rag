import pandas as pd

profiles = pd.read_parquet("data/processed/profiles_all.parquet")
measurements = pd.read_parquet("data/processed/measurements_all.parquet")

print("Profiles shape:", profiles.shape)
print("Measurements shape:", measurements.shape)

print("\nProfiles preview:")
print(profiles.head())

print("\nMeasurements preview:")
print(measurements.head())

print("\nUnique floats:", profiles["float_id"].nunique())
print("Unique cycles:", profiles["cycle_number"].nunique())

print("\nLevels summary:")
print(profiles["n_levels"].describe())

print("\nMissing values in profiles:")
print(profiles.isna().sum())

print("\nMissing values in measurements:")
print(measurements.isna().sum())