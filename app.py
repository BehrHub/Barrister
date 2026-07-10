from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from datetime import date, datetime
from html import escape
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# =============================================================================
# BARRISTER CLOUD — SINGLE-FILE APPLICATION
# =============================================================================

APP_TITLE = "Barrister Dashboard"
BUILD_LABEL = "Barrister Cloud v5 · Single-File Stable Build"

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ASSETS_DIR = ROOT / "assets"
LOGO_DIRS = [
    ASSETS_DIR / "logos",
    ASSETS_DIR / "logo_factory" / "processed",
    ASSETS_DIR / "logo_factory" / "brand_icons",
]

SUPPORTED_REGIONS = ("MD", "VA", "DC", "PA", "WV", "DE")

CLIENT_ALIASES = {
    "Dunkin": "Dunkin'",
    "Dunkin’": "Dunkin'",
    "Baskin Robbins": "Baskin-Robbins",
    "Giant / Martin's": "Giant Food Stores",
    "Hilton Garden Inn DC": "Hilton Garden Inn",
    "Residential": "Residential – Annapolis Neck, MD",
    "Maryland Baptist Age Home": "MD Baptist Age Home",
    "Hebrew Home GW": "Hebrew Home of Greater Washington",
}

JURISDICTION_META = {
    "Maryland": {"code": "MD", "icon": "🦀", "color": "#db5a63", "depth": "#7d2f37"},
    "Washington, D.C.": {"code": "DC", "icon": "🏛️", "color": "#e0aa3e", "depth": "#7c591e"},
    "Virginia": {"code": "VA", "icon": "❤️", "color": "#5b8def", "depth": "#2b4f91"},
    "Pennsylvania": {"code": "PA", "icon": "🔔", "color": "#57ba80", "depth": "#286a46"},
    "West Virginia": {"code": "WV", "icon": "⛰️", "color": "#a78bfa", "depth": "#5b3aa8"},
    "Delaware": {"code": "DE", "icon": "💎", "color": "#38bdf8", "depth": "#176487"},
    "Other": {"code": "—", "icon": "📍", "color": "#94a3b8", "depth": "#475569"},
}


