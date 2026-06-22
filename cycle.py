import pandas as pd

profiles = pd.read_csv("data/processed/profiles_one.csv")
measurements = pd.read_csv("data/processed/measurements_one.csv")

print("Profiles rows:", len(profiles))
print("Measurements rows:", len(measurements))
print("\nUnique cycles in profiles:", profiles["cycle_number"].nunique())
print("Unique cycles in measurements:", measurements["cycle_number"].nunique())
print("\nLevels per cycle:")
print(measurements.groupby("cycle_number").size().head(20))