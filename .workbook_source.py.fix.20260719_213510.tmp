from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from posixpath import join, normpath
from typing import BinaryIO, Union
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

import pandas as pd


DATA_DIR = Path(__file__).parent / "data"
IMPORTS_DIR = DATA_DIR / "imports"
SUPPORTED_EXTENSIONS = {".xlsx"}

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"m": MAIN_NS, "r": REL_NS, "p": PACKAGE_REL_NS}


TIMELINE_ALIASES = {
    "event_number": {"visit", "visit number", "event", "event number", "service event number", "timeline position"},
    "event_date": {"date", "visit date", "event date", "service date"},
    "client": {"client", "client name", "organization"},
    "city": {"city", "location city"},
    "region_code": {"region code", "state code", "state abbreviation"},
    "state_region": {"state region", "state", "region", "jurisdiction"},
    "status": {"status", "visit status", "event status"},
    "notes": {"notes", "note", "description"},
    "latitude": {"latitude", "lat"},
    "longitude": {"longitude", "lon", "lng"},
    "service_type": {"service type", "service", "work type"},
    "project_name": {"project name", "project", "engagement"},
    "address": {"address", "street address", "service address", "location address", "site address"},
    "revenue": {
        "revenue",
        "revenue amount",
        "amount",
        "service revenue",
        "visit revenue",
        "ticket revenue",
        "invoice amount",
        "invoice total",
        "paid amount",
        "payment",
        "fee",
        "rate",
        "total revenue",
    },
}

CLIENT_ALIASES = {
    "client_number": {"client number", "client no", "client id"},
    "client": {"client", "client name", "organization"},
    "first_visit_number": {"first visit", "first visit number"},
    "first_visit_status": {"first visit status"},
    "completed_visits": {"completed visits", "visit count", "completed visit count"},
    "lifecycle": {"lifecycle", "status", "client status"},
    "category": {"category", "segment", "client category", "client segment"},
    "notes": {"notes", "note", "description"},
}

SCORECARD_ALIASES = {
    "metric": {"metric", "measure", "kpi"},
    "value": {"value", "result", "metric value"},
    "source": {"source formula", "source", "formula", "methodology"},
}

PIPELINE_ALIASES = {
    "event_number": {"visit", "visit number", "event", "event number", "service event number", "timeline position"},
    "client": {"client", "client name", "organization"},
    "location": {"location", "site", "city state", "city/state"},
    "event_date": {"date", "visit date", "event date", "service date", "date timing", "date / timing"},
    "status": {"status", "visit status", "event status"},
    "notes": {"notes", "note", "description"},
}
PIPELINE_COLUMNS = ["event_number", "client", "location", "event_date", "status", "notes"]

REQUIRED_COLUMNS = {
    "Timeline": {"event_number", "client", "status"},
    "Client List": {"client"},
    "Scorecard": {"metric", "value"},
}


@dataclass
class WorkbookData:
    path: Path
    sheet_names: list[str]
    row_counts: dict[str, int]
    timeline: pd.DataFrame
    clients: pd.DataFrame
    scorecard: pd.DataFrame
    pipeline: pd.DataFrame
    logic: pd.DataFrame
    validation: dict


def normalize_label(value: object) -> str:
    text = str(value or "").strip().lower().replace("&", " and ")
    text = re.sub(r"[#_/\\-]+", " ", text)
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", text)).strip()


def _column_index(reference: str) -> int:
    letters = "".join(character for character in reference if character.isalpha())
    index = 0
    for character in letters.upper():
        index = index * 26 + ord(character) - 64
    return index - 1


def _cell_value(cell: ET.Element, shared_strings: list[str]) -> object:
    cell_type = cell.attrib.get("t")
    value = cell.find("m:v", NS)
    raw = "" if value is None or value.text is None else value.text
    if cell_type == "s" and raw:
        return shared_strings[int(raw)]
    if cell_type == "inlineStr":
        inline = cell.find("m:is", NS)
        if inline is None:
            return ""
        return "".join(text.text or "" for text in inline.findall(".//m:t", NS))
    if cell_type in {"str", "d"}:
        return raw
    if cell_type == "b":
        return raw == "1"
    if raw == "":
        return ""
    try:
        number = float(raw)
        return int(number) if number.is_integer() else number
    except ValueError:
        return raw


