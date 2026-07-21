from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import math
import re

import pandas as pd

from services.career_analytics_engine import build_career_analytics


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def number(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)) and not pd.isna(value):
        return float(value)
    raw = re.sub(r"[^0-9.\-]", "", str(value))
    try:
        return float(raw) if raw not in {"", "-", ".", "-."} else 0.0
    except ValueError:
        return 0.0


def integer(value: Any) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def as_date(value: Any):
    if value is None or value == "":
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    return None if pd.isna(parsed) else parsed.date()


def key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).casefold())


def find_column(frame: pd.DataFrame, *aliases: str) -> str | None:
    lookup = {key(column): column for column in frame.columns}
    for alias in aliases:
        if key(alias) in lookup:
            return lookup[key(alias)]
    return None


def cell(row: pd.Series, column: str | None, default: Any = "") -> Any:
    if column is None:
        return default
    value = row.get(column, default)
    return default if pd.isna(value) else value


def split_work_orders(value: Any) -> list[str]:
    return [clean(item) for item in re.split(r"[,;/|]+", clean(value)) if clean(item)]


def build_canonical_career_analytics(project_root: Path) -> dict[str, Any]:
    project_root = Path(project_root).resolve()
    master_path = project_root / "data" / "Barrister_Master.xlsx"
    analytics_path = project_root / "data" / "current_master.xlsx"
    override_path = project_root / "config" / "canonical_event_overrides.json"

    for path in (master_path, analytics_path, override_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    overrides = json.loads(override_path.read_text(encoding="utf-8"))
    date_overrides = {
        int(event): as_date(value)
        for event, value in overrides.get("event_date_overrides", {}).items()
    }

    registry_path = project_root / "data" / "event_date_registry.json"
    event_date_registry = dict(date_overrides)
    if registry_path.is_file():
        registry_payload = json.loads(
            registry_path.read_text(encoding="utf-8")
        )
        for event, value in registry_payload.get("event_dates", {}).items():
            parsed = as_date(value)
            if parsed is not None:
                event_date_registry[int(event)] = parsed

    timeline = pd.read_excel(master_path, sheet_name="Timeline")
    service_events = pd.read_excel(analytics_path, sheet_name="Service Events")
    ledger_frame = pd.read_excel(analytics_path, sheet_name="Work Orders & Ledger")

    m_event = find_column(timeline, "Visit #", "Event #", "Event Number", "event_number")
    m_client = find_column(timeline, "Client", "Client Name")
    m_city = find_column(timeline, "City")
    m_state = find_column(timeline, "State/Region", "State", "Jurisdiction")
    m_status = find_column(timeline, "Status")
    m_notes = find_column(timeline, "Notes")

    a_event = find_column(service_events, "Event #", "Event Number", "Visit #", "event_number")
    a_date = find_column(service_events, "Service Date", "Date", "Event Date", "service_date")
    a_wo = find_column(service_events, "Work Orders", "Work Order #", "WO #", "wo")
    a_revenue = find_column(service_events, "Confirmed Revenue", "Revenue", "Amount")

    required = {
        "Timeline event": m_event,
        "Timeline client": m_client,
        "Timeline city": m_city,
        "Timeline state": m_state,
        "Timeline status": m_status,
        "Service Events event": a_event,
        "Service Events date": a_date,
    }
    missing = [name for name, column in required.items() if column is None]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    analytics_by_event: dict[int, dict[str, Any]] = {}
    for _, row in service_events.iterrows():
        event = integer(cell(row, a_event, 0))
        if event <= 0:
            continue
        analytics_by_event[event] = {
            "service_date": as_date(cell(row, a_date, None)),
            "work_orders": clean(cell(row, a_wo, "")),
            "confirmed_revenue": number(cell(row, a_revenue, 0)),
        }

    events: list[dict[str, Any]] = []
    for _, row in timeline.iterrows():
        event = integer(cell(row, m_event, 0))
        if event <= 0:
            continue
        detail = analytics_by_event.get(event, {})
        service_date = event_date_registry.get(event) or detail.get("service_date")
        if service_date is None:
            service_date = (
                events[-1]["service_date"]
                if events
                else pd.Timestamp.today().date()
            )

        client = clean(cell(row, m_client, ""))
        city = clean(cell(row, m_city, ""))
        state = clean(cell(row, m_state, ""))
        status = clean(cell(row, m_status, ""))
        work_orders = detail.get("work_orders", "")
        confirmed_revenue = float(detail.get("confirmed_revenue", 0.0))
        location = ", ".join(part for part in (city, state) if part)

        events.append({
            "event_number": event,
            "physical_visit_id": str(event),
            "service_date": service_date,
            "weekday": service_date.strftime("%A"),
            "workweek": 0,
            "my_month": service_date.strftime("%Y-%m"),
            "client_id": client,
            "client": client,
            "site_name": location,
            "city": city,
            "state": state,
            "jurisdiction": state,
            "location_key": location,
            "status": status,
            "visit_type": "",
            "work_order_count": len(split_work_orders(work_orders)),
            "work_orders": work_orders,
            "confirmed_revenue": confirmed_revenue,
            "revenue_eligibility": "Eligible" if confirmed_revenue > 0 else "",
            "financial_scope": "Yes",
            "breakdown_expected": "",
            "notes": clean(cell(row, m_notes, "")),
        })

    events.sort(key=lambda row: (row["service_date"], row["event_number"]))
    first_date = min(row["service_date"] for row in events)
    for row in events:
        row["workweek"] = ((row["service_date"] - first_date).days // 7) + 1

    aliases = {
        "ledger_record_id": ("Ledger Record ID", "Record ID", "ID"),
        "work_order": ("Work Order", "Work Order #", "WO #", "wo"),
        "event_number": ("Event #", "Event Number", "event_number"),
        "client": ("Client", "Client Name"),
        "service_date": ("Service Date", "Date"),
        "agreed_amount": ("Agreed Amount", "Promised Amount", "Rate"),
        "breakdown_confirmed": ("Breakdown Confirmed", "Payment Confirmation"),
        "breakdown_amount": ("Breakdown Amount", "Confirmed Amount"),
        "breakdown_date": ("Breakdown Date",),
        "expected_payment_date": ("Expected Payment Date",),
        "ach_confirmed": ("ACH Confirmed", "Deposit Confirmed"),
        "ach_amount": ("ACH Amount", "Deposit Amount"),
        "ach_date": ("ACH Date", "Deposit Date"),
        "variance": ("Variance", "Deduction"),
        "reconciliation_status": ("Reconciliation Status",),
        "mapping_status": ("Mapping Status",),
        "alias_related_wo": ("Alias Related WO", "Related WO"),
    }
    cols = {name: find_column(ledger_frame, *names) for name, names in aliases.items()}

    ledger_rows: list[dict[str, Any]] = []
    for index, row in ledger_frame.iterrows():
        work_order = clean(cell(row, cols["work_order"], ""))
        if not work_order:
            continue
        client = clean(cell(row, cols["client"], ""))
        ledger_rows.append({
            "ledger_record_id": clean(cell(row, cols["ledger_record_id"], str(index + 1))),
            "work_order": work_order,
            "event_number": integer(cell(row, cols["event_number"], 0)),
            "client_id": client,
            "client": client,
            "service_date": as_date(cell(row, cols["service_date"], None)),
            "agreed_amount": number(cell(row, cols["agreed_amount"], 0)),
            "breakdown_confirmed": cell(row, cols["breakdown_confirmed"], ""),
            "breakdown_amount": number(cell(row, cols["breakdown_amount"], 0)),
            "breakdown_date": as_date(cell(row, cols["breakdown_date"], None)),
            "expected_payment_date": as_date(cell(row, cols["expected_payment_date"], None)),
            "ach_confirmed": cell(row, cols["ach_confirmed"], ""),
            "ach_amount": number(cell(row, cols["ach_amount"], 0)),
            "ach_date": as_date(cell(row, cols["ach_date"], None)),
            "variance": number(cell(row, cols["variance"], 0)),
            "reconciliation_status": cell(row, cols["reconciliation_status"], ""),
            "mapping_status": cell(row, cols["mapping_status"], ""),
            "alias_related_wo": cell(row, cols["alias_related_wo"], ""),
        })

    result = build_career_analytics(events, ledger_rows, workbook_validation=None)
    result["metadata"].update({
        "source_type": "Canonical merged source",
        "master_workbook": str(master_path),
        "analytics_workbook": str(analytics_path),
        "override_file": str(override_path),
    })
    return result
