from __future__ import annotations
from html import escape
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from services.canonical_career_source import build_canonical_career_analytics

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

def render_career_analytics_page() -> None:
    css()
    root = Path(__file__).resolve().parents[1]

    try:
        analytics = build_canonical_career_analytics(root)
    except Exception:
        analytics = None

    st.markdown(
        '<div class="section-title">CAREER ANALYTICS</div>',
        unsafe_allow_html=True,
    )

    if analytics is None:
        master_path = root / "data" / "Barrister_Master.xlsx"
        detail_path = root / "data" / "current_master.xlsx"

        timeline = pd.read_excel(master_path, sheet_name="Timeline")
        service = pd.read_excel(detail_path, sheet_name="Service Events")

        def normalized(value: object) -> str:
            import re
            return re.sub(
                r"[^a-z0-9]+",
                "",
                str(value).casefold(),
            )

        def find_column(frame: pd.DataFrame, *aliases: str):
            lookup = {
                normalized(column): column
                for column in frame.columns
            }
            for alias in aliases:
                match = lookup.get(normalized(alias))
                if match is not None:
                    return match
            return None

        event_col = find_column(
            timeline,
            "Visit #",
            "Event #",
            "Event Number",
        )
        client_col = find_column(timeline, "Client", "Client Name")
        state_col = find_column(
            timeline,
            "State/Region",
            "State",
            "Jurisdiction",
        )
        status_col = find_column(timeline, "Status")

        detail_event = find_column(
            service,
            "Event #",
            "Event Number",
            "Visit #",
        )
        detail_client = find_column(service, "Client", "Client Name")
        detail_revenue = find_column(
            service,
            "Confirmed Revenue",
            "Revenue",
            "Amount",
        )
        detail_date = find_column(
            service,
            "Service Date",
            "Event Date",
            "Date",
        )

        completed = timeline.copy()
        if status_col is not None:
            completed = completed[
                completed[status_col]
                .fillna("")
                .astype(str)
                .str.casefold()
                .eq("completed")
            ].copy()

        event_numbers = pd.to_numeric(
            completed[event_col],
            errors="coerce",
        ).dropna() if event_col is not None else pd.Series(dtype=float)

        revenue = pd.Series(dtype=float)
        if detail_revenue is not None:
            revenue = pd.to_numeric(
                service[detail_revenue]
                .astype(str)
                .str.replace(r"[^0-9.\-]", "", regex=True),
                errors="coerce",
            )

        dates = (
            pd.to_datetime(service[detail_date], errors="coerce")
            if detail_date is not None
            else pd.Series(dtype="datetime64[ns]")
        )

        clients = (
            completed[client_col]
            .fillna("")
            .astype(str)
            .str.strip()
            if client_col is not None
            else pd.Series(dtype=str)
        )

        states = (
            completed[state_col]
            .fillna("")
            .astype(str)
            .str.strip()
            if state_col is not None
            else pd.Series(dtype=str)
        )

        summary_cards = [
            (
                "Career Events",
                f"{len(completed):,}",
                (
                    f"Through Event #{int(event_numbers.max())}"
                    if not event_numbers.empty
                    else "Timeline"
                ),
            ),
            (
                "Career Revenue",
                f"${float(revenue.sum()):,.2f}",
                "Confirmed Service Events revenue",
            ),
            (
                "Unique Clients",
                f"{clients[clients.ne('')].nunique():,}",
                "Completed chronology",
            ),
            (
                "Worked Days",
                f"{dates.dropna().dt.date.nunique():,}",
                f"{states[states.ne('')].nunique()} jurisdictions",
            ),
        ]

        st.markdown(
            '<div class="ca-grid">'
            + "".join(metric(*card) for card in summary_cards)
            + "</div>",
            unsafe_allow_html=True,
        )

        st.subheader("Top Clients")

        client_source = (
            service[detail_client]
            .fillna("")
            .astype(str)
            .str.strip()
            if detail_client is not None
            else pd.Series(dtype=str)
        )

        fallback = pd.DataFrame({
            "Client": client_source,
            "Revenue": revenue,
        })
        fallback = fallback[fallback["Client"].ne("")]

        if fallback.empty:
            st.info("No client financial records are available.")
        else:
            ranked = (
                fallback.groupby("Client", as_index=False)
                .agg(
                    Events=("Client", "size"),
                    Revenue=("Revenue", "sum"),
                )
                .sort_values(
                    ["Revenue", "Events"],
                    ascending=[False, False],
                )
            )
            st.dataframe(
                ranked,
                hide_index=True,
                use_container_width=True,
            )

        st.caption(
            "Career Analytics is using its live workbook fallback "
            "while detailed record calculations are unavailable."
        )
        return

    validation = analytics.get("validation", {})
    if validation.get("validation_status") not in {None, "PASSED"}:
        mismatches = validation.get("validation_mismatches", [])
        if mismatches:
            st.warning("Some detailed analytics require review.")

    summary = analytics["summary"]

    def whole(value: object) -> int:
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return 0

    def money(value: object) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    cards = [
        (
            "Career Events",
            f"{whole(summary.get('career_events')):,}",
            f"Through Event #{whole(summary.get('highest_completed_event'))}",
        ),
        (
            "Career Revenue",
            f"${money(summary.get('career_revenue')):,.2f}",
            "Confirmed revenue",
        ),
        (
            "Unique Clients",
            f"{whole(summary.get('unique_clients')):,}",
            f"{whole(analytics.get('client_analytics', {}).get('repeat_clients'))} repeat",
        ),
        (
            "Worked Days",
            f"{whole(summary.get('worked_days')):,}",
            f"{whole(summary.get('jurisdictions'))} jurisdictions",
        ),
        (
            "Work Orders",
            f"{whole(summary.get('unique_work_orders')):,}",
            "Unique nonblank WOs",
        ),
        (
            "Longest Streak",
            str(whole(summary.get("longest_business_day_streak"))),
            f"Current: {whole(summary.get('current_business_day_streak'))}",
        ),
        (
            "Avg / Paid Event",
            f"${money(summary.get('average_revenue_paid_event')):,.2f}",
            "Positive confirmed revenue",
        ),
        (
            "Career Score",
            f"{money(summary.get('overall_score')):.1%}",
            f"Grade {summary.get('career_grade', '—')}",
        ),
    ]

    st.markdown(
        '<div class="ca-grid">'
        + "".join(metric(*card) for card in cards)
        + "</div>",
        unsafe_allow_html=True,
    )

    records = analytics.get("career_records", [])
    if records:
        st.subheader("12 Career Records")
        st.markdown(
            '<div class="ca-records">'
            + "".join(
                metric(
                    str(record.get("title", "")),
                    str(record.get("display_value", "")),
                    str(record.get("context", "")),
                )
                for record in records
            )
            + "</div>",
            unsafe_allow_html=True,
        )

    sections = [
        ("Record Board", analytics.get("record_board", [])),
        ("Weekly Performance", analytics.get("weekly_series", [])),
        ("Monthly Performance", analytics.get("monthly_series", [])),
        ("Weekday Performance", analytics.get("weekday_series", [])),
        (
            "Client Analytics",
            analytics.get("client_analytics", {}).get(
                "ranked_clients",
                [],
            ),
        ),
        (
            "Territory and Dispatch",
            analytics.get("territory_analytics", {}).get(
                "sector_distribution",
                [],
            ),
        ),
        ("Hall of Fame", analytics.get("hall_of_fame", [])),
    ]

    for title, rows in sections:
        frame = pd.DataFrame(rows)
        if frame.empty:
            continue
        st.subheader(title)
        st.dataframe(
            frame,
            hide_index=True,
            use_container_width=True,
        )
