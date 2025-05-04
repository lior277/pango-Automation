import streamlit as st
import pandas as pd
import json
import os

LOG_PATH = "logs/discrepancies.json"

st.set_page_config(page_title="Weather Discrepancy Dashboard", layout="wide")
st.title("🌍 Weather Discrepancy Analysis Dashboard")

# Load data
def load_data(path):
    if not os.path.exists(path):
        st.warning("No discrepancy log file found.")
        return pd.DataFrame()

    with open(path, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data)

# Main
df = load_data(LOG_PATH)

if df.empty:
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filter Discrepancies")
cities = st.sidebar.multiselect("City", options=sorted(df.city_name.unique()), default=list(df.city_name.unique()))
severity = st.sidebar.multiselect("Severity", ["LOW", "MEDIUM", "HIGH", "CRITICAL"], default=["HIGH", "CRITICAL"])

# Compute severity on the fly (in case it wasn't logged)
def determine_severity(d):
    if d > 5:
        return "CRITICAL"
    elif d > 3:
        return "HIGH"
    elif d > 1:
        return "MEDIUM"
    return "LOW"

df["severity"] = df["temp_discrepancy"].apply(determine_severity)

# Apply filters
filtered = df[df.city_name.isin(cities) & df.severity.isin(severity)]

# Summary metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Cities Analyzed", len(df))
col2.metric("Filtered Cities", len(filtered))
col3.metric("Avg Temp Discrepancy", f"{filtered.temp_discrepancy.mean():.2f} °C")

# Charts
st.subheader("📊 Discrepancy Trends")
st.bar_chart(filtered.set_index("city_name")["temp_discrepancy"].sort_values(ascending=False))

st.subheader("🔢 Detailed Data Table")
st.dataframe(filtered.sort_values(by="temp_discrepancy", ascending=False), use_container_width=True)

# Export button
st.download_button("Download Filtered Data as CSV", data=filtered.to_csv(index=False), file_name="filtered_discrepancies.csv")
