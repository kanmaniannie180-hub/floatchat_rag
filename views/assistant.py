

import matplotlib.pyplot as plt
import profile
from unittest import result
import plotly.express as px
import streamlit as st
import pandas as pd

from components.query_panel import (
    render_query_input,
    render_query_output
)

from core.query_engine import parse_query

from rag.gemini_rag import ask_floatchat


def render_assistant_page(
    profiles: pd.DataFrame,
    measurements: pd.DataFrame,
    selected_float: str,
    selected_parameter: str,
):
    st.title("🤖 FloatChat Assistant")
    st.caption("Query ocean data using natural language.")
    # ==========================================
    # QUERY HISTORY
    # ==========================================

    if "history" not in st.session_state:
        st.session_state.history = []

    st.markdown(
        """
        Try queries like:

        - Show all trajectories
        - Show float 1900122
        - Show latest temperature profile
        - Compare cycle 1 and 5
        - Show salinity for cycle 3
        """
    )

    st.markdown("---")

    # ==================================================
    # EXISTING QUERY ASSISTANT
    # ==================================================
    st.subheader("📊 Query-Based Assistant")

    query = render_query_input(selected_float)

    if query and query.strip():

        float_ids = profiles["float_id"].unique().tolist()

        parsed = parse_query(
            query=query,
            float_ids=float_ids,
            profiles=profiles,
            selected_float=selected_float,
        )

        render_query_output(
            parsed=parsed,
            profiles=profiles,
            measurements=measurements,
            selected_float=selected_float,
            selected_parameter=selected_parameter,
        )

    else:
        st.info(
            "Enter a query or use one of the sample prompts above."
        )

    st.markdown("---")

    # ==================================================
    # RAG ASSISTANT
    # ==================================================
    st.header("🌊 FloatChat RAG Assistant")

    st.caption(
        "Retrieval-Augmented Ocean Intelligence using "
        "ChromaDB + Gemini"
    )

    st.markdown(
        """
        Example Questions:

        - Which profiles indicate deep ocean conditions?
        - Find profiles with high salinity levels.
        - Which retrieved profiles show the warmest temperatures?
        - Compare warm surface waters and deep ocean waters.
        - Explain temperature patterns in the retrieved profiles.
        """
    )

    rag_query = st.text_area(
        "Ask an Oceanographic Question",
        height=100,
        placeholder="Which profiles indicate deep ocean conditions?"
    )

    if st.button(
        "🚀 Ask FloatChat",
        use_container_width=True
    ):

        if not rag_query.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Retrieving ocean profiles and generating explanation..."
            ):

                try:

                    result = ask_floatchat(rag_query)

                    # =========================================
                    # RETRIEVAL METRIC
                    # =========================================
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Profiles Retrieved",
                            len(result["sources"])
                        )

                    with col2:
                        st.metric(
                            "Vector Database",
                            "ChromaDB"
                        )

                    # =========================================
                    # RETRIEVED PROFILES
                    # =========================================
                    st.subheader("Step 1: Retrieved Profiles")

                    for source, metadata in zip(
                        result["sources"],
                        result["metadata"]
                    ):

                        st.success(source)

                        st.caption(
                            f"""
                    **Region:** {metadata['region']}

                    **Profile Type:** {metadata['profile_type']}

                    **Water Type:** {metadata['water_type']}

                    **Thermocline:** {metadata['thermocline']}

                    **Salinity:** {metadata['salinity_event']}
                    """
                        )

                        # Show anomaly only if one exists
                        if metadata["anomaly"] != "No Significant Anomaly":
                            st.warning(metadata["anomaly"])

                    # =========================================
                    # RETRIEVAL SCORES
                    # =========================================
                    st.subheader("Step 2: Similarity Scores")

                    for source, distance in zip(
                        result["sources"],
                        result["distances"]
                    ):

                        st.write(
                            f"{source} → Distance: {round(distance, 4)}"
                        )


                    # =========================================
                    # RETRIEVED CONTEXT
                    # =========================================
                
                    with st.expander(
                        "Step 3: Retrieved Evidence"
                    ):

                        for source, doc in zip(
                            result["sources"],
                            result["documents"]
                        ):

                            st.markdown(f"### 📄 {source}")

                            st.write(doc)

                            st.markdown("---")

                    # =========================================
                    # SCIENTIFIC EXPLANATION
                    # =========================================
                    
                    # =========================================
                    # TEMPERATURE PROFILE DATA (TEST)
                    # =========================================
                    st.subheader("🌡️ Temperature vs Depth (Data Check)")

                    profile = measurements[
                        (measurements["float_id"] == result["top_float"])
                            &
                        (measurements["cycle_number"] == result["top_cycle"])
                        ]

                    fig, ax = plt.subplots(figsize=(5.5, 4.5))

                    ax.plot(
                    profile["temperature"],
                    profile["pressure"],
                    marker="o",
                    markersize=2,
                    linewidth=1.5
                    )

                    ax.set_xlabel("Temperature (°C)")
                    ax.set_ylabel("Pressure (dbar)")
                    ax.set_title(
                    f"Temperature Profile\nFloat {result['top_float']} | Cycle {result['top_cycle']}",
                    fontsize=13,
                    fontweight="bold"
                    )

                    ax.invert_yaxis()
                    ax.set_xlim(
                    profile["temperature"].min() - 1,
                    profile["temperature"].max() + 1
                    )
                    ax.grid(True, linestyle="--", alpha=0.5)
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)
                    # =========================================
                    # SALINITY PROFILE
                    # =========================================
                    st.subheader("🧂 Salinity vs Depth")

                    fig, ax = plt.subplots(figsize=(5.5, 4.5))

                    ax.plot(
                    profile["salinity"],
                    profile["pressure"],
                    marker="o",
                    markersize=2,
                    linewidth=1.5
                    )

                    ax.set_xlabel("Salinity (PSU)")
                    ax.set_ylabel("Pressure (dbar)")

                    ax.set_title(
                    f"Salinity Profile\nFloat {result['top_float']} | Cycle {result['top_cycle']}",
                    fontsize=13,
                    fontweight="bold"
                    )

                    ax.invert_yaxis()

                    ax.set_xlim(
                    profile["salinity"].min() - 0.2,
                    profile["salinity"].max() + 0.2
                    )

                    ax.grid(True, linestyle="--", alpha=0.5)

                    plt.tight_layout()

                    st.pyplot(fig)

                    plt.close(fig)
                    st.subheader("🗺️ Retrieved Float Locations")

                    retrieved_profiles = profiles[
                    profiles.apply(
                        lambda row: f"{row['float_id']}_{row['cycle_number']}"
                        in result["sources"],
                        axis=1
                    )
                    ].copy()
                    retrieved_profiles["Profile"] = (
                        retrieved_profiles["float_id"].astype(str)
                        + "_"
                        + retrieved_profiles["cycle_number"].astype(str)
                        )

                    retrieved_profiles["Region"] = [
                    m["region"] for m in result["metadata"]
                    ]

                    retrieved_profiles["Water Type"] = [
                    m["water_type"] for m in result["metadata"]
                    ]

                    fig = px.scatter_map(
                        retrieved_profiles,
                        lat="latitude",
                        lon="longitude",
                        hover_name="Profile",
                        hover_data={
                            "cycle_number": True,
                            "Region": True,
                            "Water Type": True,
                            "latitude": ":.2f",
                            "longitude": ":.2f"
                            },
                        color="Region",
                        zoom=4,
                        height=500
                        )

                    fig.update_layout(
                        margin=dict(l=0, r=0, t=40, b=0)
                        )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )
                    # =========================================
                    # OCEAN PROFILE HIGHLIGHTS
                    # =========================================

                    st.subheader("📊 Ocean Profile Highlights")

                    # Initialize variables
                    deepest_profile = None
                    warmest_profile = None
                    highest_salinity_profile = None

                    deepest_depth = -1
                    warmest_temp = -999
                    highest_salinity = -999

                    st.write("Retrieved Profiles:")
                    st.write(
                    retrieved_profiles[
                    ["float_id", "cycle_number"]
                    ]
                    )

                    # Find the deepest, warmest and highest salinity profiles
                    for _, row in retrieved_profiles.iterrows():

                        profile = measurements[
                        (measurements["float_id"] == row["float_id"])
                        &
                        (measurements["cycle_number"] == row["cycle_number"])
                        ]

                        if profile.empty:
                            continue

                        max_depth = profile["pressure"].max()
                        surface_temp = profile.iloc[0]["temperature"]
                        max_salinity = profile["salinity"].max()
                        st.write(
                            f"{row['float_id']}_{row['cycle_number']}",
                            max_depth,
                            surface_temp,
                            max_salinity
                        )

                        if max_depth > deepest_depth:
                            deepest_depth = max_depth
                            deepest_profile = row

                        if surface_temp > warmest_temp:
                            warmest_temp = surface_temp
                            warmest_profile = row

                        if max_salinity > highest_salinity:
                            highest_salinity = max_salinity
                            highest_salinity_profile = row

                    # Display highlight cards
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                        "🏆 Deepest Profile",
                        f"{deepest_profile['float_id']}_{deepest_profile['cycle_number']}",
                        f"{deepest_depth:.1f} m"
                        )

                    with col2:
                        st.metric(
                        "🔥 Warmest Profile",
                        f"{warmest_profile['float_id']}_{warmest_profile['cycle_number']}",
                        f"{warmest_temp:.2f} °C"
                        )

                    with col3:
                        st.metric(
                        "🧂 Highest Salinity",
                        f"{highest_salinity_profile['float_id']}_{highest_salinity_profile['cycle_number']}",
                        f"{highest_salinity:.2f} PSU"
                        )
                    with st.expander("🔍 Highlight Card Debug"):

                        debug_rows = []

                    for _, row in retrieved_profiles.iterrows():

                        profile = measurements[
                            (measurements["float_id"] == row["float_id"])
                            &
                            (measurements["cycle_number"] == row["cycle_number"])
                        ]

                        if profile.empty:
                            continue

                        debug_rows.append({
                            "Profile": f"{row['float_id']}_{row['cycle_number']}",
                            "Max Depth (m)": round(profile["pressure"].max(), 1),
                            "Surface Temp (°C)": round(profile.iloc[0]["temperature"], 2),
                            "Max Salinity (PSU)": round(profile["salinity"].max(), 2),
                        })

                    st.dataframe(debug_rows, use_container_width=True)
                    st.divider()
                    # =========================================
                    # SCIENTIFIC REASONING
                    # =========================================

                    st.subheader(
                    "Step 4: Scientific Reasoning"
                    )

                    st.write(
                    result["answer"]
                    )
                except Exception as e:

                    st.error(
                        f"RAG Assistant Error: {e}"
                    )

                    st.markdown("---")

                st.info(
                    """
        
        User Question
                ↓
        Region Detection
                ↓
        Metadata Filtering
                ↓
        Vector Similarity Search
                ↓
        Retrieved Profiles
                ↓
        Retrieved Evidence
                ↓
        Gemini Scientific Reasoning
                ↓
        Ocean Intelligence
        
        """
                )