import streamlit as st
import pandas as pd
import pydeck as pdk
import os

# --- Page Config ---
st.set_page_config(page_title="Map of Power Plants", layout="wide")
st.title("🗺️ Map of Renewable Power Plants in Denmark")

# --- Load Data ---

DATA_PATH = os.path.join(os.path.dirname(__file__), "renewable_power_plants_DK.csv")



if not os.path.exists(DATA_PATH):
    st.error("Power plant file not found. Please upload it to the correct path.")
    st.stop()

df = pd.read_csv(DATA_PATH)

# --- Filter out plants without location ---
df = df.dropna(subset=["lat", "lon"])

# Sidebar filters
st.sidebar.header("🔍 Filter Plants")

tech_options = df["technology"].dropna().unique().tolist()
selected_tech = st.sidebar.multiselect("Technology Type", tech_options, default=tech_options)

# Filter data
filtered_df = df[df["technology"].isin(selected_tech)]
# --- PyDeck Map ---
st.subheader(f"Showing {len(filtered_df)} plants")

# Updated color (green), larger bubbles
layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered_df,
    get_position='[lon, lat]',
    get_radius="electrical_capacity * 1000",  # Bigger bubbles
    get_fill_color="[34, 139, 34, 180]",     # Forest green, semi-transparent
    pickable=True,
    auto_highlight=True
)

# Cleaner map style
view_state = pdk.ViewState(
    latitude=56.2639,
    longitude=9.5018,
    zoom=6.5,  # Slight zoom in
    pitch=20, # Adds a bit of 3D perspective
    bearing=0
)

tooltip = {
    "html": "<b>{name}</b><br/>Tech: {technology}<br/>Capacity: {electrical_capacity} MW",
    "style": {"backgroundColor": "#2c3e50", "color": "white"}
}

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/outdoors-v11",  # Cleaner and greener
    layers=[layer],
    initial_view_state=view_state,
    tooltip=tooltip
))
