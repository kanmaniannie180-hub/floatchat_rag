import pandas as pd
import plotly.express as px

# Load data
profiles = pd.read_parquet("data/processed/profiles_all.parquet")
measurements = pd.read_parquet("data/processed/measurements_all.parquet")

# 🔥 Apply cleaning filters
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

# Optional: filter profiles based on cleaned measurements
valid_profiles = measurements[["float_id", "cycle_number"]].drop_duplicates()

profiles = profiles.merge(valid_profiles, on=["float_id", "cycle_number"], how="inner")

# Convert date
profiles["profile_date"] = pd.to_datetime(profiles["profile_date"])

# Sort for trajectory lines
profiles = profiles.sort_values(["float_id", "profile_date"])

# Plot
# Plot
fig = px.line_geo(
    profiles,
    lat="latitude",
    lon="longitude",
    color="float_id",
    hover_name="float_id",
    hover_data={
        "cycle_number": True,
        "profile_date": True,
        "latitude": ':.3f',
        "longitude": ':.3f'
    },
    title="ARGO Float Trajectories (Cleaned Data)"
)

fig.update_traces(mode="lines+markers", line=dict(width=2))

fig.update_geos(
    lataxis_range=[-40, 30],
    lonaxis_range=[30, 110]
)

fig.update_layout(showlegend=False)

fig.show()