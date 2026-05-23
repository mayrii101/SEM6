import streamlit as st
import pandas as pd
import random
import serial
import time
import requests

import plotly.express as px
import plotly.graph_objects as go

from streamlit_autorefresh import st_autorefresh

# =========================================
# AUTO REFRESH
# =========================================

st_autorefresh(interval=5000, key="refresh")

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(

    page_title="Festival Heatmap",

    layout="wide"
)

st.title("🎪 Smart Festival Crowd Heatmap")

# =========================================
# API
# =========================================

API_URL = "http://127.0.0.1:5000"

# =========================================
# ESP32 CONNECTION
# =========================================

PORT = '/dev/cu.usbserial-0001'

if "esp32" not in st.session_state:

    try:

        st.session_state.esp32 = serial.Serial(
            PORT,
            115200,
            timeout=1
        )

        time.sleep(2)

        st.session_state.connected = True

    except BaseException:

        st.session_state.connected = False

connected = st.session_state.connected

esp32 = st.session_state.get("esp32")

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
    },

    # ───────── Middle band (y: 40–60) ─────────

    "Amapiano Stage": {
        "x1": 0,
        "x2": 20,
        "y1": 40,
        "y2": 60
    },

    "Dancehall Stage": {
        "x1": 20,
        "x2": 40,
        "y1": 40,
        "y2": 60
    },

    "HipHop Stage": {
        "x1": 40,
        "x2": 60,
        "y1": 40,
        "y2": 60
    },

    "Notes Stage": {
        "x1": 60,
        "x2": 80,
        "y1": 40,
        "y2": 60
    },

    "Spotlight Stage": {
        "x1": 80,
        "x2": 100,
        "y1": 40,
        "y2": 60
    },

    # ───────── Extra facilities ─────────

    "FoodCourt South": {
        "x1": 40,
        "x2": 60,
        "y1": 60,
        "y2": 80
    },

    "FoodCourt North": {
        "x1": 40,
        "x2": 60,
        "y1": 80,
        "y2": 100
    },

    "Toilets West": {
        "x1": 40,
        "x2": 50,
        "y1": 0,
        "y2": 20
    },

    "Toilets East": {
        "x1": 50,
        "x2": 60,
        "y1": 0,
        "y2": 20
    }
}

# =========================================
# INITIALIZE PEOPLE
# =========================================

TOTAL_PEOPLE = 200

if "people" not in st.session_state:

    st.session_state.people = []

    for i in range(TOTAL_PEOPLE):

        zone = random.choice(
            list(zones.keys())
        )

        area = zones[zone]

        st.session_state.people.append({

            "id": i,

            "zone": zone,

            "x": random.uniform(
                area["x1"],
                area["x2"]
            ),

            "y": random.uniform(
                area["y1"],
                area["y2"]
            )
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

    person["x"] += random.uniform(-2, 2)

    person["y"] += random.uniform(-2, 2)

    person["x"] = max(
        0,
        min(100, person["x"])
    )

    person["y"] = max(
        0,
        min(100, person["y"])
    )

    # Change zones

    if random.random() < 0.03:

        new_zone = random.choice(
            list(zones.keys())
        )

        area = zones[new_zone]

        person["zone"] = new_zone

        person["x"] = random.uniform(
            area["x1"],
            area["x2"]
        )

        person["y"] = random.uniform(
            area["y1"],
            area["y2"]
        )

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
# BRACELET STATUS
# =========================================

bracelet_zone = random.choice(
    list(zones.keys())
)

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

    esp32.write(
        (bracelet_state + "\n").encode()
    )

# =========================================
# SAVE HISTORY
# =========================================

st.session_state.history.append({

    "MainStage":
        zone_counts["MainStage"],

    "FoodCourt":
        zone_counts["FoodCourt"],

    "ChillZone":
        zone_counts["ChillZone"],

    "Entrance":
        zone_counts["Entrance"],

    "Amapiano Stage":
        zone_counts["Amapiano Stage"],

    "Dancehall Stage":
        zone_counts["Dancehall Stage"],

    "HipHop Stage":
        zone_counts["HipHop Stage"],

    "Notes Stage":
        zone_counts["Notes Stage"],

    "Spotlight Stage":
        zone_counts["Spotlight Stage"],

    "FoodCourt South":
        zone_counts["FoodCourt South"],

    "Toilets West":
        zone_counts["Toilets West"],

    "Toilets East":
        zone_counts["Toilets East"],

    "FoodCourt North":
        zone_counts["FoodCourt North"]
})

if len(st.session_state.history) > 30:

    st.session_state.history.pop(0)

# =========================================
# LIVE FESTIVAL MAP
# =========================================

df = pd.DataFrame(
    st.session_state.people
)

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

st.plotly_chart(

    fig,

    width='stretch'
)

# =========================================
# HISTORICAL ANALYTICS
# =========================================

st.subheader("📈 Historical Crowd Analytics")

history_df = pd.DataFrame(
    st.session_state.history
)

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

st.plotly_chart(

    fig2,

    width='stretch'
)

# =========================================
# BRACELET STATUS
# =========================================

st.subheader("📍 Real Bracelet")

st.write(
    f"Zone: **{bracelet_zone}**"
)

st.write(
    f"Status: :{bracelet_color}[{bracelet_state}]"
)

st.write(
    f"Nearby People: **{people_in_zone}**"
)

# =========================================
# ZONE HEAT LEVELS
# =========================================

st.subheader("🔥 Zone Heat Levels")

for zone, count in zone_counts.items():

    if count < 30:

        st.success(
            f"{zone}: {count} people"
        )

    elif count < 70:

        st.warning(
            f"{zone}: {count} people"
        )

    else:

        st.error(
            f"{zone}: {count} people"
        )

# =========================================
# DISTRESS MESSAGES
# =========================================

st.subheader("🚨 Distress Messages")

try:

    distress_response = requests.get(

        f"{API_URL}/distress"
    )

    distress_messages = distress_response.json()

    if len(distress_messages) == 0:

        st.success(
            "No distress messages."
        )

    else:

        for alert in distress_messages:

            st.error(

                f'''
                NAME:
                {alert["Sender"]}

                ZONE:
                {alert["Zone"]}

                MESSAGE:
                {alert["Message"]}

                TIME:
                {alert["CreatedAT"]}
                '''
            )

except Exception as e:

    st.warning(
        f"Could not load distress messages: {e}"
    )

# =========================================
# CONNECTION STATUS
# =========================================

if connected:

    st.success(
        "ESP32 Connected"
    )

else:

    st.error(
        "ESP32 Not Connected"
    )