def read_xlsx(source: Union[Path, bytes, BinaryIO]) -> dict[str, pd.DataFrame]:
    payload = BytesIO(source) if isinstance(source, bytes) else source
    try:
        archive = ZipFile(payload)
    except (BadZipFile, OSError) as error:
        raise ValueError("The selected file is not a valid .xlsx workbook") from error

    with archive:
        names = set(archive.namelist())
        if "xl/workbook.xml" not in names:
            raise ValueError("The workbook is missing its Excel workbook definition")

        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared_strings = [
                "".join(text.text or "" for text in item.findall(".//m:t", NS))
                for item in root.findall("m:si", NS)
            ]

        workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {relation.attrib["Id"]: relation.attrib["Target"] for relation in relationships_root}
        sheets: dict[str, pd.DataFrame] = {}

        for sheet in workbook_root.findall("m:sheets/m:sheet", NS):
            sheet_name = sheet.attrib["name"]
            relationship_id = sheet.attrib[f"{{{REL_NS}}}id"]
            raw_target = targets[relationship_id].lstrip("/")
            target = raw_target if raw_target.startswith("xl/") else normpath(join("xl", raw_target))
            sheet_root = ET.fromstring(archive.read(target))
            rows: list[list[object]] = []
            max_columns = 0

            for row in sheet_root.findall(".//m:sheetData/m:row", NS):
                values: dict[int, object] = {}
                for cell in row.findall("m:c", NS):
                    column = _column_index(cell.attrib.get("r", "A1"))
                    values[column] = _cell_value(cell, shared_strings)
                    max_columns = max(max_columns, column + 1)
                if values:
                    rows.append([values.get(column, "") for column in range(max_columns)])

            if not rows:
                sheets[sheet_name] = pd.DataFrame()
                continue
            width = max(len(row) for row in rows)
            padded = [row + [""] * (width - len(row)) for row in rows]
            headers = [str(value).strip() or f"Column {index + 1}" for index, value in enumerate(padded[0])]
            frame = pd.DataFrame(padded[1:], columns=headers)
            frame = frame.loc[~frame.apply(lambda row: all(str(value).strip() == "" for value in row), axis=1)]
            sheets[sheet_name] = frame.reset_index(drop=True)

        return sheets


def _find_sheet(sheets: dict[str, pd.DataFrame], names: set[str]) -> tuple[str, pd.DataFrame]:
    normalized = {normalize_label(name): name for name in sheets}
    for candidate in names:
        actual = normalized.get(normalize_label(candidate))
        if actual:
            return actual, sheets[actual].copy()
    return "", pd.DataFrame()


def _canonicalize_columns(frame: pd.DataFrame, aliases: dict[str, set[str]]) -> pd.DataFrame:
    if frame.empty and not len(frame.columns):
        return frame
    alias_lookup = {
        normalize_label(alias): canonical
        for canonical, options in aliases.items()
        for alias in options | {canonical}
    }
    renamed = {}
    used = set()
    for column in frame.columns:
        raw_label = str(column).strip().lower()
        normalized = normalize_label(column)
        if aliases is CLIENT_ALIASES and (raw_label.startswith("client #") or normalized in {"client number", "client no", "client id"}):
            canonical = "client_number"
        else:
            canonical = alias_lookup.get(normalized, normalized.replace(" ", "_"))
        if canonical in used:
            canonical = f"{canonical}_extra"
        renamed[column] = canonical
        used.add(canonical)
    return frame.rename(columns=renamed)


def empty_pipeline_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=PIPELINE_COLUMNS)


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _event_dates(series: pd.Series) -> pd.Series:
    dates = pd.to_datetime(series, errors="coerce")
    numeric = pd.to_numeric(series, errors="coerce")
    excel_serials = numeric.between(20000, 80000)
    if excel_serials.any():
        dates.loc[excel_serials] = pd.to_datetime(
            numeric.loc[excel_serials], unit="D", origin="1899-12-30", errors="coerce"
        )
    return dates


def _scorecard_values(scorecard: pd.DataFrame) -> dict[str, object]:
    if not {"metric", "value"}.issubset(scorecard.columns):
        return {}
    return {
        normalize_label(row.metric): row.value
        for row in scorecard[["metric", "value"]].itertuples(index=False)
        if str(row.metric).strip()
    }


def scorecard_metric(scorecard: pd.DataFrame, *names: str, fallback: object = None) -> object:
    values = _scorecard_values(scorecard)
    for name in names:
        key = normalize_label(name)
        if key in values and str(values[key]).strip() != "":
            return values[key]
    return fallback


def _as_count(value: object, fallback: int) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return fallback


def find_source_workbook() -> Path | None:
    """
    Return the authoritative legacy dashboard workbook.

    Career Analytics uses data/current_master.xlsx directly and must never
    become the global workbook for the existing dashboard pages.
    """
    preferred = DATA_DIR / "Barrister_Master.xlsx"
    if preferred.is_file():
        return preferred

    IMPORTS_DIR.mkdir(parents=True, exist_ok=True)

    def eligible(path: Path) -> bool:
        return (
            path.is_file()
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
            and not path.name.startswith("~$")
            and path.name != "current_master.xlsx"
        )

    imported = [path for path in IMPORTS_DIR.iterdir() if eligible(path)]
    if imported:
        return max(imported, key=lambda path: (path.stat().st_mtime_ns, path.name))

    root_files = [path for path in DATA_DIR.iterdir() if eligible(path)]
    return (
        max(root_files, key=lambda path: (path.stat().st_mtime_ns, path.name))
        if root_files
        else None
    )

