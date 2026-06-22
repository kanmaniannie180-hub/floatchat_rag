import streamlit as st

# -----------------------------
# CORE IMPORTS
# -----------------------------
from core.data_loader import load_data
from core.region_classifier import add_region_column

# -----------------------------
# COMPONENTS
# -----------------------------
from components.sidebar import render_sidebar

# -----------------------------
# PAGES
# -----------------------------
from views.overview import render_overview_page
from views.explorer import render_explorer_page
from views.comparison import render_comparison_page
from views.assistant import render_assistant_page
from views.analytics_page import render_analytics_page


# -----------------------------
# APP CONFIG
# -----------------------------
st.set_page_config(
    page_title="FloatChat",
    page_icon="🌊",
    layout="wide"
)

st.title("🌊 FloatChat — Explainable Ocean Intelligence System")


# -----------------------------
# LOAD DATA
# -----------------------------
try:
    profiles, measurements = load_data()
except Exception as e:
    st.error(f"❌ Data loading failed: {e}")
    st.stop()


# -----------------------------
# ADD REGION (important)
# -----------------------------
profiles = add_region_column(profiles)


# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
sidebar_state = render_sidebar(profiles, measurements)

selected_float = sidebar_state.get("selected_float")
selected_cycle = sidebar_state.get("selected_cycle")
selected_parameter = sidebar_state.get("selected_parameter")

compare_mode = sidebar_state.get("compare_mode")
comparison_type = sidebar_state.get("comparison_type")
comparison_cycle = sidebar_state.get("comparison_cycle")
second_float = sidebar_state.get("second_float")


# -----------------------------
# PAGE NAVIGATION
# -----------------------------
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    [
        "Overview",
        "Explorer",
        "Comparison",
        "Assistant",
        "Analytics"
    ]
)


# -----------------------------
# PAGE ROUTING
# -----------------------------
if page == "Overview":
    render_overview_page(profiles, measurements)

elif page == "Explorer":
    render_explorer_page(
        profiles,
        measurements,
        selected_float,
        selected_cycle,
        selected_parameter
    )

elif page == "Comparison":
    render_comparison_page(
        profiles,
        measurements,
        selected_float,
        selected_cycle,
        selected_parameter,
        compare_mode,
        comparison_type,
        comparison_cycle,
        second_float
    )

elif page == "Assistant":
    render_assistant_page(
        profiles,
        measurements,
        selected_float,
        selected_parameter
    )

elif page == "Analytics":
    render_analytics_page(
        profiles,
        measurements,
        selected_float,
        selected_parameter
    )


# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption(
    "FloatChat • ARGO Ocean Intelligence • Explainable AI + Scientific Analytics"
)