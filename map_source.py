from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import pandas as pd


LOCATION_COLUMNS = {
    "location_key",
    "client",
    "city",
    "state",
    "address",
    "visit_numbers",
    "latitude",
    "longitude",
}


@dataclass
class CoordinateMatchResult:
    all_events: pd.DataFrame
    mapped_events: pd.DataFrame
    failed_matches: pd.DataFrame
    duplicate_matches: pd.DataFrame
    ambiguous_matches: pd.DataFrame
    successful_matches: pd.DataFrame
    locations: pd.DataFrame


def _text_series(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame:
        return pd.Series("", index=frame.index, dtype="string")
    return frame[column].fillna("").astype(str).str.strip()


def _event_dates(frame: pd.DataFrame) -> pd.Series:
    if "event_date" not in frame:
        return pd.Series(pd.NaT, index=frame.index, dtype="datetime64[ns]")
    raw = frame["event_date"]
    dates = pd.to_datetime(raw, errors="coerce")
    numeric = pd.to_numeric(raw, errors="coerce")
    excel_serials = numeric.between(20000, 80000)
    if excel_serials.any():
        dates.loc[excel_serials] = pd.to_datetime(
            numeric.loc[excel_serials], unit="D", origin="1899-12-30", errors="coerce"
        )
    return dates


def _key_part(value: object) -> str:
    text = str(value or "").strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def location_key(client: object, address: object, city: object, state: object) -> str:
    return "__".join(
        part
        for part in (
            _key_part(client),
            _key_part(address),
            _key_part(city),
            _key_part(state),
        )
        if part
    )


def _parse_visit_numbers(value: object) -> list[int]:
    return [int(number) for number in re.findall(r"\d+", str(value or ""))]


def load_locations(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Coordinate enrichment file not found: {path}")
    locations = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = sorted(LOCATION_COLUMNS.difference(locations.columns))
    if missing:
        raise ValueError(f"locations.csv is missing columns: {', '.join(missing)}")

    locations = locations[list(LOCATION_COLUMNS)].copy()
    locations["source_row"] = locations.index + 2
    for column in ("location_key", "client", "city", "state", "address", "visit_numbers"):
        locations[column] = locations[column].fillna("").astype(str).str.strip()
    locations["latitude"] = pd.to_numeric(locations["latitude"], errors="coerce")
    locations["longitude"] = pd.to_numeric(locations["longitude"], errors="coerce")
    locations["coordinates_valid"] = (
        locations["latitude"].between(-90, 90)
        & locations["longitude"].between(-180, 180)
    )
    locations["normalized_key"] = locations.apply(
        lambda row: location_key(row.client, row.address, row.city, row.state), axis=1
    )
    return locations


def _prepare_events(timeline: pd.DataFrame) -> pd.DataFrame:
    events = timeline.copy().reset_index(drop=True)
    events["source_row"] = events.index + 2
    events["event_date"] = _event_dates(events)
    events["address"] = _text_series(events, "address")
    events["city"] = _text_series(events, "city")
    events["state"] = _text_series(events, "state_region")
    missing_state = events["state"].eq("")
    events.loc[missing_state, "state"] = _text_series(events, "region_code").loc[missing_state]
    events["client"] = _text_series(events, "client")
    events["status"] = _text_series(events, "status")
    events["notes"] = _text_series(events, "notes")
    if "event_number" not in events:
        events["event_number"] = pd.NA
    events["event_number"] = pd.to_numeric(events["event_number"], errors="coerce")
    events["normalized_key"] = events.apply(
        lambda row: location_key(row.client, row.address, row.city, row.state), axis=1
    )
    return events


def _candidate_signature(row: pd.Series) -> tuple:
    return (
        row["normalized_key"],
        row["latitude"],
        row["longitude"],
    )


def match_timeline_locations(
    timeline: pd.DataFrame, locations: pd.DataFrame
) -> CoordinateMatchResult:
    """Enrich workbook Timeline rows using explicit locations.csv records."""
    events = _prepare_events(timeline)
    coordinate_rows = locations.copy().reset_index(drop=True)

    visits_to_rows: dict[int, list[int]] = {}
    for index, value in coordinate_rows["visit_numbers"].items():
        for visit_number in _parse_visit_numbers(value):
            visits_to_rows.setdefault(visit_number, []).append(index)

    keys_to_rows: dict[str, list[int]] = {}
    for index, key in coordinate_rows["normalized_key"].items():
        if key:
            keys_to_rows.setdefault(key, []).append(index)

    successful: list[dict] = []
    failed: list[dict] = []
    duplicates: list[dict] = []
    ambiguous: list[dict] = []

    for event in events.to_dict("records"):
        event_number = event.get("event_number")
        explicit_rows = []
        if pd.notna(event_number):
            explicit_rows = visits_to_rows.get(int(event_number), [])
        candidate_rows = explicit_rows
        match_method = "Visit Number"
        if not candidate_rows and event.get("normalized_key"):
            candidate_rows = keys_to_rows.get(event["normalized_key"], [])
            match_method = "Location Key"

        if not candidate_rows:
            failed.append({**event, "match_reason": "No matching locations.csv record"})
            continue

        candidates = coordinate_rows.loc[candidate_rows].copy()
        signatures = candidates.apply(_candidate_signature, axis=1).drop_duplicates()
        if len(candidates) > 1 and len(signatures) > 1:
            for candidate in candidates.to_dict("records"):
                ambiguous.append(
                    {
                        **event,
                        "location_source_row": candidate["source_row"],
                        "candidate_location_key": candidate["location_key"],
                        "candidate_latitude": candidate["latitude"],
                        "candidate_longitude": candidate["longitude"],
                        "match_reason": "Multiple conflicting coordinate candidates",
                    }
                )
            continue

        chosen = candidates.iloc[0].to_dict()
        if len(candidates) > 1:
            duplicates.append(
                {
                    **event,
                    "location_source_rows": ", ".join(
                        str(value) for value in candidates["source_row"].tolist()
                    ),
                    "location_key": chosen["location_key"],
                    "match_reason": "Duplicate equivalent coordinate records",
                }
            )
        if not chosen["coordinates_valid"]:
            failed.append(
                {
                    **event,
                    "location_source_row": chosen["source_row"],
                    "location_key": chosen["location_key"],
                    "match_reason": "Matched coordinate record has invalid latitude or longitude",
                }
            )
            continue

        successful.append(
            {
                **event,
                "latitude": chosen["latitude"],
                "longitude": chosen["longitude"],
                "location_key": chosen["location_key"],
                "location_address": chosen["address"],
                "location_city": chosen["city"],
                "location_state": chosen["state"],
                "location_source_row": chosen["source_row"],
                "match_method": match_method,
            }
        )

    successful_frame = pd.DataFrame(successful)
    failed_frame = pd.DataFrame(failed)
    duplicate_frame = pd.DataFrame(duplicates)
    ambiguous_frame = pd.DataFrame(ambiguous)
    return CoordinateMatchResult(
        all_events=events,
        mapped_events=successful_frame.copy(),
        failed_matches=failed_frame,
        duplicate_matches=duplicate_frame,
        ambiguous_matches=ambiguous_frame,
        successful_matches=successful_frame,
        locations=coordinate_rows,
    )


def filter_mapped_events(
    events: pd.DataFrame,
    states: list[str],
    clients: list[str],
    statuses: list[str],
    date_range: tuple[pd.Timestamp, pd.Timestamp] | None,
) -> pd.DataFrame:
    filtered = events.copy()
    if states:
        filtered = filtered[filtered["location_state"].isin(states)]
    if clients:
        filtered = filtered[filtered["client"].isin(clients)]
    if statuses:
        filtered = filtered[filtered["status"].isin(statuses)]
    if date_range is not None:
        start, end = date_range
        filtered = filtered[filtered["event_date"].between(start, end, inclusive="both")]
    return filtered


def mapped_table(events: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "event_number",
        "event_date",
        "client",
        "location_address",
        "location_city",
        "location_state",
        "status",
        "notes",
        "latitude",
        "longitude",
        "match_method",
    ]
    display = events[[column for column in columns if column in events]].copy()
    if "event_date" in display:
        display["event_date"] = display["event_date"].dt.strftime("%Y-%m-%d").fillna("")
    display.columns = [column.replace("_", " ").title() for column in display.columns]
    return display


def match_report_table(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    columns = [
        "event_number",
        "event_date",
        "client",
        "city",
        "state",
        "status",
        "location_key",
        "location_source_row",
        "location_source_rows",
        "candidate_location_key",
        "candidate_latitude",
        "candidate_longitude",
        "match_method",
        "match_reason",
    ]
    display = frame[[column for column in columns if column in frame]].copy()
    if "event_date" in display:
        display["event_date"] = display["event_date"].dt.strftime("%Y-%m-%d").fillna("")
    display.columns = [column.replace("_", " ").title() for column in display.columns]
    return display
