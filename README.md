# FloatChat 🌊  
## AI-Powered Ocean Data Intelligence System

FloatChat is an interactive ocean intelligence platform that transforms complex ARGO oceanographic data into explainable insights using a multi-layer AI pipeline.

Developed for the **Neural Nexus AI/ML Hackathon 2026**.

---

## 🚀 Problem Statement

ARGO ocean data is:

- High-dimensional and large-scale  
- Stored in NetCDF scientific format  
- Difficult to interpret without domain expertise  

This creates a major barrier for:
- Students  
- Researchers  
- Analysts  

👉 Result: Ocean data remains **underutilized and inaccessible**

---

## 💡 Solution

FloatChat converts raw ARGO data into an **interactive, explainable AI-driven system** that enables:

- Natural language-based exploration  
- Scientific insight generation  
- Temporal and spatial analysis  
- Pattern detection in ocean profiles  

👉 **“From raw ocean data to explainable intelligence”**

---

## 🧠 System Architecture

FloatChat follows a **3-phase intelligent pipeline**:

Data Ingestion → Query Intelligence → Scientific Intelligence → Analytics Layer → Visualization + Insights


---

## ⚙️ Phase 1 — Query / AI Layer

Enables intuitive interaction with ocean data.

### Features:
- Natural language query assistant  
- Intent detection  
- Entity extraction:
  - Float ID  
  - Cycle number  
  - Parameter (temperature / salinity)  
- Explanation box (interpreted query)  
- Confidence + reasoning display  
- Guided prompts  
- Shortcuts:
  - Latest profile  
  - Earliest profile  
  - First vs latest comparison  

👉 Converts user queries → structured execution

---

## 🌊 Phase 2 — Scientific Intelligence

Adds domain-aware reasoning on top of raw data.

### Features:
- Thermocline detection  
- Temperature gradient analysis  
- Surface vs deep summaries  
- Region classification  
- Anomaly detection  
- Profile quality indicators  
- Depth-band summaries  

👉 Transforms raw measurements → scientific insights

---

## 📊 Phase 3 — Analytics Layer

Provides deeper exploration and comparison.

### Features:
- Heatmaps across cycles  
- Time-series analysis  
- First vs latest comparison  
- Two-float comparison  
- Multi-dimensional pattern visualization  

👉 Enables temporal + comparative understanding

---

## 📂 Dataset Collection

### Source:
- ARGO Global Data Repository  
- Indian Ocean ARGO float profiles  

### Format:
- NetCDF (`*_prof.nc`) files  

---

## 📥 Data Collection Process

1. Download ARGO float profile files (`*_prof.nc`)
2. Store files in:


data/raw/


---

## ⚙️ Data Processing Pipeline

### Step 1: Parsing NetCDF files

Using `xarray`, extract:
- Pressure (PRES)  
- Temperature (TEMP)  
- Salinity (PSAL)  
- Latitude / Longitude  
- Cycle number  
- Profile date  

---

### Step 2: Create structured datasets

#### Profiles Table
- float_id  
- cycle_number  
- latitude  
- longitude  
- profile_date  
- number of levels  

#### Measurements Table
- float_id  
- cycle_number  
- pressure  
- temperature  
- salinity  

---

### Step 3: Data Cleaning

Applied filters:

- Pressure: 0 to 2500 dbar  
- Temperature: -2°C to 40°C  
- Salinity: 0 to 50 PSU  
- Removed weak profiles (low depth levels)  

---

### Step 4: Storage

Processed data is stored in structured formats for efficient retrieval and visualization.

data/processed/
├── profiles_all.csv
├── measurements_all.csv
├── profiles_all.parquet
└── measurements_all.parquet
- **profiles_all.csv / parquet** → Contains profile-level metadata  
- **measurements_all.csv / parquet** → Contains depth-wise measurements  

👉 Parquet format is used for faster loading in the Streamlit application.


---

## 📊 Dataset Summary

- 25 ARGO float files  
- ~1,891 profiles  
- ~137,000 measurements  

---

## 🛠️ Tech Stack

### Programming:
- Python  

### Data Processing:
- pandas  
- numpy  
- xarray  
- netCDF4  
- pyarrow  

### Visualization:
- Plotly  
- matplotlib  

### App Framework:
- Streamlit  

---

---
## 📦 Project Structure

```
FloatChat/
│
├── app.py
│
├── core/
│   ├── data_loader.py
│   ├── query_engine.py
│   ├── insights.py
│   ├── analytics.py
│   └── utils.py
│
├── components/
│   ├── sidebar.py
│   ├── maps.py
│   ├── metrics.py
│   ├── query_panel.py
│   ├── insight_cards.py
│   └── comparison_panel.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── requirements.txt
└── README.md
```
---

##
---

## ▶️ How to Run

### 1. Install dependencies

pip install -r requirements.txt

### 2. Parse dataset

python parse_all.py

### 3. Run application

python -m streamlit run app.py

---

## 🎯 Key Features
- ARGO trajectory visualization  
- Temperature & salinity profiles  
- Cycle comparison  
- Query-based interaction  
- Explainable ocean insights  

## 🔬 Methodology
- Rule-based query interpretation  
- Gradient-based ocean analysis  
- Structured filtering  

## 📚 Research Inspiration
- ARGO Program Documentation  
- Ocean Stratification Studies  
- Explainable AI Systems  

## 💡 Innovation Highlights
- Multi-layer AI pipeline  
- Explainable intelligence  
- Event detection (thermocline, anomalies)

##  ⚠️ Limitations
- Focused on core ARGO parameters (TEMP, PSAL, PRES)
- Rule-based intelligence (no deep learning models)
- Limited geographic dataset scope

## 🚀 Future Scope
- BGC float integration
- Advanced anomaly detection
- Region-based querying
- Improved natural language reasoning

## 🏁Conclusion

FloatChat transforms complex oceanographic data into an accessible, explainable, and intelligent system, enabling users to explore and understand ocean behavior without requiring domain expertise.

## 🔥 Final Statement

“FloatChat transforms complex ocean data into explainable intelligence.”
