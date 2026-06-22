import re
from typing import Dict, Any, List, Optional

import pandas as pd

from core.utils import normalize_text, extract_numbers, clamp_confidence


# -----------------------------
# MAIN QUERY PARSER
# -----------------------------
def parse_query(
    query: str,
    float_ids: List[str],
    profiles: pd.DataFrame,
    selected_float: Optional[str] = None
) -> Dict[str, Any]:

    q = normalize_text(query)

    result = {
        "intent": "unknown",
        "view_mode": None,
        "float_id": None,
        "parameter": None,
        "cycle": None,
        "compare": False,
        "compare_cycles": [],
        "confidence": 40,
        "reasoning": [],
        "raw_query": query
    }

    # -----------------------------
    # 1. ALL TRAJECTORIES
    # -----------------------------
    if any(k in q for k in ["all trajectories", "show trajectories", "all floats"]):
        result["intent"] = "all_trajectories"
        result["view_mode"] = "Trajectory Overview"
        result["confidence"] = 95
        result["reasoning"].append("Detected request for global trajectory overview.")
        return result

    # -----------------------------
    # 2. FLOAT DETECTION
    # -----------------------------
    float_match = re.search(r'float\s+(\d+)', q)
    if float_match:
        fid = float_match.group(1)
        if fid in [str(x) for x in float_ids]:
            result["float_id"] = fid
            result["confidence"] += 25
            result["reasoning"].append(f"Explicit float ID detected: {fid}")

    if result["float_id"] is None:
        for fid in float_ids:
            if str(fid) in q:
                result["float_id"] = str(fid)
                result["confidence"] += 20
                result["reasoning"].append(f"Float ID inferred from text: {fid}")
                break

    if result["float_id"] is None and selected_float:
        result["float_id"] = str(selected_float)
        result["confidence"] += 10
        result["reasoning"].append("Using currently selected float (not specified in query).")

    # -----------------------------
    # 3. PARAMETER DETECTION
    # -----------------------------
    if "temperature" in q or "temp" in q:
        result["parameter"] = "temperature"
        result["confidence"] += 20
        result["reasoning"].append("Temperature parameter detected.")

    elif "salinity" in q or "psal" in q:
        result["parameter"] = "salinity"
        result["confidence"] += 20
        result["reasoning"].append("Salinity parameter detected.")

    # -----------------------------
    # 4. LATEST PROFILE
    # -----------------------------
    latest_match = re.search(r'latest profile(?: for float (\d+))?', q)
    if latest_match:
        result["intent"] = "latest_profile"

        if latest_match.group(1):
            result["float_id"] = latest_match.group(1)
            result["confidence"] += 20
            result["reasoning"].append(f"Latest profile requested for float {latest_match.group(1)}.")

        if result["parameter"] is None:
            result["parameter"] = "temperature"
            result["reasoning"].append("Defaulted parameter to temperature.")

        if result["float_id"]:
            fp = profiles[profiles["float_id"] == str(result["float_id"])]
            if not fp.empty:
                result["cycle"] = int(fp["cycle_number"].max())
                result["confidence"] += 20
                result["reasoning"].append(f"Resolved latest cycle as {result['cycle']}.")

        result["confidence"] = clamp_confidence(result["confidence"])
        return result

    # -----------------------------
    # 5. SHOW FLOAT TRAJECTORY
    # -----------------------------
    if "show float" in q or q.startswith("float "):
        if result["float_id"]:
            result["intent"] = "float_trajectory"
            result["confidence"] = max(result["confidence"], 95)
            result["reasoning"].append("Detected float trajectory request.")
            return result

    # -----------------------------
    # 6. COMPARE CYCLES
    # -----------------------------
    compare_match = re.search(r'compare\s+cycle\s+(\d+)\s+(and|vs)\s+(\d+)', q)
    if compare_match:
        c1 = int(compare_match.group(1))
        c2 = int(compare_match.group(3))

        result["intent"] = "compare_cycles"
        result["compare"] = True
        result["compare_cycles"] = [c1, c2]

        if result["parameter"] is None:
            result["parameter"] = "temperature"
            result["reasoning"].append("Defaulted parameter to temperature.")

        result["confidence"] = max(result["confidence"], 92)
        result["reasoning"].append(f"Detected comparison between cycles {c1} and {c2}.")

        return result

    # -----------------------------
    # 7. PARAMETER FOR CYCLE
    # -----------------------------
    metric_cycle = re.search(r'(temperature|salinity)\s+for\s+cycle\s+(\d+)', q)
    if metric_cycle:
        result["intent"] = "metric_for_cycle"
        result["parameter"] = metric_cycle.group(1)
        result["cycle"] = int(metric_cycle.group(2))

        result["confidence"] = max(result["confidence"], 95)
        result["reasoning"].append(
            f"Detected {result['parameter']} request for cycle {result['cycle']}."
        )
        return result

    # -----------------------------
    # 8. GENERIC CYCLE DETECTION
    # -----------------------------
    cycles = extract_numbers(q)

    if len(cycles) == 1:
        result["cycle"] = cycles[0]

        if result["parameter"]:
            result["intent"] = "metric_for_cycle"
            result["confidence"] = max(result["confidence"], 80)
            result["reasoning"].append(f"Single cycle detected: {cycles[0]}")
            return result

    elif len(cycles) >= 2:
        result["intent"] = "compare_cycles"
        result["compare"] = True
        result["compare_cycles"] = [cycles[0], cycles[1]]

        if result["parameter"] is None:
            result["parameter"] = "temperature"

        result["confidence"] = max(result["confidence"], 80)
        result["reasoning"].append(f"Multiple cycles detected: {cycles[:2]}")
        return result

    # -----------------------------
    # FALLBACK
    # -----------------------------
    if result["float_id"]:
        result["intent"] = "float_trajectory"
        result["confidence"] = max(result["confidence"], 70)
        result["reasoning"].append("Fallback: float detected, assuming trajectory request.")

    result["confidence"] = clamp_confidence(result["confidence"])
    return result


# -----------------------------
# SYSTEM RESPONSE
# -----------------------------
def build_system_response(parsed: Dict[str, Any]) -> str:
    intent = parsed["intent"]

    if intent == "all_trajectories":
        return "Showing all float trajectories."

    if intent == "float_trajectory":
        return f"Showing trajectory for Float {parsed['float_id']}."

    if intent == "latest_profile":
        return (
            f"Showing latest {parsed['parameter']} profile "
            f"for Float {parsed['float_id']} (Cycle {parsed['cycle']})."
        )

    if intent == "compare_cycles":
        c1, c2 = parsed["compare_cycles"]
        return (
            f"Comparing {parsed['parameter']} between Cycle {c1} and Cycle {c2} "
            f"for Float {parsed['float_id']}."
        )

    if intent == "metric_for_cycle":
        return (
            f"Showing {parsed['parameter']} for Cycle {parsed['cycle']} "
            f"for Float {parsed['float_id']}."
        )

    return "Could not understand query. Try a guided prompt."


# -----------------------------
# QUERY EXPLANATION DATA
# -----------------------------
def get_query_explanation(parsed: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "intent": parsed["intent"],
        "float": parsed["float_id"],
        "parameter": parsed["parameter"],
        "cycle": parsed["cycle"],
        "compare_cycles": parsed["compare_cycles"],
        "confidence": parsed["confidence"],
        "reasoning": parsed["reasoning"],
    }