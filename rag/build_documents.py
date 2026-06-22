import sys
from pathlib import Path
import pickle

sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.data_loader import load_data

profiles, measurements = load_data()

documents = []
ids = []

for _, profile in profiles.iterrows():

    float_id = profile["float_id"]
    cycle = profile["cycle_number"]

    subset = measurements[
        (measurements["float_id"] == float_id)
        & (measurements["cycle_number"] == cycle)
    ]

    if subset.empty:
        continue

    temp_min = subset["temperature"].min()
    temp_max = subset["temperature"].max()

    sal_min = subset["salinity"].min()
    sal_max = subset["salinity"].max()

    max_pressure = subset["pressure"].max()

    document = f"""
    Float {float_id} profile {cycle}
    recorded on {profile['profile_date']}.

    Location:
    Latitude {profile['latitude']},
    Longitude {profile['longitude']}.

    Number of depth levels:
    {profile['n_levels_clean']}.

    Temperature ranges from
    {temp_min:.2f}°C to {temp_max:.2f}°C.

    Salinity ranges from
    {sal_min:.2f} PSU to {sal_max:.2f} PSU.

    Maximum observed pressure:
    {max_pressure:.2f} dbar.
    """

    documents.append(document)
    ids.append(f"{float_id}_{cycle}")

print("Documents created:", len(documents))

print("\nSample Document:\n")
print(documents[0])

with open("rag/documents.pkl", "wb") as f:
    pickle.dump(documents, f)

with open("rag/ids.pkl", "wb") as f:
    pickle.dump(ids, f)

print("\nSaved documents.pkl and ids.pkl")