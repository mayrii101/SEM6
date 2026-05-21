import streamlit as st
import pandas as pd
import random
import serial
import time

from streamlit_autorefresh import st_autorefresh

# run program: streamlit run festival_live_system_v1.py
st_autorefresh(interval=5000, key="festivalrefresh")
st.set_page_config(
    page_title="Festival Crowd System",
    layout="wide"
)

st.title("🎪 Smart Festival Crowd Monitor")


# connect esp32

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

people = []

for i in range(TOTAL_PEOPLE):

    people.append({
        "id": i,
        "zone": random.choice(zones)
    })


# hardware(echte armband)

real_bracelet = {
    "id": 999,
    "zone": random.choice(zones)
}

# simulatie

for person in people:

    if random.random() < 0.3:
        person["zone"] = random.choice(zones)

# verander locatie echte armband

if random.random() < 0.5:
    real_bracelet["zone"] = random.choice(zones)


# zone logic

zone_counts = {}

for zone in zones:
    zone_counts[zone] = 0

for person in people:
    zone_counts[person["zone"]] += 1


# state armband

current_zone = real_bracelet["zone"]

people_in_zone = zone_counts[current_zone]

if people_in_zone < 45:
    bracelet_state = "LOW"
    bracelet_color = "🟢"

elif people_in_zone < 55:
    bracelet_state = "MEDIUM"
    bracelet_color = "🟠"

else:
    bracelet_state = "HIGH"
    bracelet_color = "🔴"

# stuur naar esp32

if connected:

    esp32.write((bracelet_state + "\n").encode())


# dashboard tabel


dashboard_data = []

for zone, count in zone_counts.items():

    if count < 45:
        status = "LOW"
        color = "🟢"

    elif count < 55:
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

st.subheader("📊 Zone Status")

st.dataframe(df, width='stretch')

# tabel

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

# status hardware


st.subheader("📍 Real Bracelet")

st.write(f"Current Zone: **{current_zone}**")

st.write(
    f"Bracelet Status: {bracelet_color} **{bracelet_state}**"
)

st.write(f"People Nearby: **{people_in_zone}**")

# connectie status debug

if connected:
    st.success("ESP32 Connected")

else:
    st.error("ESP32 Not Connected")
