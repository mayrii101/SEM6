import streamlit as st
import pandas as pd
import random
import serial
import time

from streamlit_autorefresh import st_autorefresh

# run program: streamlit run festival_live_system_v2.py

st_autorefresh(interval=3000, key="festivalrefresh")


st.set_page_config(
    page_title="Festival Crowd System",
    layout="wide"
)

st.title("🎪 Smart Festival Crowd Monitor")

# esp connectie

PORT = '/dev/cu.usbserial-0001'

try:
    esp32 = serial.Serial(PORT, 115200, timeout=1)
    time.sleep(2)
    connected = True

except BaseException:
    connected = False

# zones

zones = [
    "MainStage",
    "FoodCourt",
    "ChillZone",
    "Entrance"
]

# fake ppl

TOTAL_PEOPLE = 200

if "people" not in st.session_state:

    st.session_state.people = []

    for i in range(TOTAL_PEOPLE):

        st.session_state.people.append({
            "id": i,
            "zone": random.choice(zones)
        })

# armband initialize

if "bracelet" not in st.session_state:

    st.session_state.bracelet = {
        "id": 999,
        "zone": random.choice(zones)
    }

# ppl simulator

for person in st.session_state.people:

    # kans op beweging 20%
    if random.random() < 0.2:

        current_zone = person["zone"]

        # beweging

        if current_zone == "MainStage":

            next_zone = random.choices(
                zones,
                weights=[50, 20, 20, 10]
            )[0]

        else:

            next_zone = random.choice(zones)

        person["zone"] = next_zone

# beweging echte armband

if random.random() < 0.3:

    st.session_state.bracelet["zone"] = random.choice(zones)


zone_counts = {}

for zone in zones:
    zone_counts[zone] = 0

for person in st.session_state.people:

    zone_counts[person["zone"]] += 1

# state determination

bracelet_zone = st.session_state.bracelet["zone"]

people_in_zone = zone_counts[bracelet_zone]

if people_in_zone < 30:

    bracelet_state = "LOW"
    bracelet_color = "🟢"

elif people_in_zone < 70:

    bracelet_state = "MEDIUM"
    bracelet_color = "🟠"

else:

    bracelet_state = "HIGH"
    bracelet_color = "🔴"

# stuur naar esp

if connected:

    esp32.write((bracelet_state + "\n").encode())


# dashboard data
dashboard_data = []

for zone, count in zone_counts.items():

    if count < 30:

        status = "LOW"
        color = "🟢"

    elif count < 70:

        status = "MEDIUM"
        color = "🟠"

    else:

        status = "HIGH"
        color = "🔴"

    dashboard_data.append({
        "Zone": zone,
        "People": count,
        "Density": f"{color} {status}"
    })

df = pd.DataFrame(dashboard_data)


st.subheader("📊 Live Zone Status")

st.dataframe(df, width='stretch')

# heatmap

st.subheader("🔥 Festival Heatmap")

cols = st.columns(len(zones))

for i, item in enumerate(dashboard_data):

    with cols[i]:

        st.metric(
            label=item["Zone"],
            value=item["People"],
            delta=item["Density"]
        )

        if "HIGH" in item["Density"]:

            st.error("Crowded")

        elif "MEDIUM" in item["Density"]:

            st.warning("Busy")

        else:

            st.success("Comfortable")

# data echte armband

st.subheader("📍 Real Bracelet")

st.write(
    f"Current Zone: **{bracelet_zone}**"
)

st.write(
    f"Bracelet Status: {bracelet_color} **{bracelet_state}**"
)

st.write(
    f"Nearby People: **{people_in_zone}**"
)

# stats publiek

st.subheader("📈 Crowd Statistics")

total = sum(zone_counts.values())

largest_zone = max(zone_counts, key=zone_counts.get)

st.write(f"Total Visitors: **{total}**")

st.write(
    f"Busiest Zone: **{largest_zone}** "
    f"({zone_counts[largest_zone]} people)"
)

# connectie status

if connected:

    st.success("ESP32 Connected")

else:

    st.error("ESP32 Not Connected")
