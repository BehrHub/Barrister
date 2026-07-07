import streamlit as st
import pandas as pd
import plotly.express as px

BUILD = "Barrister Cloud v3 · Build 2026-07-07"

st.set_page_config(
    page_title="Barrister Cloud v3",
    page_icon="🚆",
    layout="wide",
)

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 2.25rem;
    max-width: 1180px;
}

html, body, [class*="css"] {
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.hero {
    padding: 20px 22px;
    border-radius: 28px;
    background:
        radial-gradient(circle at 18% 16%, rgba(91,127,215,.30), transparent 35%),
        radial-gradient(circle at 82% 28%, rgba(250,204,21,.12), transparent 34%),
        linear-gradient(135deg, #08111F, #0F172A);
    border: 1px solid rgba(148,163,184,.18);
    box-shadow: 0 20px 70px rgba(0,0,0,.28);
    margin-bottom: 14px;
}

.kicker {
    color: #FACC15;
    font-size: .72rem;
    letter-spacing: .22em;
    font-weight: 900;
    text-transform: uppercase;
}

.hero-title {
    font-size: clamp(2.55rem, 8vw, 5.8rem);
    font-weight: 950;
    line-height: .84;
    letter-spacing: -.075em;
    margin-top: 8px;
}

.hero-sub {
    color: #B8C9DD;
    margin-top: 10px;
    font-size: .98rem;
    max-width: 720px;
}

.version {
    display: inline-block;
    margin-top: 13px;
    padding: 6px 10px;
    border-radius: 999px;
    background: rgba(91,127,215,.16);
    border: 1px solid rgba(91,127,215,.34);
    color: #C7D2FE;
    font-size: .68rem;
    font-weight: 900;
    letter-spacing: .08em;
}

.metric-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
    margin: 12px 0 12px;
}

.mini-metric {
    padding: 12px 13px;
    border-radius: 18px;
    background: rgba(15,23,42,.78);
    border: 1px solid rgba(148,163,184,.14);
}

.mini-metric b {
    display: block;
    font-size: 1.55rem;
    line-height: 1;
    font-weight: 950;
    letter-spacing: -.04em;
}

.mini-metric span {
    display: block;
    margin-top: 5px;
    color: #AFC2D8;
    font-size: .63rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    font-weight: 800;
}

.card-grid {
    display: grid;
    grid-template-columns: 1.15fr 1fr 1fr;
    gap: 10px;
    margin-bottom: 14px;
}

.app-card {
    padding: 16px 17px;
    border-radius: 22px;
    background: rgba(15,23,42,.82);
    border: 1px solid rgba(148,163,184,.14);
    min-height: 132px;
    box-shadow: 0 16px 44px rgba(0,0,0,.20);
}

.card-title {
    font-size: 1.75rem;
    line-height: .95;
    font-weight: 950;
    letter-spacing: -.045em;
    margin-top: 7px;
}

.card-sub {
    color: #B8C9DD;
    font-size: .86rem;
    margin-top: 8px;
}

.pill {
    display: inline-block;
    margin-top: 10px;
    padding: 5px 9px;
    border-radius: 999px;
    background: rgba(250,204,21,.13);
    color: #FACC15;
    border: 1px solid rgba(250,204,21,.26);
    font-size: .62rem;
    font-weight: 900;
    letter-spacing: .09em;
    text-transform: uppercase;
}

.section-title {
    margin: 12px 0 9px;
    font-size: 1.45rem;
    font-weight: 950;
    letter-spacing: -.04em;
}

.route {
    position: relative;
    padding-left: 16px;
    margin-top: 4px;
}

.route:before {
    content: "";
    position: absolute;
    left: 6px;
    top: 34px;
    bottom: 8px;
    width: 4px;
    border-radius: 99px;
    background: linear-gradient(#EF4444 0 32%, #38BDF8 32% 68%, #22C55E 68% 100%);
    box-shadow: 0 0 20px rgba(56,189,248,.22);
}

.month-label {
    margin: 14px 0 7px;
    color: #FACC15;
    font-size: .68rem;
    letter-spacing: .18em;
    font-weight: 950;
}

.stop {
    position: relative;
    display: grid;
    grid-template-columns: 18px 1fr auto;
    align-items: center;
    gap: 9px;
    padding: 9px 11px;
    margin-bottom: 6px;
    border-radius: 15px;
    background: rgba(2,8,20,.48);
    border: 1px solid rgba(148,163,184,.10);
}

.dot {
    width: 13px;
    height: 13px;
    border-radius: 99px;
    box-shadow: 0 0 16px currentColor;
}

.april { background:#EF4444; color:#EF4444; }
.may { background:#38BDF8; color:#38BDF8; }
.june { background:#22C55E; color:#22C55E; }

.stop-client {
    font-weight: 950;
    font-size: 1.02rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.stop-status {
    color: #B8C9DD;
    font-size: .72rem;
    margin-top: 2px;
}

.stop-num {
    color: #FACC15;
    font-weight: 950;
    font-size: .78rem;
}

.client-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(142px, 1fr));
    gap: 9px;
}

.client-card {
    min-height: 128px;
    padding: 13px;
    border-radius: 18px;
    background: rgba(2,8,20,.50);
    border: 1px solid rgba(148,163,184,.12);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.client-name {
    font-size: 1.02rem;
    font-weight: 950;
    line-height: 1.02;
    letter-spacing: -.035em;
}

.client-meta {
    color: #B8C9DD;
    font-size: .70rem;
    margin-top: 5px;
}

.client-visits {
    color: #FACC15;
    font-size: 1.38rem;
    font-weight: 950;
    line-height: 1;
    margin-top: 12px;
}

.finance-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 9px;
}

.finance-card {
    padding: 13px;
    border-radius: 18px;
    background: rgba(2,8,20,.46);
    border: 1px solid rgba(148,163,184,.12);
}

.finance-card b {
    display: block;
    font-size: 1.28rem;
    line-height: 1;
}

.finance-card span {
    display: block;
    margin-top: 5px;
    color: #B8C9DD;
    font-size: .72rem;
}

@media(max-width: 760px) {
    .metric-strip { grid-template-columns: repeat(4, 1fr); gap: 6px; }
    .mini-metric { padding: 10px 8px; }
    .mini-metric b { font-size: 1.22rem; }
    .mini-metric span { font-size: .52rem; }
    .card-grid { grid-template-columns: 1fr; }
    .app-card { min-height: 116px; }
    .client-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
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

clients = pd.DataFrame([
    {"Client": "USDA", "Visits": 12},
    {"Client": "Joint Base Andrews", "Visits": 4},
    {"Client": "Macy's", "Visits": 3},
    {"Client": "Bloomingdale's", "Visits": 2},
    {"Client": "Verizon", "Visits": 2},
    {"Client": "HomeGoods", "Visits": 2},
    {"Client": "TJ Maxx", "Visits": 2},
    {"Client": "Dunkin'", "Visits": 2},
])

state_efficiency = pd.DataFrame([
    {"State": "Maryland", "Events": 30, "Avg Trip": 93.42, "Hourly": 42.98},
    {"State": "Washington, DC", "Events": 9, "Avg Trip": 176.34, "Hourly": 40.51},
    {"State": "Virginia", "Events": 6, "Avg Trip": 178.42, "Hourly": 43.69},
    {"State": "Pennsylvania", "Events": 3, "Avg Trip": 136.67, "Hourly": 48.24},
])

monthly = pd.DataFrame([
    {"Month": "April", "Events": 8, "Net": 1283.00, "Gross": 1832.86, "Net/Event": 160.38},
    {"Month": "May", "Events": 15, "Net": 1890.41, "Gross": 2700.59, "Net/Event": 126.03},
    {"Month": "June", "Events": 25, "Net": 2696.68, "Gross": 3852.40, "Net/Event": 107.87},
])

st.markdown(f"""
<div class="hero">
  <div class="kicker">BARRISTER CLOUD · AGENT EINI</div>
  <div class="hero-title">Command Center</div>
  <div class="hero-sub">Mobile-first cloud fallback focused on journey, clients, upcoming work, and efficiency.</div>
  <div class="version">{BUILD}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="metric-strip">
  <div class="mini-metric"><b>48</b><span>Events</span></div>
  <div class="mini-metric"><b>25</b><span>Clients</span></div>
  <div class="mini-metric"><b>14</b><span>Streak</span></div>
  <div class="mini-metric"><b>4</b><span>Regions</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card-grid">
  <div class="app-card">
    <div class="kicker">Next Stop</div>
    <div class="card-title">Dunkin'</div>
    <div class="card-sub">Kiosk / PED upgrade route</div>
    <div class="pill">Upcoming</div>
  </div>
  <div class="app-card">
    <div class="kicker">Latest Stop</div>
    <div class="card-title">HomeGoods</div>
    <div class="card-sub">TJX route expansion</div>
    <div class="pill">June Line</div>
  </div>
  <div class="app-card">
    <div class="kicker">Focus</div>
    <div class="card-title">Timeline First</div>
    <div class="card-sub">Journey and clients before finance polish.</div>
    <div class="pill">v3 Baseline</div>
  </div>
</div>
""", unsafe_allow_html=True)

tab_home, tab_journey, tab_clients, tab_upcoming, tab_finance = st.tabs(
    ["Home", "Journey", "Clients", "Upcoming", "Financials"]
)

with tab_home:
    st.markdown('<div class="section-title">Territory Snapshot</div>', unsafe_allow_html=True)
    fig = px.bar(
        state_efficiency,
        x="Events",
        y="State",
        orientation="h",
        text="Events",
        color="State",
    )
    fig.update_layout(
        height=295,
        showlegend=False,
        margin=dict(l=4, r=4, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_journey:
    st.markdown('<div class="section-title">Journey</div>', unsafe_allow_html=True)
    st.markdown('<div class="route">', unsafe_allow_html=True)

    for month_name in ["April", "May", "June"]:
        month_df = timeline[timeline["month"] == month_name]
        st.markdown(f'<div class="month-label">{month_name.upper()}</div>', unsafe_allow_html=True)

        for _, row in month_df.iterrows():
            klass = row["month"].lower()
            st.markdown(
                f"""
                <div class="stop">
                  <div class="dot {klass}"></div>
                  <div>
                    <div class="stop-client">{row["client"]}</div>
                    <div class="stop-status">{row["status"]}</div>
                  </div>
                  <div class="stop-num">#{int(row["event"])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)

with tab_clients:
    st.markdown('<div class="section-title">Clients</div>', unsafe_allow_html=True)
    st.markdown('<div class="client-grid">', unsafe_allow_html=True)

    for _, row in clients.sort_values(["Visits", "Client"], ascending=[False, True]).iterrows():
        visits = int(row["Visits"])
        label = "repeat client" if visits > 1 else "single stop"
        st.markdown(
            f"""
            <div class="client-card">
              <div>
                <div class="client-name">{row["Client"]}</div>
                <div class="client-meta">Barrister client · {label}</div>
              </div>
              <div class="client-visits">{visits} visit{"s" if visits != 1 else ""}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

with tab_upcoming:
    st.markdown('<div class="section-title">Upcoming</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="app-card">
      <div class="kicker">Next Active Route</div>
      <div class="card-title">Dunkin'</div>
      <div class="card-sub">Six kiosk / PED upgrade tickets. This section becomes the active work queue when source data is connected.</div>
      <div class="pill">Needs source data</div>
    </div>
    """, unsafe_allow_html=True)

with tab_finance:
    st.markdown('<div class="section-title">Financials</div>', unsafe_allow_html=True)

    st.markdown('<div class="finance-grid">', unsafe_allow_html=True)
    st.markdown("""
      <div class="finance-card"><b>.29</b><span>Career net / event</span></div>
      <div class="finance-card"><b>.70</b><span>Gross equivalent / event</span></div>
      <div class="finance-card"><b>.73</b><span>Career net / hour</span></div>
      <div class="finance-card"><b>,967</b><span>Gross salary pace</span></div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    f1, f2 = st.columns(2)

    with f1:
        fig = px.bar(
            state_efficiency,
            x="State",
            y="Avg Trip",
            text="Avg Trip",
            title="1E — Avg Trip by State",
        )
        fig.update_layout(height=310, margin=dict(l=4, r=4, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with f2:
        fig = px.line(
            monthly,
            x="Month",
            y=["Net", "Gross"],
            markers=True,
            title="2E — Monthly Net vs Gross",
        )
        fig.update_layout(height=310, margin=dict(l=4, r=4, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)
