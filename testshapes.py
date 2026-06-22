import xarray as xr

ds = xr.open_dataset("data/raw/1900121_prof.nc")

needed = ["PRES", "TEMP", "PSAL", "LATITUDE", "LONGITUDE", "JULD", "CYCLE_NUMBER"]

for name in needed:
    print(f"{name}: {'FOUND' if name in ds.variables else 'MISSING'}")
print("PRES shape:", ds["PRES"].shape if "PRES" in ds.variables else "Missing")
print("TEMP shape:", ds["TEMP"].shape if "TEMP" in ds.variables else "Missing")
print("PSAL shape:", ds["PSAL"].shape if "PSAL" in ds.variables else "Missing")
print("LATITUDE shape:", ds["LATITUDE"].shape if "LATITUDE" in ds.variables else "Missing")
print("LONGITUDE shape:", ds["LONGITUDE"].shape if "LONGITUDE" in ds.variables else "Missing")
print("JULD shape:", ds["JULD"].shape if "JULD" in ds.variables else "Missing")
print("CYCLE_NUMBER shape:", ds["CYCLE_NUMBER"].shape if "CYCLE_NUMBER" in ds.variables else "Missing")
print("LATITUDE:", ds["LATITUDE"].values[:5])
print("LONGITUDE:", ds["LONGITUDE"].values[:5])
print("JULD:", ds["JULD"].values[:5])
print("CYCLE_NUMBER:", ds["CYCLE_NUMBER"].values[:5])
print("PRES first profile:", ds["PRES"].values[0][:10])
print("TEMP first profile:", ds["TEMP"].values[0][:10])
print("PSAL first profile:", ds["PSAL"].values[0][:10])