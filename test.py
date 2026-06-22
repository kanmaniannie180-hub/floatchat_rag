import xarray as xr

ds = xr.open_dataset("data/raw/2900256_prof.nc")
print(ds)