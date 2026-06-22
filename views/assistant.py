


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

                    for source in result["sources"]:
                        st.success(source)

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

                        for i, doc in enumerate(
                            result["documents"],
                            start=1
                        ):

                            st.markdown(
                                f"### Context {i}"
                            )

                            st.write(doc)

                            st.markdown("---")

                    # =========================================
                    # SCIENTIFIC EXPLANATION
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
        FloatChat RAG Pipeline

        Question
            ↓
        ChromaDB Retrieval
            ↓
        Retrieved Ocean Profiles
            ↓
        Retrieval Scores
            ↓
        Retrieved Context
            ↓
        Gemini Scientific Reasoning
            ↓
        Explainable Ocean Intelligence
        """
    )

