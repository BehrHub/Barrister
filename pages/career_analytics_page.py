from __future__ import annotations
from html import escape
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from services.career_analytics_engine import build_career_analytics_from_workbook

@st.cache_data(show_spinner=False)
def load_cached_career_analytics(path: str, modified_ns: int) -> dict:
    _ = modified_ns
    root = Path(__file__).resolve().parents[1]
    return build_career_analytics_from_workbook(path, sector_map_path=root / "config" / "client_sector_map.json")

def metric(label: str, value: str, note: str="") -> str:
    return f'<div class="ca-card"><div class="ca-label">{escape(label)}</div><div class="ca-value">{escape(value)}</div><div class="ca-note">{escape(note)}</div></div>'

def css() -> None:
    st.markdown('''<style>
    .ca-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.65rem;margin:.6rem 0 1rem}
    .ca-records{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.65rem;margin-bottom:1rem}
    .ca-card{min-height:112px;padding:.85rem;border:1px solid #263b58;border-radius:15px;background:linear-gradient(145deg,rgba(20,34,55,.97),rgba(10,22,39,.97));box-shadow:0 10px 24px rgba(0,0,0,.18)}
    .ca-label{font-size:.67rem;font-weight:850;letter-spacing:.075em;text-transform:uppercase;color:#9fb1c8}.ca-value{margin:.42rem 0 .28rem;font-size:1.45rem;font-weight:900;color:#fff}.ca-note{font-size:.69rem;line-height:1.3;color:#9fb1c8}
    @media(max-width:900px){.ca-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.ca-records{grid-template-columns:repeat(2,minmax(0,1fr))}}
    @media(max-width:560px){.ca-grid,.ca-records{grid-template-columns:1fr}.ca-card{min-height:100px}}
    </style>''', unsafe_allow_html=True)

def dual_chart(frame: pd.DataFrame, x: str, height: int=360) -> None:
    if frame.empty: return
    fig=go.Figure(); fig.add_bar(x=frame[x],y=frame.events,name="Events"); fig.add_bar(x=frame[x],y=frame.revenue,name="Revenue",yaxis="y2")
    fig.update_layout(barmode="group",height=height,margin=dict(l=10,r=10,t=20,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#dbe7f5"),yaxis2=dict(overlaying="y",side="right",showgrid=False),legend=dict(orientation="h"))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

def render_career_analytics_page(master_path: str | Path) -> None:
    css(); path=Path(master_path); analytics=load_cached_career_analytics(str(path),path.stat().st_mtime_ns)
    st.markdown('<div class="section-title">CAREER ANALYTICS</div>',unsafe_allow_html=True)
    validation=analytics["validation"]
    if validation["validation_status"]!="PASSED":
        st.warning("Workbook validation mismatches detected")
        st.dataframe(pd.DataFrame(validation["validation_mismatches"]),hide_index=True,width="stretch")
    s=analytics["summary"]
    summary=[("Career Events",f"{s['career_events']:,}",f"Through Event #{s['highest_completed_event']}"),("Career Revenue",f"${s['career_revenue']:,.2f}","Confirmed Event revenue"),("Unique Clients",f"{s['unique_clients']:,}",f"{analytics['client_analytics']['repeat_clients']} repeat"),("Worked Days",f"{s['worked_days']:,}",f"{s['jurisdictions']} jurisdictions"),("Work Orders",f"{s['unique_work_orders']:,}","Unique nonblank WOs"),("Longest Streak",str(s['longest_business_day_streak']),f"Current: {s['current_business_day_streak']}"),("Avg / Paid Event",f"${s['average_revenue_paid_event']:,.2f}","Positive confirmed revenue"),("Career Score",f"{s['overall_score']:.1%}",f"Grade {s['career_grade']}")]
    st.markdown('<div class="ca-grid">'+''.join(metric(*x) for x in summary)+'</div>',unsafe_allow_html=True)
    st.subheader("12 Career Records"); st.markdown('<div class="ca-records">'+''.join(metric(r['title'],r['display_value'],r['context']) for r in analytics['career_records'])+'</div>',unsafe_allow_html=True)
    st.subheader("Record Board"); st.dataframe(pd.DataFrame(analytics["record_board"]),hide_index=True,width="stretch")
    st.subheader("Career Season Graph"); weekly=pd.DataFrame(analytics["weekly_series"]); dual_chart(weekly,"workweek");
    with st.expander("Weekly and MY_MONTH tables",expanded=False): st.dataframe(weekly,hide_index=True,width="stretch"); st.dataframe(pd.DataFrame(analytics["monthly_series"]),hide_index=True,width="stretch")
    st.subheader("Weekday Performance"); weekdays=pd.DataFrame(analytics["weekday_series"]); dual_chart(weekdays,"weekday",330); st.dataframe(weekdays,hide_index=True,width="stretch")
    c=analytics["client_analytics"]; st.subheader("Client Analytics"); st.markdown('<div class="ca-grid">'+''.join(metric(*x) for x in [("Total Clients",str(c['total_clients']),""),("Repeat Clients",str(c['repeat_clients']),f"{c['repeat_client_rate']:.1%}"),("One-Time Clients",str(c['one_time_clients']),""),("Average Visits",f"{c['average_visits_per_client']:.2f}","Per client")])+'</div>',unsafe_allow_html=True); st.dataframe(pd.DataFrame(c["ranked_clients"]),hide_index=True,width="stretch")
    t=analytics["territory_analytics"]; st.subheader("Territory and Dispatch"); st.markdown('<div class="ca-grid">'+''.join(metric(*x) for x in [("Jurisdictions",str(t['jurisdictions']),", ".join(t['jurisdiction_set'])),("Cities",str(t['cities']),""),("Most-Visited City",str(t['most_visited_city'].get('city','—')),f"{int(t['most_visited_city'].get('events',0))} Events"),("Jobs / Dispatch Day",f"{t['average_jobs_per_dispatch_day']:.2f}","")])+'</div>',unsafe_allow_html=True); st.dataframe(pd.DataFrame(t["sector_distribution"]),hide_index=True,width="stretch")
    st.subheader("Hall of Fame"); st.dataframe(pd.DataFrame(analytics["hall_of_fame"]),hide_index=True,width="stretch")
    score=analytics["scorecard"]; st.subheader("Scorecard"); st.metric("Overall Career Score",f"{score['overall_score']:.1%}",f"Grade {score['grade']}"); st.dataframe(pd.DataFrame(score["dimensions"]),hide_index=True,width="stretch")
    with st.expander("Financial status",expanded=False): st.json(analytics["financial_status"])
