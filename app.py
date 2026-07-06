import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Barrister Cloud", page_icon="🚆", layout="wide")

ROOT = Path(__file__).parent
TIMELINE_PATH = ROOT / "data" / "barrister_timeline.csv"

st.title("Barrister Cloud Dashboard")
st.caption("Cloud fallback — timeline-first version")

@st.cache_data
def load_timeline():
    df = pd.read_csv(TIMELINE_PATH)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values("event_number")
    return df

timeline = load_timeline()

st.header("Event Timeline")
st.warning("Current CSV is a cloud placeholder. Replace data/barrister_timeline.csv with the authoritative workbook export when available.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Events Loaded", len(timeline))
c2.metric("Unique Clients", timeline["client"].nunique())
c3.metric("States / Jurisdictions", timeline["state"].nunique())
c4.metric("Completed", int((timeline["status"] == "Completed").sum()))

with st.expander("Filters", expanded=True):
    f1, f2, f3 = st.columns(3)
    months = f1.multiselect("Month", sorted(timeline["month"].dropna().unique()), default=sorted(timeline["month"].dropna().unique()))
    states = f2.multiselect("State", sorted(timeline["state"].dropna().unique()), default=sorted(timeline["state"].dropna().unique()))
    search = f3.text_input("Client search", "")

filtered = timeline[
    timeline["month"].isin(months)
    & timeline["state"].isin(states)
]

if search:
    filtered = filtered[filtered["client"].str.contains(search, case=False, na=False)]

display = filtered.rename(columns={
    "event_number": "Event #",
    "date": "Date",
    "month": "Month",
    "client": "Client",
    "location": "Location",
    "state": "State",
    "status": "Status",
    "category": "Category",
    "notes": "Notes",
})

st.dataframe(
    display[["Event #", "Date", "Month", "Client", "Location", "State", "Status", "Category", "Notes"]],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Timeline Volume")
m1, m2 = st.columns(2)

with m1:
    by_month = filtered.groupby("month", as_index=False).size().rename(columns={"size": "Events"})
    st.plotly_chart(px.bar(by_month, x="month", y="Events", text="Events", title="Events by Month"), use_container_width=True)

with m2:
    by_state = filtered.groupby("state", as_index=False).size().rename(columns={"size": "Events"})
    st.plotly_chart(px.bar(by_state, x="state", y="Events", text="Events", title="Events by State"), use_container_width=True)

st.subheader("Client Frequency")
client_counts = filtered["client"].value_counts().reset_index()
client_counts.columns = ["Client", "Events"]
st.dataframe(client_counts, use_container_width=True, hide_index=True)

st.divider()
st.header("Financial Analytics")
st.caption("Next pass: reconnect 1E State Efficiency, 2E Monthly Efficiency, and 3E Career Efficiency after timeline import is stabilized.")
