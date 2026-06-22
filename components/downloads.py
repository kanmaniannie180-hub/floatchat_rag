import streamlit as st
import pandas as pd
from typing import Optional


def _to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def render_profile_download(profile_data: pd.DataFrame, float_id: str, cycle_number: int) -> None:
    """
    Download selected profile data as CSV.
    """
    st.markdown("### ⬇️ Downloads")

    if profile_data.empty:
        st.info("No selected profile data available for download.")
        return

    st.download_button(
        "Download Selected Profile CSV",
        data=_to_csv_bytes(profile_data),
        file_name=f"{float_id}_cycle_{cycle_number}_profile.csv",
        mime="text/csv",
        use_container_width=True
    )


def render_metadata_download(selected_profile_row: pd.Series, float_id: str, cycle_number: int) -> None:
    """
    Download selected profile metadata as CSV.
    """
    metadata_df = pd.DataFrame([{
        "float_id": float_id,
        "cycle_number": cycle_number,
        "profile_date": selected_profile_row.get("profile_date"),
        "latitude": selected_profile_row.get("latitude"),
        "longitude": selected_profile_row.get("longitude"),
        "n_levels_clean": selected_profile_row.get("n_levels_clean"),
        "region": selected_profile_row.get("region", None),
    }])

    st.download_button(
        "Download Metadata CSV",
        data=_to_csv_bytes(metadata_df),
        file_name=f"{float_id}_cycle_{cycle_number}_metadata.csv",
        mime="text/csv",
        use_container_width=True
    )


def render_comparison_download(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    float_a: str,
    float_b: str,
    parameter: str,
    cycle: Optional[int] = None,
) -> None:
    """
    Download two-float or two-cycle comparison data as one CSV.
    """
    st.markdown("### ⬇️ Comparison Download")

    if df_a.empty or df_b.empty:
        st.info("No comparison data available for download.")
        return

    left = df_a.copy()
    right = df_b.copy()

    left["comparison_source"] = f"float_{float_a}"
    right["comparison_source"] = f"float_{float_b}"

    combined = pd.concat([left, right], ignore_index=True)

    cycle_suffix = f"_cycle_{cycle}" if cycle is not None else "_latest"
    filename = f"comparison_{float_a}_vs_{float_b}_{parameter}{cycle_suffix}.csv"

    st.download_button(
        "Download Comparison CSV",
        data=_to_csv_bytes(combined),
        file_name=filename,
        mime="text/csv",
        use_container_width=True
    )