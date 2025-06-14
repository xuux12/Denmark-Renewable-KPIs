import streamlit as st
import pandas as pd
import altair as alt
import os

# --- Page Config ---
st.set_page_config(
    page_title="Denmark Renewable KPIs",
    page_icon="🌱",
    layout="wide"
)

# --- Inject Theme CSS ---
def inject_theme_css(theme):
    if theme == "Light Mode":
        css = """
        html, body, [class*="main"] {
            font-family: 'Segoe UI', sans-serif;
            background-color: #e6f4ea;
        }
        h1, h2, h3 { color: #004d40 !important; }
        [data-testid="stSidebar"] {
            background-color: #e3f2fd;
            padding-top: 2rem;
        }
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        button[data-testid="baseButton-download"] {
            background-color: #00695c; color: white;
            border-radius: 10px; padding: 0.5em 1.5em;
        }
        button[data-testid="baseButton-download"]:hover {
            background-color: #004d40;
        }
        .stMetric label, .stDateInput label, .stSelectbox label {
            font-weight: bold;
        }
        """
    else:
        css = """
        html, body, [class*="main"] {
            font-family: 'Segoe UI', sans-serif;
            background-color: #1c1c2c;
            color: white;
        }
        h1, h2, h3 { color: #80cbc4 !important; }
        [data-testid="stSidebar"] {
            background-color: #1e1e2e;
            padding-top: 2rem;
        }
        .block-container {
            background-color: #1c1c2c;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        button[data-testid="baseButton-download"] {
            background-color: #26a69a;
            color: white;
            border-radius: 10px;
            padding: 0.5em 1.5em;
        }
        button[data-testid="baseButton-download"]:hover {
            background-color: #00897b;
        }
        .stMetric label, .stDateInput label, .stSelectbox label {
            font-weight: bold;
            color: white;
        }
        /* Expander white text */
        [data-testid="stExpander"] {
            color: white !important;
        }
        [data-testid="stExpander"] div {
            color: white !important;
        }
        """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Filter Options")

    theme = st.radio("🎨 Theme", ["Light Mode", "Dark Mode"], index=0)
    inject_theme_css(theme)

    energy_type = st.selectbox("Energy Source", [
        "wind_onshore", "wind_offshore", "solar_photovoltaic"])

    metric_type = st.selectbox("Metric", [
        "generation", "installed_capacity", "capacity_factor"])

    compare = st.checkbox("Enable Comparison")
    compare_energy = None
    if compare:
        compare_energy = st.selectbox("Compare With", [e for e in ["wind_onshore", "wind_offshore", "solar_photovoltaic"] if e != energy_type])

    DATA_PATH = "kpis.csv"

    if not os.path.exists(DATA_PATH):
        st.error("❌ KPI file not found. Please run the ETL pipeline first.")
        st.stop()

    df = pd.read_csv(DATA_PATH, parse_dates=["utc_timestamp"])
    df["utc_timestamp"] = df["utc_timestamp"].dt.tz_localize(None)
    df.set_index("utc_timestamp", inplace=True)

    min_date = df.index.min().date()
    max_date = df.index.max().date()
    default_start = max_date.replace(day=1)

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", default_start, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

# --- Data Filter ---
start_date = pd.to_datetime(start_date).tz_localize(None)
end_date = pd.to_datetime(end_date).tz_localize(None)
if start_date > end_date:
    st.error("⚠️ Start date must be before end date.")
    st.stop()

filtered_df = df.loc[start_date:end_date]
column = f"{energy_type}_{metric_type}"
y_label = {
    "generation": "Generation (MWh)",
    "installed_capacity": "Installed Capacity (MW)",
    "capacity_factor": "Capacity Factor (%)"
}.get(metric_type, column)

# --- Main Title ---
st.title("📈 Renewable Energy in Denmark")

# --- Chart ---
st.subheader(f"🔍 {column.replace('_', ' ').title()} Over Time")
base = alt.Chart(filtered_df.reset_index())
line = base.mark_line(color="#388e3c").encode(
    x=alt.X("utc_timestamp:T", title="Date"),
    y=alt.Y(f"{column}:Q", title=y_label),
    tooltip=["utc_timestamp:T", column]
)

if compare and compare_energy:
    compare_col = f"{compare_energy}_{metric_type}"
    line2 = base.mark_line(color="#1976d2").encode(
        x="utc_timestamp:T",
        y=compare_col,
        tooltip=["utc_timestamp:T", compare_col]
    )
    chart = line + line2
else:
    chart = line

st.altair_chart(chart, use_container_width=True)

# --- Metrics ---
st.subheader("🗓️ Date Range Summary")
col1, col2 = st.columns(2)
with col1:
    st.metric("Total MWh", f"{filtered_df[column].sum():,.2f}")
with col2:
    st.metric("Daily Avg MWh", f"{filtered_df[column].mean():,.2f}")

# --- YoY Analysis ---
st.subheader(" 📊 Year-over-Year (YoY) Analysis")
df_yoy = df[[column]].copy()
df_yoy["year"] = df_yoy.index.year
annual = df_yoy.groupby("year")[column].sum()
st.bar_chart(annual)

# --- Download & Data ---
csv = filtered_df[[column]].to_csv().encode("utf-8")
st.download_button("📅 Download CSV", csv, f"{column}_filtered.csv", "text/csv")

# --- Expanders with white text in dark mode ---
with st.expander("📄 Show raw KPI data"):
    st.dataframe(filtered_df[[column]].head())

with st.expander("📊 What do these metrics mean?"):
    st.markdown("""
    - **Generation**: Actual energy produced (MWh)
    - **Installed Capacity**: Total rated output (MW)
    - **Capacity Factor**: Actual / Potential output (%)
    """)
