import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from streamlit_autorefresh import st_autorefresh

# =========================================
# AUTO REFRESH
# =========================================

st_autorefresh(interval=5000, key="dashboardrefresh")

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(

    page_title="Festival Control Dashboard",

    layout="wide"
)

st.title("🎪 Festival Safety Dashboard")

# =========================================
# API URL
# =========================================

API_URL = "http://127.0.0.1:5000"

# =========================================
# GET LIVE ZONE DATA
# =========================================

response = requests.get(

    f"{API_URL}/zone-status"
)

zones = response.json()

# =========================================
# GET DISTRESS MESSAGES
# =========================================

distress_response = requests.get(

    f"{API_URL}/distress"
)

distress_messages = distress_response.json()

# =========================================
# ZONE TABLE
# =========================================

st.subheader("📊 Live Zone Status")

zone_df = pd.DataFrame(zones)

st.dataframe(

    zone_df,

    width='stretch'
)

# =========================================
# GENERATE HEATMAP POINTS
# =========================================

points = []

for zone in zones:

    count = zone["CurrentCount"]

    zone_name = zone["Name"]

    for i in range(count):

        if zone_name == "MainStage":

            x = px.data.iris().sepal_length.sample(1).values[0] * 5
            y = 70 + (i % 30)

        elif zone_name == "FoodCourt":

            x = 60 + (i % 30)
            y = 70 + (i % 30)

        elif zone_name == "ChillZone":

            x = 10 + (i % 30)
            y = 10 + (i % 30)

        else:

            x = 60 + (i % 30)
            y = 10 + (i % 30)

        points.append({

            "x": x,
            "y": y,
            "zone": zone_name
        })

heatmap_df = pd.DataFrame(points)

# =========================================
# LIVE HEATMAP
# =========================================

st.subheader("🔥 Live Festival Heatmap")

fig = px.density_heatmap(

    heatmap_df,

    x="x",
    y="y",

    nbinsx=25,
    nbinsy=25,

    width=900,
    height=600
)

st.plotly_chart(

    fig,

    width='stretch'
)

# =========================================
# ANALYTICS GRAPH
# =========================================

st.subheader("📈 Crowd Analytics")

analytics_data = []

for zone in zones:

    analytics_data.append({

        "Zone": zone["Name"],

        "People": zone["CurrentCount"]
    })

analytics_df = pd.DataFrame(analytics_data)

fig2 = px.bar(

    analytics_df,

    x="Zone",
    y="People",

    color="People"
)

st.plotly_chart(

    fig2,

    width='stretch'
)

# =========================================
# DISTRESS MESSAGES
# =========================================

st.subheader("🚨 Distress Messages")

if len(distress_messages) == 0:

    st.success(
        "No distress messages."
    )

else:

    for alert in distress_messages:

        st.error(

            f"""
            NAME: {alert['Sender']}

            ZONE: {alert['Zone']}

            MESSAGE:
            {alert['Message']}

            TIME:
            {alert['CreatedAT']}
            """
        )
