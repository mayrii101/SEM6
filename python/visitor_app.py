import streamlit as st
import json
import random
import pandas as pd
import plotly.express as px

from streamlit_autorefresh import st_autorefresh

# =========================================
# AUTO REFRESH
# =========================================

st_autorefresh(interval=3000, key="visitorrefresh")

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Festival Visitor App",
    layout="wide"
)

st.title("🎪 Festival Crowd Viewer")

st.write(
    "Check crowded zones and stay safe."
)

# =========================================
# SIMULATED ZONES
# =========================================

zones = {
    "MainStage": random.randint(20, 100),
    "FoodCourt": random.randint(10, 80),
    "ChillZone": random.randint(5, 40),
    "Entrance": random.randint(5, 60)
}

# =========================================
# CREATE VISUAL MAP DATA
# =========================================

people = []

for zone, amount in zones.items():

    for i in range(amount):

        if zone == "MainStage":

            x = random.uniform(0, 40)
            y = random.uniform(60, 100)

        elif zone == "FoodCourt":

            x = random.uniform(60, 100)
            y = random.uniform(60, 100)

        elif zone == "ChillZone":

            x = random.uniform(0, 40)
            y = random.uniform(0, 40)

        else:

            x = random.uniform(60, 100)
            y = random.uniform(0, 40)

        people.append({
            "x": x,
            "y": y,
            "zone": zone
        })

df = pd.DataFrame(people)

# =========================================
# HEATMAP
# =========================================

st.subheader("🔥 Live Festival Heatmap")

fig = px.density_heatmap(

    df,

    x="x",
    y="y",

    nbinsx=20,
    nbinsy=20,

    width=900,
    height=600
)

st.plotly_chart(fig, width='stretch')

# =========================================
# DISTRESS MESSAGE FORM
# =========================================

st.subheader("🚨 Send Distress Message")

visitor_name = st.text_input("Your Name")

zone = st.selectbox(

    "Current Zone",

    list(zones.keys())
)

message = st.text_area(

    "Describe the situation"
)

if st.button("Send Alert"):

    new_alert = {

        "name": visitor_name,

        "zone": zone,

        "message": message
    }

    # Load existing messages

    with open(
        "distress_messages.json",
        "r"
    ) as file:

        alerts = json.load(file)

    # Add new message

    alerts.append(new_alert)

    # Save updated list

    with open(
        "distress_messages.json",
        "w"
    ) as file:

        json.dump(alerts, file, indent=4)

    st.success(
        "Alert sent to festival staff."
    )
