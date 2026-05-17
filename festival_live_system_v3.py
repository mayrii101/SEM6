import streamlit as st
import pandas as pd
import random
import serial
import time
import plotly.express as px
import plotly.graph_objects as go

from streamlit_autorefresh import st_autorefresh

# =========================================
# AUTO REFRESH
# =========================================

st_autorefresh(interval=2000, key="refresh")

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Festival Heatmap",
    layout="wide"
)

st.title("🎪 Smart Festival Crowd Heatmap")

# =========================================
# ESP32 CONNECTION
# =========================================

PORT = '/dev/cu.usbserial-0001'

try:
    esp32 = serial.Serial(PORT, 115200, timeout=1)
    time.sleep(2)
    connected = True

except BaseException:
    connected = False

# =========================================
# FESTIVAL ZONES
# =========================================

zones = {
    "MainStage": {
        "x1": 0,
        "x2": 40,
        "y1": 60,
        "y2": 100
    },

    "FoodCourt": {
        "x1": 60,
        "x2": 100,
        "y1": 60,
        "y2": 100
    },

    "ChillZone": {
        "x1": 0,
        "x2": 40,
        "y1": 0,
        "y2": 40
    },

    "Entrance": {
        "x1": 60,
        "x2": 100,
        "y1": 0,
        "y2": 40
    }
}

# =========================================
# INITIALIZE PEOPLE
# =========================================

TOTAL_PEOPLE = 200

if "people" not in st.session_state:

    st.session_state.people = []

    for i in range(TOTAL_PEOPLE):

        zone = random.choice(list(zones.keys()))

        area = zones[zone]

        st.session_state.people.append({

            "id": i,

            "zone": zone,

            "x": random.uniform(area["x1"], area["x2"]),

            "y": random.uniform(area["y1"], area["y2"])
        })

# =========================================
# INITIALIZE HISTORY
# =========================================

if "history" not in st.session_state:

    st.session_state.history = []

# =========================================
# REAL BRACELET
# =========================================

if "bracelet" not in st.session_state:

    st.session_state.bracelet = {
        "zone": "MainStage"
    }

# =========================================
# MOVE PEOPLE
# =========================================

for person in st.session_state.people:

    # Small movement
    person["x"] += random.uniform(-2, 2)
    person["y"] += random.uniform(-2, 2)

    # Keep inside map
    person["x"] = max(0, min(100, person["x"]))
    person["y"] = max(0, min(100, person["y"]))

    # Occasionally change zones
    if random.random() < 0.03:

        new_zone = random.choice(list(zones.keys()))

        area = zones[new_zone]

        person["zone"] = new_zone

        person["x"] = random.uniform(area["x1"], area["x2"])

        person["y"] = random.uniform(area["y1"], area["y2"])

# =========================================
# COUNT ZONES
# =========================================

zone_counts = {}

for zone in zones.keys():

    count = len([
        p for p in st.session_state.people
        if p["zone"] == zone
    ])

    zone_counts[zone] = count

# =========================================
# DETERMINE BRACELET STATUS
# =========================================

bracelet_zone = random.choice(list(zones.keys()))

people_in_zone = zone_counts[bracelet_zone]

if people_in_zone < 45:

    bracelet_state = "LOW"
    bracelet_color = "green"

elif people_in_zone < 55:

    bracelet_state = "MEDIUM"
    bracelet_color = "orange"

else:

    bracelet_state = "HIGH"
    bracelet_color = "red"

# =========================================
# SEND TO ESP32
# =========================================

if connected:

    esp32.write((bracelet_state + "\n").encode())

# =========================================
# SAVE HISTORY
# =========================================

st.session_state.history.append({

    "MainStage": zone_counts["MainStage"],
    "FoodCourt": zone_counts["FoodCourt"],
    "ChillZone": zone_counts["ChillZone"],
    "Entrance": zone_counts["Entrance"]
})

# Limit history size

if len(st.session_state.history) > 30:

    st.session_state.history.pop(0)

# =========================================
# CREATE MAP DATAFRAME
# =========================================

df = pd.DataFrame(st.session_state.people)

# =========================================
# LIVE FESTIVAL MAP
# =========================================

st.subheader("🗺️ Live Festival Map")

fig = px.scatter(

    df,

    x="x",
    y="y",

    color="zone",

    hover_data=["id"],

    width=900,
    height=600
)

fig.update_layout(

    xaxis_range=[0, 100],
    yaxis_range=[0, 100],

    title="Live Crowd Movement",

    showlegend=True
)

st.plotly_chart(fig, width='stretch')

# =========================================
# HISTORICAL ANALYTICS
# =========================================

st.subheader("📈 Historical Crowd Analytics")

history_df = pd.DataFrame(st.session_state.history)

fig2 = go.Figure()

for zone in history_df.columns:

    fig2.add_trace(

        go.Scatter(

            y=history_df[zone],

            mode='lines',

            name=zone
        )
    )

fig2.update_layout(

    title="Crowd Density Over Time",

    xaxis_title="Time",

    yaxis_title="People"
)

st.plotly_chart(fig2, use_container_width=True)

# =========================================
# BRACELET STATUS
# =========================================

st.subheader("📍 Real Bracelet")

st.write(f"Zone: **{bracelet_zone}**")

st.write(
    f"Status: :{bracelet_color}[{bracelet_state}]"
)

st.write(f"Nearby People: **{people_in_zone}**")

# =========================================
# ZONE STATUS
# =========================================

st.subheader("🔥 Zone Heat Levels")

for zone, count in zone_counts.items():

    if count < 30:

        st.success(f"{zone}: {count} people")

    elif count < 70:

        st.warning(f"{zone}: {count} people")

    else:

        st.error(f"{zone}: {count} people")
