
import sys
from pathlib import Path
import pickle

sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.data_loader import load_data
profiles, measurements = load_data()

documents = []
ids = []
metadatas = []
low_surface = 0
strong_gradient = 0
high_salinity = 0
low_salinity = 0

print(
    "Latitude Range:",
    profiles["latitude"].min(),
    "to",
    profiles["latitude"].max()
)

print(
    "Longitude Range:",
    profiles["longitude"].min(),
    "to",
    profiles["longitude"].max()
)

sri_lanka_profiles = profiles[
    (profiles["latitude"] >= 5)
    & (profiles["latitude"] <= 15)
    & (profiles["longitude"] >= 75)
    & (profiles["longitude"] <= 85)
]

print(
    "Sri Lanka Profiles:",
    len(sri_lanka_profiles)
)


# ==========================================
# REGION CLASSIFICATION
# ==========================================
def classify_region(lat, lon):

    # Near Sri Lanka first
    if 5 <= lat <= 15 and 75 <= lon <= 85:
        return "Near Sri Lanka, Northern Indian Ocean"

    # Arabian Sea
    elif 5 <= lat <= 25 and 60 <= lon <= 75:
        return "Arabian Sea"

    # Bay of Bengal
    elif 5 <= lat <= 25 and 80 <= lon <= 100:
        return "Bay of Bengal"

    # General Indian Ocean
    elif -20 <= lat <= 25 and 40 <= lon <= 110:
        return "Indian Ocean"

    return "Ocean Region Unknown"


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

    latitude = profile["latitude"]
    longitude = profile["longitude"]

    # ==========================================
    # TEMPERATURE FEATURES
    # ==========================================
    surface_temp = subset["temperature"].iloc[0]
    deep_temp = subset["temperature"].iloc[-1]

    temp_difference = surface_temp - deep_temp

    if temp_difference > 15:
        thermocline = "Strong Thermocline Present"

    elif temp_difference > 8:
        thermocline = "Moderate Thermocline Present"

    else:
        thermocline = "Weak Thermocline"

    # ==========================================
    # ANOMALY DETECTION
    # ==========================================

    anomalies = []

    if surface_temp < 15:
        low_surface += 1
        anomalies.append(
            f"Low surface temperature ({surface_temp:.2f}°C)"
    )

    if temp_difference > 28:
        strong_gradient += 1
        anomalies.append(
            f"Strong temperature gradient ({temp_difference:.2f}°C)"
    )

    if sal_max > 36:
        high_salinity += 1
        anomalies.append(
            "High salinity event"
    )

    if sal_min < 30:
        low_salinity += 1
        anomalies.append(
            "Low salinity event"
    )

    if anomalies:
        anomaly = (
            "Possible anomalous profile detected: "
            + " | ".join(anomalies)
        )


    else:
        anomaly = "No Significant Anomaly"
    # ==========================================
    # REGION
    # ==========================================
    region = classify_region(
        latitude,
        longitude
    )
    # ==========================================
    # PROFILE TYPE
    # ==========================================
    if max_pressure > 1500:
        profile_type = "Deep Ocean Profile"

    elif max_pressure > 500:
        profile_type = "Mid-Ocean Profile"

    else:
        profile_type = "Surface Ocean Profile"

    # ==========================================
    # SALINITY EVENTS
    # ==========================================
    if sal_max > 35.5:
        salinity_event = "High Salinity Event"

    elif sal_min < 33:
        salinity_event = "Low Salinity Event"

    else:
        salinity_event = "Normal Salinity Conditions"

    # ==========================================
    # WATER TYPE
    # ==========================================
    if temp_max > 28:
        water_type = "Warm Tropical Water"

    elif temp_max > 20:
        water_type = "Subtropical Water"

    else:
        water_type = "Cold Ocean Water"

    # ==========================================
    # KEYWORDS
    # ==========================================
    keywords = [
        region,
        profile_type,
        water_type,
        salinity_event,
        thermocline,
        "Indian Ocean",
        "Ocean Stratification",
        "Temperature Gradient",
        "Ocean Profile",
        "Scientific Oceanography",
        "Ocean Measurements",
        "Temperature Variation",
        "Salinity Variation"
    ]

    keywords_text = "\n".join(keywords)

    # ==========================================
    # DOCUMENT
    # ==========================================
    document = f"""
    Float {float_id} profile {cycle}
    recorded on {profile['profile_date']}.

    Ocean Region:
    {region}

    Location:
    Latitude {latitude},
    Longitude {longitude}.

    Profile Type:
    {profile_type}

    Water Type:
    {water_type}

    Salinity Condition:
    {salinity_event}

    Thermocline Status:
    {thermocline}

    Anomaly Detection:
    {anomaly}

    Number of Depth Levels:
    {profile['n_levels_clean']}

    Maximum Depth:
    {max_pressure:.1f} meters

    Surface Temperature:
    {surface_temp:.2f}°C

    Deep Temperature:
    {deep_temp:.2f}°C

    Temperature Difference:
    {temp_difference:.2f}°C

    Temperature Range:
    {temp_min:.2f}°C to {temp_max:.2f}°C

    Salinity Range:
    {sal_min:.2f} PSU to {sal_max:.2f} PSU

    Keywords:
    {keywords_text}

    Scientific Summary:

    This profile represents a
    {profile_type}
    located in the
    {region}.

    Coordinates:
    Latitude {latitude:.2f}°,
    Longitude {longitude:.2f}°.

    Recorded on:
    {profile['profile_date']}

    Date Range Context:

    This profile was collected during
    {profile['profile_date']}

    and contributes to temporal analysis
    of Indian Ocean variability.

    Location Summary:

    This observation was collected at
    Latitude {latitude:.2f}°
    and Longitude {longitude:.2f}°
    within the {region}.

    The water mass is classified as
    {water_type}.

    Salinity analysis indicates
    {salinity_event}.

    Temperature analysis shows
    a difference of
    {temp_difference:.2f}°C
    between surface and deep waters.

    Thermocline assessment:
    {thermocline}.

    Maximum observed depth reaches
    {max_pressure:.1f} meters.

    This profile is suitable for studying:

    - Ocean Stratification
    - Temperature Gradients
    - Salinity Variation
    - Thermocline Behaviour
    - Regional Ocean Dynamics
    - Deep Ocean Conditions
    - Temporal Ocean Variability
    - Tropical Ocean Waters
    - Indian Ocean Dynamics
    """

    documents.append(document)

    ids.append(
        f"{float_id}_{cycle}"
    )
    if anomaly != "No Significant Anomaly":
        print(f"\n{float_id}_{cycle}")
        print(anomaly)
    metadatas.append(
    {
        "region": region,
        "profile_type": profile_type,
        "water_type": water_type,
        "salinity_event": salinity_event,
        "thermocline": thermocline,
        "anomaly": anomaly
    }
    )

print("Documents created:", len(documents))

print("\nSample Document:\n")
print(documents[0])

with open("rag/documents.pkl", "wb") as f:
    pickle.dump(documents, f)

with open("rag/ids.pkl", "wb") as f:
    pickle.dump(ids, f)

with open("rag/metadatas.pkl", "wb") as f:
    pickle.dump(metadatas, f)

print("\nSaved documents.pkl, ids.pkl and metadatas.pkl")

anomaly_count = sum(
    1 for m in metadatas
    if m["anomaly"] != "No Significant Anomaly"
)

print(f"\nAnomalous Profiles: {anomaly_count}")
print("Low surface temp:", low_surface)
print("Strong gradient:", strong_gradient)
print("High salinity:", high_salinity)
print("Low salinity:", low_salinity)
