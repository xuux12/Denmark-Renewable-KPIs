import streamlit as st
import pandas as pd
import pydeck as pdk
import os

# --- Page Config ---
st.set_page_config(page_title="Map of Power Plants", layout="wide")
st.title("🗺️ Map of Renewable Power Plants in Denmark")

# --- Load Data ---
DATA_PATH = os.path.join(os.path.dirname(__file__), "renewable_power_plants_DK.csv")

# Show path info for debugging
st.write("📁 Looking for file at:", DATA_PATH)
st.write("✅ File exists:", os.path.exists(DATA_PATH))

if not os.path.exists(DATA_PATH):
    st.error("❌ Power plant file not found. Please upload it to: `dashboard/pages/renewable_power_plants_DK.csv`")
    st.stop()

# Read CSV
df = pd.read_csv(DATA_PATH)
st.write("✅ Data loaded. Preview:")
st.dataframe(df.head())  # Show first few rows
st.write("📋 Columns:", df.columns.tolist())

# --- Filter out plants without location ---
if "lat" not in df.columns or "lon" not in df.columns:
    st.error("❌ Your CSV must contain 'lat' and 'lon' columns.")
    st.stop()

df = df.dropna(subset=["lat", "lon"])

# Sidebar filters
st.sidebar.header("🔍 Filter Plants")

# Technology filter
if "technology" not in df.columns:
    st.error("❌ 'technology' column not found in CSV.")
    st.stop()

tech_options = df["technology"].dropna().unique().tolist()
selected_tech = st.sidebar.multiselect("Technology Type", tech_options, default=tech_options)

# Filter data
filtered_df = df[df["technology"].isin(selected_tech)]

# Debug filtered data
st.write("🔍 Selected technologies:", selected_tech)
st.write("📊 Filtered plants count:", len(filtered_df))

# --- PyDeck Map ---
st.subheader(f"Showing {len(filtered_df)} plants")

# Check for electrical_capacity column
if "electrical_capacity" not in filtered_df.columns:
    st.error("❌ 'electrical_capacity' column missing from your CSV.")
    st.stop()

layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered_df,
    get_position='[lon, lat]',
    get_radius="electrical_capacity * 1000",  # Bigger bubbles
    get_fill_color="[34, 139, 34, 180]",      # Forest green, semi-transparent
    pickable=True,
    auto_highlight=True
)

view_state = pdk.ViewState(
    latitude=filtered_df["lat"].mean() if not filtered_df.empty else 56.2639,
    longitude=filtered_df["lon"].mean() if not filtered_df.empty else 9.5018,
    zoom=6.5,
    pitch=20,
    bearing=0
)

tooltip = {
    "html": "<b>{name}</b><br/>Tech: {technology}<br/>Capacity: {electrical_capacity} MW",
    "style": {"backgroundColor": "#2c3e50", "color": "white"}
}

# Render map
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/outdoors-v11",
    layers=[layer],
    initial_view_state=view_state,
    tooltip=tooltip
))

