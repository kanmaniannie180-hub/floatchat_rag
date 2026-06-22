import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/measurements_one.csv")

sample_cycle = df["cycle_number"].dropna().iloc[0]
sample = df[df["cycle_number"] == sample_cycle].copy()

plt.figure(figsize=(6, 8))
plt.plot(sample["temperature"], sample["pressure"])
plt.gca().invert_yaxis()
plt.xlabel("Temperature")
plt.ylabel("Pressure")
plt.title(f"Temperature Profile - Cycle {sample_cycle}")
plt.show()