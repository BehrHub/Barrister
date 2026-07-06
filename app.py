import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Barrister Cloud v2",
    page_icon="🚆",
    layout="wide",
)

st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2.5rem;
    max-width: 1180px;
}

[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(15,23,42,.96), rgba(8,17,31,.96));
    border: 1px solid rgba(148,163,184,.18);
    border-radius: 18px;
    padding: 14px 16px;
}

[data-testid="stMetricLabel"] {
    font-size: .72rem;
    color: #AFC2D8;
    text-transform: uppercase;
    letter-spacing: .12em;
}

[data-testid="stMetricValue"] {
    font-size: 1.85rem;
    font-weight: 900;
}

.hero {
    padding: 22px 24px;
    border-radius: 26px;
    background:
        radial-gradient(circle at 16% 18%, rgba(91,127,215,.24), transparent 34%),
        linear-gradient(135deg, #08111F, #0F172A);
    border: 1px solid rgba(148,163,184,.18);
    margin-bottom: 18px;
}

.hero-kicker {
    color: #FACC15;
    font-size: .75rem;
    letter-spacing: .22em;
    font-weight: 800;
}

.hero-title {
    font-size: clamp(2.4rem, 8vw, 5.4rem);
    font-weight: 950;
    line-height: .85;
    letter-spacing: -.07em;
    margin-top: 8px;
}

.card {
    padding: 18px 20px;
    border-radius: 24px;
    background: rgba(15,23,42,.84);
    border: 1px solid rgba(148,163,184,.16);
    box-shadow: 0 18px 50px rgba(0,0,0,.22);
    min-height: 140px;
}

.card-kicker {
    color: #FACC15;
    font-size: .72rem;
    letter-spacing: .18em;
    font-weight: 800;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.card-title {
    font-size: 2rem;
    font-weight: 900;
    letter-spacing: -.04em;
    line-height: 1;
}

.card-sub {
    color: #B8C9DD;
    margin-top: 8px;
    font-size: .95rem;
}

.pill {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(250,204,21,.14);
    color: #FACC15;
    border: 1px solid rgba(250,204,21,.26);
    font-size: .72rem;
    font-weight: 800;
    letter-spacing: .08em;
    margin-top: 12px;
}

.section-title {
    margin-top: 26px;
    margin-bottom: 10px;
    font-size: 1.45rem;
    font-weight: 900;
    letter-spacing: -.035em;
}

.client-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 12px;
    align-items: center;
    padding: 12px 14px;
    border-radius: 16px;
    background: rgba(2,8,20,.48);
    border: 1px solid rgba(148,163,184,.10);
    margin-bottom: 8px;
}

.client-name {
    font-weight: 900;
    font-size: 1.05rem;
}

.client-visits {
    color: #FACC15;
    font-weight: 900;
    font-size: 1.1rem;
}

.timeline-stop {
    display: grid;
    grid-template-columns: 28px 1fr;
    gap: 12px;
    margin-bottom: 12px;
}

.dot {
    width: 17px;
    height: 17px;
    border-radius: 99px;
    margin-top: 3px;
    box-shadow: 0 0 18px currentColor;
}

.dot.april { background: #EF4444; color: #EF4444; }
.dot.may { background: #38BDF8; color: #38BDF8; }
.dot.june { background: #22C55E; color: #22C55E; }

.stop-title {
    font-weight: 900;
}

.stop-meta {
    color: #B8C9DD;
    font-size: .86rem;
}

.small-note {
    color: #8EA3BA;
    font-size: .82rem;
}
</style>
""", unsafe_allow_html=True)

timeline = pd.DataFrame([
    {"event": 1, "month": "April", "client": "Macy's", "state": "Virginia", "status": "Completed"},
    {"event": 2, "month": "April", "client": "Bloomingdale's", "state": "Virginia", "status": "Completed"},
    {"event": 3, "month": "April", "client": "Hampton Inn & Suites", "state": "Washington, DC", "status": "Completed"},
    {"event": 4, "month": "April", "client": "Davis Polk & Wardwell", "state": "Washington, DC", "status": "Completed"},
    {"event": 5, "month": "May", "client": "USDA", "state": "Washington, DC", "status": "Completed"},
    {"event": 6, "month": "May", "client": "Joint Base Andrews", "state": "Maryland", "status": "Completed"},
    {"event": 7, "month": "May", "client": "Verizon", "state": "Maryland", "status": "Completed"},
    {"event": 8, "month": "June", "client": "TJ Maxx", "state": "Maryland", "status": "Completed"},
    {"event": 9, "month": "June", "client": "HomeGoods", "state": "Maryland", "status": "Completed"},
    {"event": 10, "month": "June", "client": "Dunkin'", "state": "Maryland", "status": "Upcoming"},
])

client_counts = pd.DataFrame([
    {"Client": "USDA", "Visits": 12},
    {"Client": "Joint Base Andrews", "Visits": 4},
    {"Client": "Macy's", "Visits": 3},
    {"Client": "Bloomingdale's", "Visits": 2},
    {"Client": "Verizon", "Visits": 2},
    {"Client": "HomeGoods", "Visits": 2},
    {"Client": "TJ Maxx", "Visits": 2},
    {"Client": "Dunkin'", "Visits": 2},
])

state_counts = pd.DataFrame([
    {"State": "Maryland", "Events": 30},
    {"State": "Washington, DC", "Events": 9},
    {"State": "Virginia", "Events": 6},
    {"State": "Pennsylvania", "Events": 3},
])

st.markdown("""
<div class="hero">
  <div class="hero-kicker">BARRISTER CLOUD · AGENT EINI</div>
  <div class="hero-title">Command Center</div>
  <div class="card-sub">Cloud fallback focused on journey, clients, upcoming work, and clean operational visibility.</div>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Events", "48")
m2.metric("Clients", "25")
m3.metric("Longest Streak", "14")
m4.metric("Regions", "4")

left, mid, right = st.columns([1.15, 1, 1])

with left:
    st.markdown("""
    <div class="card">
      <div class="card-kicker">Next Stop</div>
      <div class="card-title">Dunkin'</div>
      <div class="card-sub">Kiosk / PED upgrade route</div>
      <div class="pill">Upcoming</div>
    </div>
    """, unsafe_allow_html=True)

with mid:
    st.markdown("""
    <div class="card">
      <div class="card-kicker">Latest Stop</div>
      <div class="card-title">HomeGoods</div>
      <div class="card-sub">TJX route expansion</div>
      <div class="pill">June Line</div>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown("""
    <div class="card">
      <div class="card-kicker">Focus</div>
      <div class="card-title">Journey First</div>
      <div class="card-sub">Timeline and client structure before finance refinement.</div>
      <div class="pill">Cloud v2</div>
    </div>
    """, unsafe_allow_html=True)

tab_home, tab_journey, tab_clients, tab_upcoming, tab_finance = st.tabs(
    ["Home", "Journey", "Clients", "Upcoming", "Financials"]
)

with tab_home:
    st.markdown('<div class="section-title">Territory Snapshot</div>', unsafe_allow_html=True)
    fig = px.bar(
        state_counts,
        x="Events",
        y="State",
        orientation="h",
        text="Events",
        title=None,
    )
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with tab_journey:
    st.markdown('<div class="section-title">Journey</div>', unsafe_allow_html=True)
    st.caption("Placeholder route until authoritative workbook import.")
    for _, row in timeline.iterrows():
        klass = row["month"].lower()
        st.markdown(
            f"""
            <div class="timeline-stop">
              <div class="dot {klass}"></div>
              <div>
                <div class="stop-title">#{row['event']} · {row['client']}</div>
                <div class="stop-meta">{row['month']} · {row['state']} · {row['status']}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with tab_clients:
    st.markdown('<div class="section-title">Top Clients</div>', unsafe_allow_html=True)
    for _, row in client_counts.iterrows():
        st.markdown(
            f"""
            <div class="client-row">
              <div class="client-name">{row['Client']}</div>
              <div class="client-visits">{row['Visits']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with tab_upcoming:
    st.markdown('<div class="section-title">Upcoming</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
      <div class="card-kicker">Next Active Route</div>
      <div class="card-title">Dunkin'</div>
      <div class="card-sub">Six kiosk / PED upgrade tickets. This section will become the active work queue.</div>
      <div class="pill">Needs source data</div>
    </div>
    """, unsafe_allow_html=True)

with tab_finance:
    st.markdown('<div class="section-title">Financials Holding Area</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
      <div class="card-kicker">Coming Next</div>
      <div class="card-title">1E / 2E / 3E</div>
      <div class="card-sub">State Efficiency, Monthly Efficiency, and Career Efficiency will return after the timeline is cleaner.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="small-note">The cloud version is now structured for app-style refinement instead of report-style output.</div>', unsafe_allow_html=True)
