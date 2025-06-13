import pandas as pd
import os

print("🚀 Starting ETL...")

# Step 1: Load the data
try:
    plants = pd.read_csv("data/raw/renewable_power_plants_DK.csv")
    ts = pd.read_csv("data/raw/time_series_60min_singleindex_filtered.csv", index_col=0, parse_dates=True)
    print("✅ CSVs loaded")
except Exception as e:
    print("❌ Error loading CSVs:", e)
    exit()

# Step 2: Create plant category
try:
    plants["category"] = plants.apply(
        lambda row: f"{row['energy_source_level_2'].lower()}_{row['technology'].lower()}".replace(" ", "_"),
        axis=1
    )
    print("✅ Plant categories created")
except Exception as e:
    print("❌ Error creating categories:", e)
    exit()

# Step 3: Group installed capacity
try:
    installed_capacity = plants.groupby("category")["electrical_capacity"].sum()
    print("✅ Installed capacity calculated")
except Exception as e:
    print("❌ Error calculating installed capacity:", e)
    exit()

# Step 4: Time series mapping
mapping = {
    "wind_onshore": "DK_wind_onshore_generation_actual",
    "wind_offshore": "DK_wind_offshore_generation_actual",
    "solar_photovoltaic": "DK_solar_generation_actual"
}

# Step 5: Build KPI dataframe
try:
    kpi_df = pd.DataFrame(index=ts.index)
    for category, ts_column in mapping.items():
        if ts_column in ts.columns:
            kpi_df[f"{category}_generation"] = ts[ts_column]
            kpi_df[f"{category}_installed_capacity"] = installed_capacity.get(category, 0)
            kpi_df[f"{category}_capacity_factor"] = (
                kpi_df[f"{category}_generation"] / installed_capacity.get(category, 1)
            )
    print("✅ KPI DataFrame created")
except Exception as e:
    print("❌ Error creating KPI DataFrame:", e)
    exit()

# Step 6: Daily average
try:
    daily_kpis = kpi_df.resample("D").mean()
    print("✅ Daily KPI resampled")
    print(daily_kpis.head())
except Exception as e:
    print("❌ Error during resampling:", e)
    exit()

# Step 7: Save output
try:
    os.makedirs("data/processed", exist_ok=True)
    daily_kpis.to_csv("data/processed/kpis_by_category.csv")
    print("✅ KPIs saved to data/processed/kpis_by_category.csv")
except Exception as e:
    print("❌ Error saving CSV:", e)
    exit()