def workbook_version(path: Path) -> tuple[str, int, int]:
    stat = path.stat()
    return str(path), stat.st_mtime_ns, stat.st_size


def load_workbook(path: Path) -> WorkbookData:
    sheets = read_xlsx(path)
    timeline_name, timeline_raw = _find_sheet(sheets, {"Timeline"})
    clients_name, clients_raw = _find_sheet(sheets, {"Client List", "Clients"})
    scorecard_name, scorecard_raw = _find_sheet(sheets, {"Scorecard"})
    pipeline_name, pipeline_raw = _find_sheet(sheets, {"Pipeline", "Upcoming", "Upcoming Assignments"})
    logic_name, logic_raw = _find_sheet(sheets, {"Logic", "Rules & Governance", "Rules and Governance", "Methodology"})

    timeline = _canonicalize_columns(timeline_raw, TIMELINE_ALIASES)
    clients = _canonicalize_columns(clients_raw, CLIENT_ALIASES)
    scorecard = _canonicalize_columns(scorecard_raw, SCORECARD_ALIASES)
    pipeline = _canonicalize_columns(pipeline_raw, PIPELINE_ALIASES)
    if pipeline.empty and not len(pipeline.columns):
        pipeline = empty_pipeline_frame()
    else:
        for column in PIPELINE_COLUMNS:
            if column not in pipeline:
                pipeline[column] = ""
    logic = logic_raw.copy()

    if "event_number" in timeline:
        timeline["event_number"] = _numeric(timeline["event_number"])
        timeline = timeline[timeline["event_number"].notna()].copy()
    if "event_date" in timeline:
        timeline["event_date"] = _event_dates(timeline["event_date"])
    if "status" in timeline:
        timeline["status"] = timeline["status"].fillna("").astype(str).str.strip().str.title()
    if "client" in timeline:
        timeline["client"] = timeline["client"].fillna("").astype(str).str.strip()
    if "completed_visits" in clients:
        clients["completed_visits"] = _numeric(clients["completed_visits"]).fillna(0).astype(int)
    if "client" in clients:
        clients["client"] = clients["client"].fillna("").astype(str).str.strip()
    if "status" in pipeline:
        pipeline["status"] = pipeline["status"].fillna("").astype(str).str.strip().str.title()
    if "client" in pipeline:
        pipeline["client"] = pipeline["client"].fillna("").astype(str).str.strip()
    if "location" in pipeline:
        pipeline["location"] = pipeline["location"].fillna("").astype(str).str.strip()

    missing_columns = {}
    for expected_name, frame in (("Timeline", timeline), ("Client List", clients), ("Scorecard", scorecard)):
        missing = sorted(REQUIRED_COLUMNS[expected_name].difference(frame.columns))
        if missing:
            missing_columns[expected_name] = missing

    duplicate_numbers: list[object] = []
    if "event_number" in timeline:
        duplicate_numbers = timeline.loc[timeline["event_number"].duplicated(keep=False), "event_number"].dropna().unique().tolist()

    completed_events = 0
    if "status" in timeline:
        completed_events = int(timeline["status"].eq("Completed").sum())
    service_event_count = _as_count(
        scorecard_metric(scorecard, "Completed Service Events", fallback=completed_events),
        completed_events,
    )
    unique_client_count = int(clients["client"].replace("", pd.NA).nunique()) if "client" in clients else 0
    repeat_client_count = None
    if "completed_visits" in clients:
        repeat_client_count = int(clients["completed_visits"].gt(1).sum())

    validation = {
        "detected_tabs": list(sheets),
        "resolved_tabs": {
            "Timeline": timeline_name,
            "Client List": clients_name,
            "Scorecard": scorecard_name,
            "Pipeline": pipeline_name,
            "Logic": logic_name,
        },
        "row_counts": {name: len(frame) for name, frame in sheets.items()},
        "service_event_count": service_event_count,
        "unique_client_count": unique_client_count,
        "repeat_client_count": repeat_client_count,
        "missing_required_tabs": [
            name for name, actual in (("Timeline", timeline_name), ("Client List", clients_name), ("Scorecard", scorecard_name))
            if not actual
        ],
        "missing_required_columns": missing_columns,
        "duplicate_event_numbers": duplicate_numbers,
    }

    return WorkbookData(
        path=path,
        sheet_names=list(sheets),
        row_counts=validation["row_counts"],
        timeline=timeline.reset_index(drop=True),
        clients=clients.reset_index(drop=True),
        scorecard=scorecard.reset_index(drop=True),
        pipeline=pipeline.reset_index(drop=True),
        logic=logic.reset_index(drop=True),
        validation=validation,
    )
