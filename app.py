import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

BUILD = "Barrister Cloud v4 · Authoritative Data Backbone"

st.set_page_config(page_title="Barrister Cloud v4", page_icon="🚆", layout="wide")

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "barrister_timeline.csv"

st.markdown("""
<style>
.block-container{padding-top:1rem;max-width:1180px}
#MainMenu,footer,header{visibility:hidden}
.hero{padding:20px 22px;border-radius:28px;background:linear-gradient(135deg,#08111F,#0F172A);border:1px solid rgba(148,163,184,.18);margin-bottom:12px}
.kicker{color:#FACC15;font-size:.72rem;letter-spacing:.22em;font-weight:900;text-transform:uppercase}
.hero-title{font-size:clamp(2.4rem,8vw,5.4rem);font-weight:950;line-height:.84;letter-spacing:-.075em;margin-top:8px}
.version{display:inline-block;margin-top:12px;padding:6px 10px;border-radius:999px;background:rgba(91,127,215,.16);border:1px solid rgba(91,127,215,.34);color:#C7D2FE;font-size:.68rem;font-weight:900}
.metric-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:12px 0}
.mini{padding:12px;border-radius:18px;background:rgba(15,23,42,.78);border:1px solid rgba(148,163,184,.14)}
.mini b{display:block;font-size:1.55rem;line-height:1;font-weight:950}
.mini span{display:block;margin-top:5px;color:#AFC2D8;font-size:.63rem;letter-spacing:.12em;text-transform:uppercase;font-weight:800}
.section-title{margin:14px 0 9px;font-size:1.45rem;font-weight:950;letter-spacing:-.04em}
.route{position:relative;padding-left:16px}
.route:before{content:"";position:absolute;left:6px;top:34px;bottom:8px;width:4px;border-radius:99px;background:linear-gradient(#EF4444 0 33%,#38BDF8 33% 66%,#22C55E 66% 100%)}
.stop{display:grid;grid-template-columns:18px 1fr auto;gap:9px;align-items:center;padding:9px 11px;margin-bottom:6px;border-radius:15px;background:rgba(2,8,20,.48);border:1px solid rgba(148,163,184,.10)}
.dot{width:13px;height:13px;border-radius:99px;background:#38BDF8;box-shadow:0 0 16px #38BDF8}
.stop-client{font-weight:950;font-size:1.02rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.stop-status{color:#B8C9DD;font-size:.72rem;margin-top:2px}
.stop-num{color:#FACC15;font-weight:950;font-size:.78rem}
.client-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(142px,1fr));gap:9px}
.client-card{min-height:118px;padding:13px;border-radius:18px;background:rgba(2,8,20,.50);border:1px solid rgba(148,163,184,.12);display:flex;flex-direction:column;justify-content:space-between}
.client-name{font-size:1.02rem;font-weight:950;line-height:1.02;letter-spacing:-.035em}
.client-meta{color:#B8C9DD;font-size:.70rem;margin-top:5px}
.client-visits{color:#FACC15;font-size:1.38rem;font-weight:950;line-height:1;margin-top:12px}
@media(max-width:760px){.metric-strip{grid-template-columns:repeat(4,1fr);gap:6px}.mini{padding:10px 8px}.mini b{font-size:1.18rem}.mini span{font-size:.5rem}.client-grid{grid-template-columns:repeat(2,1fr)}}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_timeline():
    if not DATA_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(DATA_PATH)
    return df.sort_values("event_number")

timeline = load_timeline()

if timeline.empty:
    st.error("No timeline data found. Expected data/barrister_timeline.csv.")
    st.stop()

total_events = len(timeline)
unique_clients = timeline["client"].nunique()
completed = int((timeline["status"].astype(str).str.lower() == "completed").sum())
regions = timeline["state_region"].nunique()

latest = timeline.sort_values("event_number").iloc[-1]
client_counts = (
    timeline.groupby("client", as_index=False)
    .agg(Visits=("event_number", "count"), First=("event_number", "min"), Latest=("event_number", "max"))
    .sort_values(["Visits", "First"], ascending=[False, True])
)

st.markdown(f"""
<div class="hero">
  <div class="kicker">BARRISTER CLOUD · AGENT EINI</div>
  <div class="hero-title">Command Center</div>
  <div class="version">{BUILD} · Source rows: {total_events}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="metric-strip">
  <div class="mini"><b>{total_events}</b><span>Events</span></div>
  <div class="mini"><b>{unique_clients}</b><span>Clients</span></div>
  <div class="mini"><b>{completed}</b><span>Done</span></div>
  <div class="mini"><b>{regions}</b><span>Regions</span></div>
</div>
""", unsafe_allow_html=True)

tab_home, tab_journey, tab_clients, tab_upcoming, tab_finance = st.tabs(
    ["Home", "Journey", "Clients", "Upcoming", "Financials"]
)

with tab_home:
    st.markdown('<div class="section-title">Latest Event</div>', unsafe_allow_html=True)
    st.markdown(f"**#{int(latest.event_number)} · {latest.client}**  \n{latest.city}, {latest.state_region} · {latest.status}")

    by_state = timeline.groupby("state_region", as_index=False).size().rename(columns={"size":"Events"})
    fig = px.bar(by_state, x="Events", y="state_region", orientation="h", text="Events")
    fig.update_layout(height=280, margin=dict(l=4,r=4,t=10,b=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with tab_journey:
    st.markdown('<div class="section-title">Journey</div>', unsafe_allow_html=True)
    st.markdown('<div class="route">', unsafe_allow_html=True)

    for _, row in timeline.iterrows():
        st.markdown(f"""
        <div class="stop">
          <div class="dot"></div>
          <div>
            <div class="stop-client">{row.client}</div>
            <div class="stop-status">{row.city}, {row.state_region} · {row.status}</div>
          </div>
          <div class="stop-num">#{int(row.event_number)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with tab_clients:
    st.markdown('<div class="section-title">Clients</div>', unsafe_allow_html=True)
    st.markdown('<div class="client-grid">', unsafe_allow_html=True)

    for _, row in client_counts.iterrows():
        st.markdown(f"""
        <div class="client-card">
          <div>
            <div class="client-name">{row.Client}</div>
            <div class="client-meta">First #{int(row.First)} · Latest #{int(row.Latest)}</div>
          </div>
          <div class="client-visits">{int(row.Visits)} visit{"s" if int(row.Visits) != 1 else ""}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with tab_upcoming:
    st.markdown('<div class="section-title">Upcoming / Open Items</div>', unsafe_allow_html=True)
    open_items = timeline[timeline["status"].astype(str).str.lower() != "completed"]
    if open_items.empty:
        st.success("No non-completed items in imported source.")
    else:
        st.dataframe(open_items[["event_number","client","city","state_region","status","notes"]], use_container_width=True, hide_index=True)

with tab_finance:
    st.markdown('<div class="section-title">Financials</div>', unsafe_allow_html=True)
    money = timeline.copy()
    money["amount_numeric"] = pd.to_numeric(money["amount"], errors="coerce")
    known = money.dropna(subset=["amount_numeric"])

    f1, f2, f3 = st.columns(3)
    f1.metric("Known Revenue Rows", len(known))
    f2.metric("Known Total", f"${known['amount_numeric'].sum():,.2f}")
    f3.metric("Avg Known Event", f"${known['amount_numeric'].mean():,.2f}")

    by_region = known.groupby("state_region", as_index=False)["amount_numeric"].sum()
    fig = px.bar(by_region, x="state_region", y="amount_numeric", text="amount_numeric", title="Known Revenue by Region")
    fig.update_layout(height=320, margin=dict(l=4,r=4,t=40,b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.caption("1E / 2E / 3E exact efficiency model can now be rebuilt from this imported backbone plus final deltas.")
