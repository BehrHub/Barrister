import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Barrister Cloud", page_icon="🚆", layout="wide")

st.title("Barrister Cloud Dashboard")
st.caption("Emergency cloud version — financial analytics baseline")

state = pd.DataFrame([
    ["Maryland", 30, 93.42, 42.98],
    ["Washington, DC", 9, 176.34, 40.51],
    ["Virginia", 6, 178.42, 43.69],
    ["Pennsylvania", 3, 136.67, 48.24],
], columns=["State", "Events", "Avg Net / Trip", "Net Hourly Rate"])

month = pd.DataFrame([
    ["April 2026", 8, 1283.00, 1832.86, 160.38, 229.11],
    ["May 2026", 15, 1890.41, 2700.59, 126.03, 180.04],
    ["June 2026", 25, 2696.68, 3852.40, 107.87, 154.10],
], columns=["Month", "Events", "Net Earned", "Gross Equivalent", "Net / Event", "Gross / Event"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Career Events", "48")
c2.metric("Avg Net / Event", "$122.29")
c3.metric("Avg Net / Hour", "$42.73")
c4.metric("Gross Salary Pace", "$126,967")

st.header("1E — State Efficiency")
st.dataframe(state, use_container_width=True, hide_index=True)
st.plotly_chart(px.bar(state, x="State", y="Avg Net / Trip", text="Avg Net / Trip"), use_container_width=True)

st.header("2E — Monthly Efficiency")
st.dataframe(month, use_container_width=True, hide_index=True)
st.plotly_chart(px.line(month, x="Month", y=["Net Earned", "Gross Equivalent"], markers=True), use_container_width=True)

st.header("3E — Career Efficiency")
st.markdown("""
- **48 events**
- **$122.29 net per event**
- **$174.70 gross equivalent per event**
- **$42.73 net per hour**
- **$126,967 gross salary pace**
""")
