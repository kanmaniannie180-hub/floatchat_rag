import os
import xarray as xr
import pandas as pd
import numpy as np

file_path = r"data/raw/1900121_prof.nc"

ds = xr.open_dataset(file_path)

platform = ds["PLATFORM_NUMBER"].values
cycle = ds["CYCLE_NUMBER"].values
juld = ds["JULD"].values
lat = ds["LATITUDE"].values
lon = ds["LONGITUDE"].values
pres = ds["PRES"].values
temp = ds["TEMP"].values
psal = ds["PSAL"].values

profiles = []
measurements = []

# safer float id
float_id = os.path.basename(file_path).replace("_prof.nc", "").replace(".nc", "")

n_prof = pres.shape[0]
n_levels = pres.shape[1]

for i in range(n_prof):
    platform_num = str(platform[i]).strip() if len(platform.shape) > 0 else str(platform).strip()

    profiles.append({
        "float_id": float_id,
        "platform_number": platform_num,
        "cycle_number": int(cycle[i]) if not np.isnan(cycle[i]) else None,
        "profile_date": str(juld[i]),
        "latitude": float(lat[i]) if not np.isnan(lat[i]) else None,
        "longitude": float(lon[i]) if not np.isnan(lon[i]) else None,
        "n_levels": int(np.sum(~np.isnan(pres[i])))
    })

    for j in range(n_levels):
        if np.isnan(pres[i, j]):
            continue

        measurements.append({
            "float_id": float_id,
            "platform_number": platform_num,
            "cycle_number": int(cycle[i]) if not np.isnan(cycle[i]) else None,
            "profile_date": str(juld[i]),
            "latitude": float(lat[i]) if not np.isnan(lat[i]) else None,
            "longitude": float(lon[i]) if not np.isnan(lon[i]) else None,
            "pressure": float(pres[i, j]),
            "temperature": float(temp[i, j]) if not np.isnan(temp[i, j]) else None,
            "salinity": float(psal[i, j]) if not np.isnan(psal[i, j]) else None
        })

profiles_df = pd.DataFrame(profiles)
measurements_df = pd.DataFrame(measurements)

print("\nProfiles preview:")
print(profiles_df.head())

print("\nMeasurements preview:")
print(measurements_df.head())

profiles_df.to_csv("data/processed/profiles_one.csv", index=False)
measurements_df.to_csv("data/processed/measurements_one.csv", index=False)

print("\nSaved:")
print("data/processed/profiles_one.csv")
print("data/processed/measurements_one.csv")