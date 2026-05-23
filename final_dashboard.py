import streamlit as st
import pandas as pd
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


# FETCH LIVE PEOPLE


try:

    people_response = requests.get(

        f"{API_URL}/people"
    )

    people = people_response.json()

except Exception as e:

    st.error(
        f"Could not load people data: {e}"
    )

    st.stop()


# FETCH ZONE STATUS


try:

    zone_response = requests.get(

        f"{API_URL}/zone-status"
    )

    zones = zone_response.json()

except Exception as e:

    st.error(
        f"Could not load zone data: {e}"
    )

    st.stop()


# FETCH MESSAGES


try:

    distress_response = requests.get(

        f"{API_URL}/distress"
    )

    distress_messages = distress_response.json()

except BaseException:

    distress_messages = []


# LIVE FESTIVAL MAP


st.subheader("Live Festival Map")

df = pd.DataFrame(people)

fig = px.scatter(

    df,

    x="X",
    y="Y",

    color="ZoneName",

    hover_data=["ID"],

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


# HISTORICAL ANALYTICS


if "history" not in st.session_state:

    st.session_state.history = []


history_entry = {}

for zone in zones:

    history_entry[zone["Name"]] = \
        zone["CurrentCount"]

st.session_state.history.append(
    history_entry
)

if len(st.session_state.history) > 30:

    st.session_state.history.pop(0)

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


# SELECT BRACELET ZONE (niet meer gesimuleerd zelf kiezen)


zone_names = [

    z["Name"]

    for z in zones
]

bracelet_zone = st.selectbox(

    "Select Bracelet Zone",

    zone_names
)


# GET BRACELET STATE FROM API


selected_zone = next(

    z for z in zones

    if z["Name"] == bracelet_zone
)

bracelet_state = \
    selected_zone["DensityLevel"]

people_in_zone = \
    selected_zone["CurrentCount"]


# DETERMINE COLOR


if bracelet_state == "LOW":

    bracelet_color = "green"

elif bracelet_state == "MEDIUM":

    bracelet_color = "orange"

else:

    bracelet_color = "red"


# SEND TO ESP32


if connected:

    esp32.write(

        (bracelet_state + "\n").encode()
    )


# BRACELET STATUS


st.subheader("Real Bracelet")

st.write(
    f"Zone: **{bracelet_zone}**"
)

st.write(
    f"Status: :{bracelet_color}[{bracelet_state}]"
)

st.write(
    f"Nearby People: **{people_in_zone}**"
)

# ZONE HEAT LEVELS


st.subheader("Zone Heat Levels")

for zone in zones:

    name = zone["Name"]

    count = zone["CurrentCount"]

    density = zone["DensityLevel"]

    if density == "LOW":

        st.success(
            f"{name}: {count} people"
        )

    elif density == "MEDIUM":

        st.warning(
            f"{name}: {count} people"
        )

    else:

        st.error(
            f"{name}: {count} people"
        )


# DISTRESS MESSAGES


st.subheader("Distress Messages")

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


# CONNECTION STATUS (ESP32)


if connected:

    st.success(
        "ESP32 Connected"
    )

else:

    st.error(
        "ESP32 Not Connected"
    )