# =============================================================================
# PAGE + GLOBAL STYLE
# =============================================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #07111f;
        --panel: #0d1b2d;
        --panel-2: #101f34;
        --line: rgba(148, 163, 184, .16);
        --muted: #9eb0c4;
        --text: #f8fafc;
        --teal: #2dd4bf;
        --gold: #facc15;
        --blue: #5b8def;
        --red: #ef4444;
    }

    html, body, [class*="css"] {
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 9% 4%, rgba(37, 99, 235, .10), transparent 30%),
            linear-gradient(145deg, #07101d 0%, #091526 55%, #06101c 100%);
        color: var(--text);
    }

    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"] {
        display: none !important;
    }

    .block-container {
        width: 100%;
        max-width: 1460px;
        padding-top: 1rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3 {
        letter-spacing: -.04em;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 24px 26px;
        border-radius: 30px;
        border: 1px solid rgba(91, 141, 239, .26);
        background:
            radial-gradient(circle at 14% 15%, rgba(45, 212, 191, .16), transparent 34%),
            radial-gradient(circle at 84% 25%, rgba(91, 141, 239, .18), transparent 31%),
            linear-gradient(135deg, rgba(8, 17, 31, .98), rgba(15, 31, 53, .98));
        box-shadow: 0 26px 80px rgba(0, 0, 0, .30);
        margin-bottom: 12px;
    }

    .hero::after {
        content: "";
        position: absolute;
        inset: auto -8% -48% 36%;
        height: 230px;
        border-radius: 50%;
        border: 28px solid rgba(91, 141, 239, .06);
        transform: rotate(-8deg);
    }

    .hero-kicker {
        position: relative;
        z-index: 1;
        color: var(--teal);
        font-size: .70rem;
        letter-spacing: .22em;
        font-weight: 900;
        text-transform: uppercase;
    }

    .hero-title {
        position: relative;
        z-index: 1;
        margin-top: 8px;
        font-size: clamp(2.7rem, 8vw, 6.2rem);
        line-height: .82;
        font-weight: 950;
        letter-spacing: -.075em;
    }

    .hero-sub {
        position: relative;
        z-index: 1;
        max-width: 760px;
        margin-top: 13px;
        color: #b7c7d9;
        font-size: .92rem;
    }

    .build-pill {
        position: relative;
        z-index: 1;
        display: inline-flex;
        align-items: center;
        gap: 7px;
        margin-top: 14px;
        padding: 7px 11px;
        border-radius: 999px;
        border: 1px solid rgba(91, 141, 239, .35);
        background: rgba(91, 141, 239, .13);
        color: #c9d7ff;
        font-size: .66rem;
        font-weight: 900;
        letter-spacing: .06em;
    }

    .metric-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 9px;
        margin: 13px 0;
    }

    .metric-cell {
        padding: 15px 16px;
        border-radius: 22px;
        border: 1px solid var(--line);
        background: linear-gradient(180deg, rgba(15, 30, 51, .95), rgba(9, 21, 37, .95));
        box-shadow: 0 12px 34px rgba(0, 0, 0, .18);
    }

    .metric-cell b {
        display: block;
        font-size: clamp(1.45rem, 4vw, 2.25rem);
        line-height: 1;
        font-weight: 950;
        letter-spacing: -.045em;
    }

    .metric-cell span {
        display: block;
        margin-top: 7px;
        color: #a8b9cc;
        font-size: .59rem;
        font-weight: 900;
        letter-spacing: .16em;
        text-transform: uppercase;
    }

    .section-kicker {
        color: var(--teal);
        font-size: .66rem;
        font-weight: 900;
        letter-spacing: .18em;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    .section-title {
        font-size: clamp(1.7rem, 5vw, 2.8rem);
        font-weight: 950;
        line-height: .93;
        letter-spacing: -.055em;
        margin: 0 0 12px;
    }

    .spotlight-grid {
        display: grid;
        grid-template-columns: 1.2fr 1fr 1fr;
        gap: 10px;
        margin: 11px 0 18px;
    }

    .spotlight {
        min-height: 146px;
        padding: 17px 18px;
        border-radius: 23px;
        border: 1px solid var(--line);
        background:
            radial-gradient(circle at 90% 10%, rgba(45, 212, 191, .09), transparent 35%),
            rgba(12, 27, 47, .88);
        box-shadow: 0 14px 40px rgba(0, 0, 0, .19);
    }

    .spotlight-label {
        color: var(--gold);
        font-size: .63rem;
        font-weight: 900;
        letter-spacing: .17em;
        text-transform: uppercase;
    }

    .spotlight-title {
        margin-top: 8px;
        font-size: 1.55rem;
        font-weight: 950;
        line-height: .96;
        letter-spacing: -.04em;
    }

    .spotlight-meta {
        margin-top: 9px;
        color: var(--muted);
        font-size: .80rem;
        line-height: 1.35;
    }

    .status-pill {
        display: inline-flex;
        margin-top: 12px;
        padding: 5px 9px;
        border-radius: 999px;
        border: 1px solid rgba(45, 212, 191, .28);
        background: rgba(45, 212, 191, .11);
        color: #8ff6e8;
        font-size: .58rem;
        font-weight: 900;
        letter-spacing: .10em;
        text-transform: uppercase;
    }

    .timeline {
        position: relative;
        margin-top: 8px;
        padding-left: 32px;
    }

    .timeline::before {
        content: "";
        position: absolute;
        left: 11px;
        top: 5px;
        bottom: 5px;
        width: 5px;
        border-radius: 999px;
        background: linear-gradient(#ef4444 0 30%, #38bdf8 30% 66%, #22c55e 66% 100%);
        box-shadow: 0 0 22px rgba(56, 189, 248, .19);
    }

    .month-tag {
        position: relative;
        display: inline-flex;
        margin: 16px 0 9px -4px;
        padding: 6px 10px;
        border-radius: 999px;
        color: var(--gold);
        background: rgba(250, 204, 21, .09);
        border: 1px solid rgba(250, 204, 21, .20);
        font-size: .62rem;
        font-weight: 900;
        letter-spacing: .16em;
        text-transform: uppercase;
    }

    .timeline-row {
        position: relative;
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 10px;
        align-items: center;
        padding: 11px 13px;
        margin-bottom: 7px;
        border-radius: 17px;
        border: 1px solid rgba(148, 163, 184, .11);
        background: rgba(8, 20, 35, .74);
    }

    .timeline-row::before {
        content: "";
        position: absolute;
        left: -27px;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: var(--teal);
        border: 4px solid #0a1728;
        box-shadow: 0 0 17px rgba(45, 212, 191, .75);
    }

    .timeline-client {
        font-size: .97rem;
        font-weight: 900;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .timeline-meta {
        margin-top: 3px;
        color: var(--muted);
        font-size: .69rem;
    }

    .event-number {
        color: var(--gold);
        font-size: .72rem;
        font-weight: 950;
    }

    .client-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(178px, 1fr));
        gap: 10px;
    }

    .client-card {
        min-height: 152px;
        padding: 14px;
        border-radius: 20px;
        border: 1px solid rgba(148, 163, 184, .13);
        background: linear-gradient(180deg, rgba(16, 31, 53, .88), rgba(8, 20, 35, .88));
        box-shadow: 0 12px 34px rgba(0, 0, 0, .16);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .client-logo {
        height: 52px;
        display: flex;
        align-items: center;
        margin-bottom: 11px;
    }

    .client-logo img {
        max-width: 100%;
        max-height: 52px;
        object-fit: contain;
        object-position: left center;
        filter: drop-shadow(0 4px 10px rgba(0,0,0,.18));
    }

    .client-initials {
        width: 48px;
        height: 48px;
        display: grid;
        place-items: center;
        border-radius: 15px;
        background: rgba(91, 141, 239, .14);
        border: 1px solid rgba(91, 141, 239, .28);
        color: #d5e1ff;
        font-weight: 950;
    }

    .client-name {
        font-size: 1rem;
        font-weight: 950;
        line-height: 1.02;
        letter-spacing: -.03em;
    }

    .client-detail {
        margin-top: 5px;
        color: var(--muted);
        font-size: .68rem;
        line-height: 1.3;
    }

    .client-count {
        margin-top: 13px;
        color: var(--gold);
        font-size: 1.35rem;
        line-height: 1;
        font-weight: 950;
    }

    .upcoming-list {
        display: grid;
        gap: 9px;
    }

    .upcoming-card {
        padding: 15px 16px;
        border-radius: 20px;
        border: 1px solid rgba(148, 163, 184, .13);
        background:
            radial-gradient(circle at 95% 12%, rgba(91, 141, 239, .12), transparent 33%),
            rgba(12, 27, 47, .86);
    }

    .upcoming-date {
        color: var(--gold);
        font-size: .62rem;
        font-weight: 900;
        letter-spacing: .14em;
        text-transform: uppercase;
    }

    .upcoming-client {
        margin-top: 6px;
        font-size: 1.2rem;
        font-weight: 950;
        letter-spacing: -.035em;
    }

    .upcoming-meta {
        margin-top: 5px;
        color: var(--muted);
        font-size: .76rem;
    }

    .finance-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(205px, 1fr));
        gap: 10px;
        margin-bottom: 16px;
    }

    .finance-card {
        padding: 15px;
        border-radius: 19px;
        border: 1px solid rgba(148, 163, 184, .13);
        background: rgba(13, 29, 50, .82);
    }

    .finance-value {
        font-size: 1.43rem;
        font-weight: 950;
        letter-spacing: -.035em;
    }

    .finance-label {
        margin-top: 5px;
        color: var(--muted);
        font-size: .65rem;
        font-weight: 900;
        letter-spacing: .10em;
        text-transform: uppercase;
    }

    .output-card {
        padding: 15px;
        border-radius: 19px;
        border: 1px solid rgba(148, 163, 184, .13);
        background: rgba(13, 29, 50, .82);
        margin-bottom: 9px;
    }

    .source-note {
        margin-top: 14px;
        padding: 11px 13px;
        border-radius: 15px;
        background: rgba(91, 141, 239, .09);
        border: 1px solid rgba(91, 141, 239, .18);
        color: #b9c9dc;
        font-size: .68rem;
        word-break: break-word;
    }

    [data-baseweb="tab-list"] {
        gap: .55rem;
        border-bottom: 1px solid rgba(148, 163, 184, .18);
    }

    button[data-baseweb="tab"] {
        font-size: .86rem;
        font-weight: 800;
        padding-left: .35rem;
        padding-right: .35rem;
    }

    @media (max-width: 760px) {
        .block-container { padding-left: .88rem; padding-right: .88rem; }
        .hero { padding: 20px 18px; border-radius: 25px; }
        .metric-strip { gap: 6px; }
        .metric-cell { padding: 12px 9px; border-radius: 18px; }
        .metric-cell b { font-size: 1.30rem; }
        .metric-cell span { font-size: .49rem; }
        .spotlight-grid { grid-template-columns: 1fr; }
        .client-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
        .client-card { min-height: 137px; padding: 12px; }
        .client-logo, .client-logo img { height: 43px; max-height: 43px; }
        .client-name { font-size: .88rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# DATA CONTRACT
# =============================================================================

@dataclass
class DataBundle:
    timeline: pd.DataFrame
    pipeline: pd.DataFrame
    ledger: pd.DataFrame
    source: Path | None
    source_kind: str
    warnings: list[str]


CANONICAL_TIMELINE_COLUMNS = [
    "event_number",
    "date",
    "month",
    "client",
    "city",
    "region_code",
    "state_region",
    "status",
    "notes",
    "work_order",
    "ticket_number",
    "revenue",
    "ach",
    "expected",
    "variance",
    "payment_status",
]

CANONICAL_PIPELINE_COLUMNS = [
    "event_number",
    "date",
    "client",
    "city",
    "region_code",
    "state_region",
    "status",
    "notes",
    "work_order",
    "ticket_number",
]


def clean_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def text(value: object, fallback: str = "") -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return fallback
    result = str(value).strip()
    return result if result else fallback


def numeric(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.replace("$", "").replace(",", "").strip()
        if not value:
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def canonical_client(value: object) -> str:
    client = re.sub(r"\s+", " ", text(value, "Unknown Client"))
    if client.startswith("USDA Day"):
        return "USDA"
    if client.startswith("Under Armour Day"):
        return "Under Armour"
    return CLIENT_ALIASES.get(client, client)


def compact_region_code(value: object) -> str:
    raw = text(value).upper().replace(".", "")
    normalized = re.sub(r"[^A-Z]+", " ", raw).strip()

    if not normalized:
        return ""
    if normalized.startswith("DC") or "DISTRICT OF COLUMBIA" in normalized or normalized == "WASHINGTON D C":
        return "DC"
    if normalized.startswith("MD") or normalized == "MARYLAND":
        return "MD"
    if normalized.startswith("VA") or normalized == "VIRGINIA":
        return "VA"
    if normalized.startswith("PA") or normalized == "PENNSYLVANIA":
        return "PA"
    if normalized.startswith("WV") or normalized == "WEST VIRGINIA":
        return "WV"
    if normalized.startswith("DE") or normalized == "DELAWARE":
        return "DE"
    return normalized.split()[0] if normalized else ""


def jurisdiction_name(region_code: object, state_region: object = "") -> str:
    code = compact_region_code(region_code) or compact_region_code(state_region)
    return {
        "MD": "Maryland",
        "VA": "Virginia",
        "DC": "Washington, D.C.",
        "PA": "Pennsylvania",
        "WV": "West Virginia",
        "DE": "Delaware",
    }.get(code, "Other")


def split_location(value: object) -> tuple[str, str]:
    raw = re.sub(r"\s+", " ", text(value))
    if "," not in raw:
        return raw, ""
    city, state = raw.rsplit(",", 1)
    return city.strip(), compact_region_code(state)


def standardize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    renamed = frame.copy()
    renamed.columns = [clean_key(column) for column in renamed.columns]
    return renamed


def first_present(row: dict[str, Any], names: Iterable[str], fallback: object = "") -> object:
    for name in names:
        key = clean_key(name)
        if key in row:
            candidate = row.get(key)
            if candidate is not None and text(candidate):
                return candidate
    return fallback


def empty_frame(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def normalize_timeline(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        return empty_frame(CANONICAL_TIMELINE_COLUMNS)

    normalized = standardize_columns(frame)
    records: list[dict[str, Any]] = []

    for index, raw_row in enumerate(normalized.to_dict("records"), start=1):
        event_number = first_present(
            raw_row,
            ["event_number", "visit_number", "visit", "visit_no", "visit_#", "event", "event_#"],
            index,
        )

        client = canonical_client(first_present(raw_row, ["client", "client_name", "customer"]))

        city = text(first_present(raw_row, ["city", "location_city"]))
        region = compact_region_code(
            first_present(raw_row, ["region_code", "state", "state_code", "region"])
        )
        location = first_present(raw_row, ["location", "site", "address"])

        if location and (not city or not region):
            parsed_city, parsed_region = split_location(location)
            city = city or parsed_city
            region = region or parsed_region

        state_region = text(
            first_present(raw_row, ["state_region", "state_name", "jurisdiction"])
        )
        state_region = jurisdiction_name(region, state_region)

        status = text(first_present(raw_row, ["status", "event_status"]), "Completed").title()
        event_date = pd.to_datetime(
            first_present(raw_row, ["date", "event_date", "service_date", "date_timing"]),
            errors="coerce",
        )

        revenue = numeric(
            first_present(raw_row, ["revenue", "amount", "net", "net_revenue", "earned"])
        )
        ach = numeric(first_present(raw_row, ["ach", "ach_received", "received"]))
        expected = numeric(first_present(raw_row, ["expected", "gross_equivalent", "expected_amount"]))
        variance = numeric(first_present(raw_row, ["variance", "var"]))

        if variance is None and ach is not None and expected is not None:
            variance = ach - expected

        records.append(
            {
                "event_number": int(float(event_number)) if numeric(event_number) is not None else index,
                "date": event_date,
                "month": event_date.strftime("%B %Y") if pd.notna(event_date) else "Date unavailable",
                "client": client,
                "city": city or "Location unavailable",
                "region_code": region,
                "state_region": state_region,
                "status": status,
                "notes": text(first_present(raw_row, ["notes", "note", "description"])),
                "work_order": text(first_present(raw_row, ["work_order", "wo", "wo_number", "work_order_number"])),
                "ticket_number": text(first_present(raw_row, ["ticket_number", "ticket", "ticket_#"])),
                "revenue": revenue,
                "ach": ach,
                "expected": expected,
                "variance": variance,
                "payment_status": text(first_present(raw_row, ["payment_status", "ach_status"])),
            }
        )

    result = pd.DataFrame(records, columns=CANONICAL_TIMELINE_COLUMNS)
    result = result.sort_values("event_number", kind="stable").reset_index(drop=True)
    return result


def normalize_pipeline(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        return empty_frame(CANONICAL_PIPELINE_COLUMNS)

    normalized = standardize_columns(frame)
    records: list[dict[str, Any]] = []

    for index, raw_row in enumerate(normalized.to_dict("records"), start=1):
        status = text(first_present(raw_row, ["status"]), "Scheduled").title()
        if status not in {"Scheduled", "Awarded", "Active", "Pending"}:
            continue

        location = first_present(raw_row, ["location", "site"])
        city = text(first_present(raw_row, ["city"]))
        region = compact_region_code(first_present(raw_row, ["region_code", "state"]))

        if location and (not city or not region):
            parsed_city, parsed_region = split_location(location)
            city = city or parsed_city
            region = region or parsed_region

        event_date = pd.to_datetime(
            first_present(raw_row, ["date", "event_date", "date_timing", "date_timing_"]),
            errors="coerce",
        )

        records.append(
            {
                "event_number": first_present(raw_row, ["event_number", "visit_number"], ""),
                "date": event_date,
                "client": canonical_client(first_present(raw_row, ["client"])),
                "city": city or text(location, "Location unavailable"),
                "region_code": region,
                "state_region": jurisdiction_name(region),
                "status": status,
                "notes": text(first_present(raw_row, ["notes"])),
                "work_order": text(first_present(raw_row, ["work_order", "wo_number"])),
                "ticket_number": text(first_present(raw_row, ["ticket_number", "ticket"])),
            }
        )

    return pd.DataFrame(records, columns=CANONICAL_PIPELINE_COLUMNS)


# =============================================================================
# SOURCE DISCOVERY
# =============================================================================

def candidate_workbooks() -> list[Path]:
    patterns = [
        "Barrister_Source_of_Truth*.xlsx",
        "Barrister_Master*.xlsx",
        "*Barrister*Master*.xlsx",
        "*.xlsx",
    ]
    found: list[Path] = []
    search_roots = [DATA_DIR, ROOT]

    for search_root in search_roots:
        if not search_root.exists():
            continue
        for pattern in patterns:
            for path in search_root.glob(pattern):
                if path.name.startswith("~$"):
                    continue
                if path not in found:
                    found.append(path)

    return sorted(found, key=lambda path: path.stat().st_mtime, reverse=True)


def candidate_csvs() -> list[Path]:
    candidates = [
        DATA_DIR / "barrister_timeline.csv",
        DATA_DIR / "timeline.csv",
        ROOT / "barrister_timeline.csv",
        ROOT / "timeline.csv",
    ]
    return [path for path in candidates if path.exists()]


def read_excel_sheet(path: Path, sheet_candidates: list[str]) -> pd.DataFrame:
    try:
        workbook = pd.ExcelFile(path)
    except Exception:
        return pd.DataFrame()

    mapping = {clean_key(name): name for name in workbook.sheet_names}

    for candidate in sheet_candidates:
        source_name = mapping.get(clean_key(candidate))
        if source_name:
            try:
                return pd.read_excel(path, sheet_name=source_name)
            except Exception:
                return pd.DataFrame()

    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_bundle() -> DataBundle:
    warnings: list[str] = []

    workbooks = candidate_workbooks()
    if workbooks:
        source = workbooks[0]
        timeline_raw = read_excel_sheet(source, ["Timeline", "Chronology", "Service Events"])
        pipeline_raw = read_excel_sheet(source, ["Pipeline", "Upcoming", "Scheduled Assignments"])
        ledger_raw = read_excel_sheet(
            source,
            ["Canonical Ledger", "Financial Status", "Ledger", "Analytics Input"],
        )

        timeline = normalize_timeline(timeline_raw)
        pipeline = normalize_pipeline(pipeline_raw)

        if timeline.empty:
            warnings.append(f"Workbook found, but no usable Timeline rows were read from {source.name}.")

        return DataBundle(
            timeline=timeline,
            pipeline=pipeline,
            ledger=standardize_columns(ledger_raw) if not ledger_raw.empty else pd.DataFrame(),
            source=source,
            source_kind="Workbook",
            warnings=warnings,
        )

    csvs = candidate_csvs()
    if csvs:
        source = csvs[0]
        try:
            timeline_raw = pd.read_csv(source)
        except Exception as error:
            return DataBundle(
                timeline=empty_frame(CANONICAL_TIMELINE_COLUMNS),
                pipeline=empty_frame(CANONICAL_PIPELINE_COLUMNS),
                ledger=pd.DataFrame(),
                source=source,
                source_kind="CSV",
                warnings=[f"Timeline CSV could not be read: {error}"],
            )

        timeline = normalize_timeline(timeline_raw)

        pipeline_path = DATA_DIR / "barrister_pipeline.csv"
        pipeline_raw = pd.read_csv(pipeline_path) if pipeline_path.exists() else pd.DataFrame()
        pipeline = normalize_pipeline(pipeline_raw)

        return DataBundle(
            timeline=timeline,
            pipeline=pipeline,
            ledger=pd.DataFrame(),
            source=source,
            source_kind="CSV",
            warnings=warnings,
        )

    return DataBundle(
        timeline=empty_frame(CANONICAL_TIMELINE_COLUMNS),
        pipeline=empty_frame(CANONICAL_PIPELINE_COLUMNS),
        ledger=pd.DataFrame(),
        source=None,
        source_kind="None",
        warnings=["No Barrister workbook or timeline CSV was found."],
    )


# =============================================================================
# DERIVED DATA
# =============================================================================

def completed_timeline(bundle: DataBundle) -> pd.DataFrame:
    timeline = bundle.timeline.copy()
    if timeline.empty:
        return timeline
    return timeline[timeline["status"].astype(str).str.casefold().eq("completed")].copy()


def scheduled_timeline(bundle: DataBundle) -> pd.DataFrame:
    timeline = bundle.timeline.copy()
    scheduled = timeline[
        timeline["status"].astype(str).str.casefold().isin(
            {"scheduled", "awarded", "active", "pending"}
        )
    ].copy()

    pipeline = bundle.pipeline.copy()
    if pipeline.empty:
        return scheduled

    shared_columns = [
        "event_number",
        "date",
        "client",
        "city",
        "region_code",
        "state_region",
        "status",
        "notes",
        "work_order",
        "ticket_number",
    ]
    pipeline = pipeline[shared_columns]
    scheduled = scheduled[shared_columns] if not scheduled.empty else empty_frame(shared_columns)

    combined = pd.concat([scheduled, pipeline], ignore_index=True)
    if combined.empty:
        return combined

    combined["_dedupe"] = (
        combined["client"].fillna("").astype(str).str.casefold()
        + "|"
        + combined["city"].fillna("").astype(str).str.casefold()
        + "|"
        + combined["region_code"].fillna("").astype(str).str.casefold()
        + "|"
        + combined["date"].astype(str)
    )
    combined = combined.drop_duplicates("_dedupe").drop(columns="_dedupe")
    combined = combined.sort_values(["date", "client"], na_position="last").reset_index(drop=True)
    return combined


def client_summary(bundle: DataBundle) -> pd.DataFrame:
    completed = completed_timeline(bundle)
    if completed.empty:
        return pd.DataFrame(
            columns=[
                "client",
                "visits",
                "first_visit",
                "last_visit",
                "cities",
                "states",
                "notes_count",
                "upcoming",
            ]
        )

    upcoming = scheduled_timeline(bundle)
    upcoming_counts = (
        upcoming["client"].value_counts().to_dict()
        if not upcoming.empty and "client" in upcoming
        else {}
    )

    rows: list[dict[str, Any]] = []

    for client, visits in completed.groupby("client", sort=False):
        event_numbers = pd.to_numeric(visits["event_number"], errors="coerce").dropna()
        cities = sorted(
            {
                text(value)
                for value in visits["city"]
                if text(value) and text(value) != "Location unavailable"
            },
            key=str.casefold,
        )
        states = sorted(
            {compact_region_code(value) for value in visits["region_code"] if compact_region_code(value)}
        )

        rows.append(
            {
                "client": client,
                "visits": len(visits),
                "first_visit": int(event_numbers.min()) if not event_numbers.empty else 0,
                "last_visit": int(event_numbers.max()) if not event_numbers.empty else 0,
                "cities": cities,
                "states": states,
                "notes_count": int(visits["notes"].fillna("").astype(str).str.strip().ne("").sum()),
                "upcoming": int(upcoming_counts.get(client, 0)),
            }
        )

    summary = pd.DataFrame(rows)
    return summary.sort_values(["visits", "first_visit"], ascending=[False, True]).reset_index(drop=True)


def jurisdiction_summary(bundle: DataBundle) -> pd.DataFrame:
    completed = completed_timeline(bundle)
    if completed.empty:
        return pd.DataFrame(columns=["jurisdiction", "events", "percentage"])

    grouped = (
        completed.assign(
            jurisdiction=completed.apply(
                lambda row: jurisdiction_name(row.get("region_code"), row.get("state_region")),
                axis=1,
            )
        )
        .groupby("jurisdiction", as_index=False)
        .size()
        .rename(columns={"size": "events"})
        .sort_values("events", ascending=False)
    )

    total = int(grouped["events"].sum())
    grouped["percentage"] = grouped["events"].div(total).mul(100) if total else 0.0
    return grouped.reset_index(drop=True)


def financial_rows(bundle: DataBundle) -> pd.DataFrame:
    timeline = completed_timeline(bundle)
    if timeline.empty:
        return timeline

    for column in ["revenue", "ach", "expected", "variance"]:
        timeline[column] = pd.to_numeric(timeline[column], errors="coerce")

    if timeline["revenue"].notna().any():
        return timeline

    ledger = bundle.ledger.copy()
    if ledger.empty:
        return timeline

    possible_event_columns = [
        column
        for column in ledger.columns
        if clean_key(column) in {"event_number", "visit_number", "visit", "event"}
    ]
    if not possible_event_columns:
        return timeline

    event_column = possible_event_columns[0]
    ledger[event_column] = pd.to_numeric(ledger[event_column], errors="coerce")
    timeline["event_number"] = pd.to_numeric(timeline["event_number"], errors="coerce")

    amount_map: dict[int, dict[str, float | None]] = {}

    for row in ledger.to_dict("records"):
        event = numeric(row.get(event_column))
        if event is None:
            continue
        amount_map[int(event)] = {
            "revenue": numeric(first_present(row, ["revenue", "amount", "net", "earned"])),
            "ach": numeric(first_present(row, ["ach", "ach_received", "received"])),
            "expected": numeric(first_present(row, ["expected", "gross_equivalent"])),
            "variance": numeric(first_present(row, ["variance", "var"])),
        }

    for index, row in timeline.iterrows():
        values = amount_map.get(int(row["event_number"])) if pd.notna(row["event_number"]) else None
        if not values:
            continue
        for key, value in values.items():
            if value is not None:
                timeline.at[index, key] = value

    return timeline


# =============================================================================
# LOGOS
# =============================================================================

def slug(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", text(value).lower())


@st.cache_data(show_spinner=False)
def logo_index() -> dict[str, Path]:
    index: dict[str, Path] = {}
    for directory in LOGO_DIRS:
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
                continue
            index.setdefault(slug(path.stem), path)
    return index


def logo_for(client: str) -> Path | None:
    index = logo_index()
    key = slug(client)

    if key in index:
        return index[key]

    aliases = {
        "usda": ["unitedstatesdepartmentofagriculture"],
        "baskinrobbins": ["baskinrobbins", "baskin"],
        "dunkin": ["dunkin", "dunkindonuts"],
        "giantfoodstores": ["giant", "giantfood"],
        "residentialannapolisneckmd": ["residential", "home"],
    }

    for candidate in aliases.get(key, []):
        if candidate in index:
            return index[candidate]

    for indexed_key, path in index.items():
        if key and (key in indexed_key or indexed_key in key):
            return path

    return None


def data_uri(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
    }.get(path.suffix.lower(), "application/octet-stream")
    import base64

    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def initials(client: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", client)
    return "".join(word[0] for word in words[:2]).upper() or "?"


# =============================================================================
# OUTPUT PARSER
# =============================================================================

def output_candidates() -> list[Path]:
    candidates = [
        ROOT / "logs" / "latest_barrister_output.json",
        ROOT / "logs" / "latest_barrister_output.txt",
        DATA_DIR / "latest_barrister_output.json",
        DATA_DIR / "latest_barrister_output.txt",
        Path.home()
        / "Documents"
        / "BarristerEngine"
        / "BarristerEngine"
        / "logs"
        / "latest_barrister_output.json",
        Path.home()
        / "Documents"
        / "BarristerEngine"
        / "BarristerEngine"
        / "logs"
        / "latest_barrister_output.txt",
    ]
    return [path for path in candidates if path.exists()]


def parse_output_text(raw: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "batch": "Unavailable",
        "workbook": "Unavailable",
        "months": [],
        "raw": raw,
    }

    batch = re.search(r"^Batch:\s*(.+)$", raw, flags=re.M)
    if batch:
        result["batch"] = batch.group(1).strip()

    workbooks = re.findall(r"^Workbook:\s*(.+)$", raw, flags=re.M)
    if workbooks:
        result["workbook"] = workbooks[-1].strip()

    month_pattern = re.compile(
        r"Month\s+(?P<number>\d+)\s*\|\|\s*(?P<label>[^\n]+)\n"
        r"\{(?P<events>\d+)\s+events\s*\|\s*(?P<days>\d+)\s+business days\}\n"
        r"- earned \$(?P<earned>[\d,.]+) net\n"
        r"- received \$(?P<received>[\d,.]+) ACH cash\n"
        r"- outstanding \$(?P<outstanding>[\d,.]+) "
        r"\((?P<pending>\d+) ACH pending/partial\)\n"
        r"- ACH progress:\s*(?P<complete>\d+)/(?P<total>\d+) complete "
        r"\((?P<progress>[\d.]+)%\)\n"
        r"- equivalent to \$(?P<gross>[\d,.]+) gross\n"
        r"- averaged \$(?P<net_event>[\d,.]+) net/event\n"
        r"- equivalent to \$(?P<gross_event>[\d,.]+) gross/event\n"
        r"Annual Pace:\n"
        r"\$(?P<annual>[\d,.]+)/year",
        flags=re.M,
    )

    result["months"] = [match.groupdict() for match in month_pattern.finditer(raw)]
    return result


def load_output() -> tuple[dict[str, Any], Path | None]:
    candidates = output_candidates()
    if not candidates:
        return {"months": [], "raw": "No Barrister Output file was found."}, None

    source = candidates[0]

    if source.suffix.lower() == ".json":
        try:
            payload = json.loads(source.read_text(errors="ignore"))
            raw = text(payload.get("report_text"))
            if raw:
                parsed = parse_output_text(raw)
                parsed.update({key: value for key, value in payload.items() if value is not None})
                return parsed, source
            return payload, source
        except Exception:
            pass

    raw = source.read_text(errors="ignore")
    return parse_output_text(raw), source


# =============================================================================
# RENDER HELPERS
# =============================================================================

def money(value: object) -> str:
    amount = numeric(value)
    return f"${amount:,.2f}" if amount is not None else "—"


def date_label(value: object) -> str:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return "Date TBD"
    return parsed.strftime("%b %-d, %Y")


def metric_strip(events: int, clients: int, repeat_clients: int, jurisdictions: int) -> None:
    st.markdown(
        f"""
        <div class="metric-strip">
          <div class="metric-cell"><b>{events}</b><span>Service Events</span></div>
          <div class="metric-cell"><b>{clients}</b><span>Unique Clients</span></div>
          <div class="metric-cell"><b>{repeat_clients}</b><span>Repeat Clients</span></div>
          <div class="metric-cell"><b>{jurisdictions}</b><span>Jurisdictions</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_jurisdiction_donut(summary: pd.DataFrame) -> None:
    if summary.empty:
        st.info("Jurisdiction activity is unavailable.")
        return

    labels = summary["jurisdiction"].tolist()
    values = summary["events"].tolist()
    colors = [JURISDICTION_META.get(label, JURISDICTION_META["Other"])["color"] for label in labels]

    figure = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=.57,
            marker={"colors": colors, "line": {"color": "#08111f", "width": 3}},
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value} events<br>%{percent}<extra></extra>",
            sort=False,
        )
    )

    total = int(summary["events"].sum())
    figure.update_layout(
        height=430,
        margin={"l": 10, "r": 10, "t": 14, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        annotations=[
            {
                "text": f"<span style='font-size:12px;color:#9eb0c4'>TOTAL VISITS</span><br>"
                f"<b style='font-size:32px;color:#f8fafc'>{total}</b>",
                "x": .5,
                "y": .5,
                "showarrow": False,
            }
        ],
    )

    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

    cards = []
    for row in summary.to_dict("records"):
        meta = JURISDICTION_META.get(row["jurisdiction"], JURISDICTION_META["Other"])
        cards.append(
            f"""
            <div class="output-card" style="border-left:5px solid {meta['color']}">
              <div style="display:flex;justify-content:space-between;align-items:center;gap:10px">
                <div style="font-weight:900">{meta['icon']} {escape(row['jurisdiction'])}</div>
                <div style="font-weight:950">{row['percentage']:.1f}%</div>
              </div>
              <div style="margin-top:5px;color:#9eb0c4;font-size:.68rem">{int(row['events'])} completed events</div>
            </div>
            """
        )

    st.markdown("".join(cards), unsafe_allow_html=True)


# =============================================================================
# PAGE RENDERERS
# =============================================================================

def render_home(bundle: DataBundle) -> None:
    completed = completed_timeline(bundle)
    upcoming = scheduled_timeline(bundle)
    clients = client_summary(bundle)
    jurisdictions = jurisdiction_summary(bundle)

    latest = completed.iloc[-1].to_dict() if not completed.empty else {}
    next_stop = upcoming.iloc[0].to_dict() if not upcoming.empty else {}

    st.markdown(
        """
        <div class="section-kicker">FIELD OPERATIONS</div>
        <div class="section-title">Operational Snapshot</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="spotlight-grid">
          <div class="spotlight">
            <div class="spotlight-label">Latest Stop</div>
            <div class="spotlight-title">{escape(text(latest.get("client"), "No completed events"))}</div>
            <div class="spotlight-meta">
              {escape(text(latest.get("city"), ""))}
              {", " + escape(text(latest.get("region_code"))) if text(latest.get("region_code")) else ""}
            </div>
            <div class="status-pill">Completed</div>
          </div>
          <div class="spotlight">
            <div class="spotlight-label">Next Stop</div>
            <div class="spotlight-title">{escape(text(next_stop.get("client"), "Nothing scheduled"))}</div>
            <div class="spotlight-meta">
              {escape(date_label(next_stop.get("date"))) if next_stop else "Pipeline clear"}
              {" · " + escape(text(next_stop.get("city"))) if next_stop else ""}
            </div>
            <div class="status-pill">Upcoming</div>
          </div>
          <div class="spotlight">
            <div class="spotlight-label">Client Network</div>
            <div class="spotlight-title">{len(clients)} active clients</div>
            <div class="spotlight-meta">
              {int((clients["visits"] > 1).sum()) if not clients.empty else 0} repeat relationships across
              {len(jurisdictions)} jurisdictions.
            </div>
            <div class="status-pill">Authoritative source</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, .95], gap="large")

    with left:
        st.markdown(
            '<div class="section-kicker">TERRITORY</div><div class="section-title">Service Activity by Jurisdiction</div>',
            unsafe_allow_html=True,
        )
        render_jurisdiction_donut(jurisdictions)

    with right:
        st.markdown(
            '<div class="section-kicker">LEADERS</div><div class="section-title">Top Clients</div>',
            unsafe_allow_html=True,
        )
        if clients.empty:
            st.info("No client data is available.")
        else:
            top = clients.head(8)
            max_visits = max(int(top["visits"].max()), 1)
            for row in top.to_dict("records"):
                width = max(8, int(row["visits"] / max_visits * 100))
                st.markdown(
                    f"""
                    <div class="output-card">
                      <div style="display:flex;justify-content:space-between;gap:10px">
                        <div style="font-weight:900">{escape(row["client"])}</div>
                        <div style="font-weight:950;color:#facc15">{int(row["visits"])}</div>
                      </div>
                      <div style="height:6px;border-radius:99px;background:rgba(148,163,184,.12);margin-top:8px">
                        <div style="width:{width}%;height:6px;border-radius:99px;background:linear-gradient(90deg,#2dd4bf,#5b8def)"></div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_journey(bundle: DataBundle) -> None:
    completed = completed_timeline(bundle)

    st.markdown(
        '<div class="section-kicker">CAREER JOURNEY</div><div class="section-title">Chronological Service Timeline</div>',
        unsafe_allow_html=True,
    )

    if completed.empty:
        st.info("No completed timeline events are available.")
        return

    st.markdown('<div class="timeline">', unsafe_allow_html=True)

    last_month = None

    for row in completed.to_dict("records"):
        month = text(row.get("month"), "Date unavailable")

        if month != last_month:
            st.markdown(f'<div class="month-tag">{escape(month)}</div>', unsafe_allow_html=True)
            last_month = month

        location = ", ".join(
            part for part in [text(row.get("city")), text(row.get("region_code"))] if part
        )

        st.markdown(
            f"""
            <div class="timeline-row">
              <div>
                <div class="timeline-client">{escape(text(row.get("client"), "Unknown Client"))}</div>
                <div class="timeline-meta">
                  {escape(location or "Location unavailable")}
                  {" · " + escape(text(row.get("notes"))) if text(row.get("notes")) else ""}
                </div>
              </div>
              <div class="event-number">#{int(row.get("event_number", 0))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_clients(bundle: DataBundle) -> None:
    clients = client_summary(bundle)

    st.markdown(
        '<div class="section-kicker">CLIENT NETWORK</div><div class="section-title">Clients Visited. Clients Served.</div>',
        unsafe_allow_html=True,
    )

    if clients.empty:
        st.info("No client records are available.")
        return

    cards: list[str] = []

    for row in clients.to_dict("records"):
        client = text(row.get("client"), "Unknown Client")
        logo = logo_for(client)
        uri = data_uri(logo)

        visual = (
            f'<img src="{uri}" alt="{escape(client, quote=True)} logo">'
            if uri
            else f'<div class="client-initials">{escape(initials(client))}</div>'
        )

        states = " · ".join(row.get("states") or []) or "State unavailable"
        first = f"#{int(row.get('first_visit', 0))}" if row.get("first_visit") else "—"
        last = f"#{int(row.get('last_visit', 0))}" if row.get("last_visit") else "—"

        cards.append(
            f"""
            <div class="client-card">
              <div>
                <div class="client-logo">{visual}</div>
                <div class="client-name">{escape(client)}</div>
                <div class="client-detail">
                  First {first} · Latest {last}<br>
                  {escape(states)}
                  {" · " + str(int(row.get("upcoming", 0))) + " upcoming" if row.get("upcoming") else ""}
                </div>
              </div>
              <div class="client-count">{int(row.get("visits", 0))} visit{"s" if int(row.get("visits", 0)) != 1 else ""}</div>
            </div>
            """
        )

    st.markdown(f'<div class="client-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_upcoming(bundle: DataBundle) -> None:
    upcoming = scheduled_timeline(bundle)

    st.markdown(
        '<div class="section-kicker">FORWARD VIEW</div><div class="section-title">Upcoming Assignments</div>',
        unsafe_allow_html=True,
    )

    if upcoming.empty:
        st.success("No scheduled assignments are currently loaded.")
        return

    cards: list[str] = []

    for row in upcoming.to_dict("records"):
        location = ", ".join(
            part for part in [text(row.get("city")), text(row.get("region_code"))] if part
        )

        meta = " · ".join(
            part
            for part in [
                location,
                text(row.get("work_order")) and f"WO {text(row.get('work_order'))}",
                text(row.get("ticket_number")) and f"Ticket {text(row.get('ticket_number'))}",
            ]
            if part
        )

        cards.append(
            f"""
            <div class="upcoming-card">
              <div class="upcoming-date">{escape(date_label(row.get("date")))}</div>
              <div class="upcoming-client">{escape(text(row.get("client"), "Unknown Client"))}</div>
              <div class="upcoming-meta">{escape(meta or "Location pending")}</div>
              {"<div class='upcoming-meta'>" + escape(text(row.get("notes"))) + "</div>" if text(row.get("notes")) else ""}
              <div class="status-pill">{escape(text(row.get("status"), "Scheduled"))}</div>
            </div>
            """
        )

    st.markdown(f'<div class="upcoming-list">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_financials(bundle: DataBundle) -> None:
    frame = financial_rows(bundle)

    st.markdown(
        '<div class="section-kicker">FINANCIAL ANALYTICS</div><div class="section-title">Earnings & Efficiency</div>',
        unsafe_allow_html=True,
    )

    if frame.empty or not frame["revenue"].notna().any():
        st.info(
            "No usable event-level revenue values were found in the active source. "
            "This page will populate automatically when the workbook or ledger includes revenue fields."
        )
        return

    known = frame.dropna(subset=["revenue"]).copy()
    total = float(known["revenue"].sum())
    average = float(known["revenue"].mean())
    known_events = len(known)
    received = float(known["ach"].dropna().sum()) if known["ach"].notna().any() else None
    outstanding = total - received if received is not None else None

    st.markdown(
        f"""
        <div class="finance-grid">
          <div class="finance-card"><div class="finance-value">{money(total)}</div><div class="finance-label">Known Net Revenue</div></div>
          <div class="finance-card"><div class="finance-value">{money(average)}</div><div class="finance-label">Average / Known Event</div></div>
          <div class="finance-card"><div class="finance-value">{known_events}</div><div class="finance-label">Revenue-Coded Events</div></div>
          <div class="finance-card"><div class="finance-value">{money(outstanding)}</div><div class="finance-label">Outstanding vs ACH</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    by_state = (
        known.assign(
            jurisdiction=known.apply(
                lambda row: jurisdiction_name(row.get("region_code"), row.get("state_region")),
                axis=1,
            )
        )
        .groupby("jurisdiction", as_index=False)
        .agg(events=("event_number", "count"), revenue=("revenue", "sum"))
    )
    by_state["average"] = by_state["revenue"].div(by_state["events"])

    figure = go.Figure(
        go.Bar(
            x=by_state["average"],
            y=by_state["jurisdiction"],
            orientation="h",
            marker_color=[
                JURISDICTION_META.get(label, JURISDICTION_META["Other"])["color"]
                for label in by_state["jurisdiction"]
            ],
            text=[money(value) for value in by_state["average"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x:$,.2f} average/event<extra></extra>",
        )
    )
    figure.update_layout(
        height=370,
        margin={"l": 10, "r": 55, "t": 25, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"showgrid": False, "visible": False},
        yaxis={"title": None, "autorange": "reversed"},
        showlegend=False,
    )
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})


def render_output() -> None:
    payload, source = load_output()
    months = payload.get("months") or []
    raw = text(payload.get("report_text") or payload.get("raw"), "No output text is available.")

    st.markdown(
        '<div class="section-kicker">BARRISTERENGINE</div><div class="section-title">Engine Output</div>',
        unsafe_allow_html=True,
    )

    batch = text(payload.get("batch"), "Unavailable")
    workbook = text(payload.get("workbook"), "Unavailable")

    st.markdown(
        f"""
        <div class="spotlight">
          <div class="spotlight-label">Latest Batch</div>
          <div class="spotlight-title">{escape(batch)}</div>
          <div class="spotlight-meta">Workbook: {escape(workbook)}</div>
          <div class="status-pill">Unified output source</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if months:
        st.markdown(
            '<div class="section-kicker" style="margin-top:18px">PERIODS</div><div class="section-title">Monthly Summaries</div>',
            unsafe_allow_html=True,
        )

        cards = []

        for month in months:
            cards.append(
                f"""
                <div class="output-card">
                  <div style="font-weight:950;color:#facc15">
                    Month {escape(text(month.get("number")))} · {escape(text(month.get("label"), "Period"))}
                  </div>
                  <div style="display:grid;grid-template-columns:1fr auto;gap:6px;margin-top:10px;font-size:.75rem">
                    <span style="color:#9eb0c4">Events</span><b>{escape(text(month.get("events"), "0"))}</b>
                    <span style="color:#9eb0c4">Net earned</span><b>{money(month.get("earned"))}</b>
                    <span style="color:#9eb0c4">ACH received</span><b>{money(month.get("received"))}</b>
                    <span style="color:#9eb0c4">Outstanding</span><b>{money(month.get("outstanding"))}</b>
                    <span style="color:#9eb0c4">ACH progress</span><b>{escape(text(month.get("progress"), "0"))}%</b>
                    <span style="color:#9eb0c4">Net / event</span><b>{money(month.get("net_event"))}</b>
                    <span style="color:#9eb0c4">Gross / event</span><b>{money(month.get("gross_event"))}</b>
                    <span style="color:#9eb0c4">Annual pace</span><b>{money(month.get("annual"))}</b>
                  </div>
                </div>
                """
            )

        st.markdown(f'<div class="client-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
    else:
        st.info("The current output file does not contain structured monthly sections.")

    with st.expander("Raw Engine Output", expanded=False):
        st.code(raw, language="text")

    st.markdown(
        f'<div class="source-note">Source: {escape(str(source) if source else "No output source found")}</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# APPLICATION
# =============================================================================

bundle = load_bundle()
completed = completed_timeline(bundle)
clients = client_summary(bundle)
jurisdictions = jurisdiction_summary(bundle)

event_count = len(completed)
client_count = len(clients)
repeat_count = int((clients["visits"] > 1).sum()) if not clients.empty else 0
jurisdiction_count = len(jurisdictions[jurisdictions["jurisdiction"].ne("Other")]) if not jurisdictions.empty else 0

st.markdown(
    f"""
    <div class="hero">
      <div class="hero-kicker">AGENT EINI · FIELD TRANSIT AUTHORITY</div>
      <div class="hero-title">Barrister<br>Dashboard</div>
      <div class="hero-sub">
        One normalized source powering the journey, client directory, upcoming assignments,
        jurisdiction analytics, financials, and engine output.
      </div>
      <div class="build-pill">{BUILD_LABEL} · Source rows: {len(bundle.timeline)}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_strip(event_count, client_count, repeat_count, jurisdiction_count)

for warning in bundle.warnings:
    st.warning(warning)

tabs = st.tabs(["Home", "Journey", "Clients", "Upcoming", "Financials", "Engine Output"])

with tabs[0]:
    render_home(bundle)

with tabs[1]:
    render_journey(bundle)

with tabs[2]:
    render_clients(bundle)

with tabs[3]:
    render_upcoming(bundle)

with tabs[4]:
    render_financials(bundle)

with tabs[5]:
    render_output()

st.markdown(
    f'<div class="source-note">Active source: {escape(str(bundle.source) if bundle.source else "None")} · '
    f'{escape(bundle.source_kind)} · Supported regions: {" · ".join(SUPPORTED_REGIONS)}</div>',
    unsafe_allow_html=True,
)
