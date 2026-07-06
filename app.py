import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Barrister Cloud", page_icon="🚆", layout="wide")

st.title("Barrister Cloud Dashboard")
st.caption("Cloud fallback — timeline shell first, finances second")

timeline = pd.DataFrame([
    ["2026-04", 1, "Macy's", "Fairfax, VA", "Completed", "Retail start"],
    ["2026-04", 2, "Bloomingdale's", "Tysons, VA", "Completed", "Retail / enterprise stop"],
    ["2026-04", 3, "Hampton Inn & Suites", "Washington, DC", "Completed", "Hospitality stop"],
    ["2026-04", 4, "Davis Polk & Wardwell", "Washington, DC", "Completed", "Enterprise / legal client"],
    ["2026-05", 5, "USDA", "Washington, DC", "Completed", "Federal cluster"],
    ["2026-05", 6, "Joint Base Andrews", "Camp Springs, MD", "Completed", "Multi-ticket Dynabook cluster"],
    ["2026-05", 7, "Verizon", "Maryland", "Completed", "Repeat client"],
    ["2026-06", 8, "TJ Maxx", "Rockville, MD", "Completed", "TJX route"],
    ["2026-06", 9, "HomeGoods", "Maryland", "Completed", "TJX route"],
    ["2026-06", 10, "Dunkin'", "Maryland", "Scheduled / Active", "Kiosk / PED upgrade route"],
], columns=["Month", "Event #", "Client", "Location", "Status", "Notes"])

st.header("Event Timeline")
st.warning("Timeline shell only — replace with authoritative workbook timeline when available.")

c1, c2, c3 = st.columns(3)
with c1:
    month_filter = st.multiselect("Month", sorted(timeline["Month"].unique()), default=sorted(timeline["Month"].unique()))
with c2:
    status_filter = st.multiselect("Status", sorted(timeline["Status"].unique()), default=sorted(timeline["Status"].unique()))
with c3:
    client_search = st.text_input("Client search", "")

filtered = timeline[
    timeline["Month"].isin(month_filter)
    & timeline["Status"].isin(status_filter)
]

if client_search:
    filtered = filtered[filtered["Client"].str.contains(client_search, case=False, na=False)]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Timeline Events Shown", len(filtered))
k2.metric("Unique Clients", filtered["Client"].nunique())
k3.metric("Months", filtered["Month"].nunique())
k4.metric("Completed", int((filtered["Status"] == "Completed").sum()))

st.dataframe(filtered, use_container_width=True, hide_index=True)

st.subheader("Timeline by Month")
fig = px.histogram(filtered, x="Month", color="Status", title="Events by Month")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Client Frequency")
client_counts = filtered["Client"].value_counts().reset_index()
client_counts.columns = ["Client", "Events"]
st.dataframe(client_counts, use_container_width=True, hide_index=True)

st.divider()
st.header("Financial Analytics — Holding Area")
st.caption("We will move the 1E / 2E / 3E financial sections back in after the authoritative timeline is stabilized.")
