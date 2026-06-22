import xarray as xr

ds = xr.open_dataset("data/raw/1900121_prof.nc")

print("Variables:")
for var in ds.variables:
    print(var)