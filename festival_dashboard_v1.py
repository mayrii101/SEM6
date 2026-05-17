import streamlit as st
import pandas as pd
import random
import time
# run program: streamlit run festival_dashboard_v1.py

st.set_page_config(
    page_title="Festival Crowd Monitor",
    layout="wide"
)

st.title("🎪 Festival Crowd Dashboard")


# zones
zones = [
    "MainStage",
    "FoodCourt",
    "ChillZone",
    "Entrance"
]

# simulatie publiek

zone_data = []

for zone in zones:

    people = random.randint(0, 120)

    # hoeveelheid drukte
    if people < 30:
        status = "LOW"
        color = "🟢"

    elif people < 70:
        status = "MEDIUM"
        color = "🟠"

    else:
        status = "HIGH"
        color = "🔴"

    zone_data.append({
        "Zone": zone,
        "People": people,
        "Status": f"{color} {status}"
    })

# tabel display

df = pd.DataFrame(zone_data)

st.dataframe(df, width='stretch')


# eerste versie heatmap
st.subheader("Festival Heatmap")

cols = st.columns(len(zones))

for i, zone in enumerate(zone_data):

    with cols[i]:

        st.metric(
            label=zone["Zone"],
            value=zone["People"],
            delta=zone["Status"]
        )

        # Fake heat block
        if "HIGH" in zone["Status"]:
            st.error("Crowded")

        elif "MEDIUM" in zone["Status"]:
            st.warning("Busy")

        else:
            st.success("Comfortable")


time.sleep(5)

st.rerun()
