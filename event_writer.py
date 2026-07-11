from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from posixpath import join, normpath
import re
import tempfile
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd

from workbook_source import (
    CLIENT_ALIASES,
    MAIN_NS,
    NS,
    PIPELINE_COLUMNS,
    PIPELINE_ALIASES,
    REL_NS,
    SCORECARD_ALIASES,
    TIMELINE_ALIASES,
    WorkbookData,
    load_workbook,
    normalize_label,
    read_xlsx,
)


ET.register_namespace("", MAIN_NS)
ET.register_namespace("r", REL_NS)


STATE_NAMES = {
    "MD": "Maryland",
    "VA": "Virginia",
    "DC": "Washington, D.C.",
    "PA": "Pennsylvania",
}
STATE_CODES = {
    **{code: code for code in STATE_NAMES},
    "MARYLAND": "MD",
    "VIRGINIA": "VA",
    "WASHINGTON DC": "DC",
    "WASHINGTON D C": "DC",
    "DISTRICT OF COLUMBIA": "DC",
    "PENNSYLVANIA": "PA",
}

PIPELINE_HEADERS = ["Visit #", "Client", "Location", "Date / Timing", "Status", "Notes"]


@dataclass
class ParsedLocation:
    city: str
    region_code: str
    state_region: str


@dataclass
class ServiceEventDraft:
    client: str
    city: str
    region_code: str
    state_region: str
    event_date: date
    notes: str
    status: str = "Completed"
    event_number: int | None = None
    existing_client: bool = False


@dataclass
class SavedServiceEvent:
    event_number: int | None
    client: str
    city: str
    region_code: str
    state_region: str
    event_date: date
    status: str
    notes: str
    existing_client: bool
    completed_visits: int | None


def parse_location(value: str) -> ParsedLocation:
    text = re.sub(r"\s+", " ", str(value or "").strip())
    if not text:
        raise ValueError("Enter a location such as Lanham, MD.")

    if "," in text:
        city, raw_state = [part.strip() for part in text.rsplit(",", 1)]
    else:
        match = re.match(r"^(.+?)\s+([A-Za-z.]{2,})$", text)
        if not match:
            raise ValueError("Use City, ST format, for example Lanham, MD.")
        city, raw_state = match.group(1).strip(), match.group(2).strip()

    state_key = re.sub(r"[^A-Za-z]+", " ", raw_state).strip().upper()
    region_code = STATE_CODES.get(state_key)
    if not city or not region_code:
        raise ValueError("Supported regions: MD · VA · DC · PA · WV · DE · WV · DE")
    return ParsedLocation(city=city, region_code=region_code, state_region=STATE_NAMES[region_code])


def next_visit_number(data: WorkbookData) -> int:
    if data.timeline.empty or "event_number" not in data.timeline:
        return 1
    completed = data.timeline[data.timeline.get("status", pd.Series(dtype=str)).eq("Completed")]
    numbers = pd.to_numeric(completed.get("event_number", pd.Series(dtype=float)), errors="coerce").dropna()
    return int(numbers.max()) + 1 if not numbers.empty else 1


def resolve_client_name(data: WorkbookData, client: str) -> tuple[str, bool]:
    requested = re.sub(r"\s+", " ", str(client or "").strip())
    if not requested:
        raise ValueError("Enter a client name.")
    existing = {
        str(value).strip().casefold(): str(value).strip()
        for value in data.clients.get("client", pd.Series(dtype=str)).dropna()
        if str(value).strip()
    }
    match = existing.get(requested.casefold())
    return (match, True) if match else (requested, False)


def build_service_event_draft(
    data: WorkbookData,
    client: str,
    location: str,
    event_date: date,
    notes: str,
    status: str = "Completed",
) -> ServiceEventDraft:
    resolved_client, existing_client = resolve_client_name(data, client)
    parsed = parse_location(location)
    normalized_status = str(status or "Completed").strip().title()
    if normalized_status not in {"Completed", "Scheduled"}:
        raise ValueError("Status must be Completed or Scheduled.")
    return ServiceEventDraft(
        client=resolved_client,
        city=parsed.city,
        region_code=parsed.region_code,
        state_region=parsed.state_region,
        event_date=event_date,
        notes=str(notes or "").strip(),
        status=normalized_status,
        event_number=next_visit_number(data) if normalized_status == "Completed" else None,
        existing_client=existing_client,
    )


def _column_letter(index: int) -> str:
    number = index + 1
    letters = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def _cell_reference(column_index: int, row_number: int) -> str:
    return f"{_column_letter(column_index)}{row_number}"


def _cell_column_index(reference: str) -> int:
    letters = "".join(character for character in reference if character.isalpha())
    index = 0
    for character in letters.upper():
        index = index * 26 + ord(character) - 64
    return index - 1


def _set_cell_value(cell: ET.Element, value: object) -> None:
    for child in list(cell):
        cell.remove(child)
    for attr in ("t",):
        cell.attrib.pop(attr, None)

    if value is None or value == "":
        return
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        value_node = ET.SubElement(cell, f"{{{MAIN_NS}}}v")
        value_node.text = str(value)
        return

    cell.set("t", "inlineStr")
    inline = ET.SubElement(cell, f"{{{MAIN_NS}}}is")
    text = ET.SubElement(inline, f"{{{MAIN_NS}}}t")
    text.text = value.isoformat() if isinstance(value, date) else str(value)


def _make_cell(column_index: int, row_number: int, value: object) -> ET.Element:
    cell = ET.Element(f"{{{MAIN_NS}}}c", {"r": _cell_reference(column_index, row_number)})
    _set_cell_value(cell, value)
    return cell


def _cells_by_column(row: ET.Element) -> dict[int, ET.Element]:
    return {
        _cell_column_index(cell.attrib.get("r", "A1")): cell
        for cell in row.findall("m:c", NS)
    }


def _set_row_value(row: ET.Element, column_index: int, value: object) -> None:
    cells = _cells_by_column(row)
    cell = cells.get(column_index)
    if cell is None:
        cell = _make_cell(column_index, int(row.attrib["r"]), value)
        inserted = False
        for existing in list(row):
            if _cell_column_index(existing.attrib.get("r", "A1")) > column_index:
                row.insert(list(row).index(existing), cell)
                inserted = True
                break
        if not inserted:
            row.append(cell)
    else:
        _set_cell_value(cell, value)


def _append_row(sheet_root: ET.Element, values: list[object]) -> int:
    sheet_data = sheet_root.find("m:sheetData", NS)
    if sheet_data is None:
        sheet_data = ET.SubElement(sheet_root, f"{{{MAIN_NS}}}sheetData")
    existing_rows = sheet_data.findall("m:row", NS)
    row_number = max((int(row.attrib.get("r", "0")) for row in existing_rows), default=0) + 1
    row = ET.Element(f"{{{MAIN_NS}}}row", {"r": str(row_number)})
    for index, value in enumerate(values):
        if value not in ("", None):
            row.append(_make_cell(index, row_number, value))
    sheet_data.append(row)
    _update_dimension(sheet_root, len(values), row_number)
    return row_number


def _update_dimension(sheet_root: ET.Element, column_count: int, row_count: int) -> None:
    dimension = sheet_root.find("m:dimension", NS)
    ref = f"A1:{_column_letter(max(column_count - 1, 0))}{max(row_count, 1)}"
    if dimension is None:
        dimension = ET.Element(f"{{{MAIN_NS}}}dimension", {"ref": ref})
        sheet_root.insert(0, dimension)
    else:
        dimension.set("ref", ref)


def _replace_sheet_table(sheet_root: ET.Element, headers: list[str], rows: list[list[object]]) -> None:
    sheet_data = sheet_root.find("m:sheetData", NS)
    if sheet_data is None:
        sheet_data = ET.SubElement(sheet_root, f"{{{MAIN_NS}}}sheetData")
    for child in list(sheet_data):
        sheet_data.remove(child)
    for row_index, values in enumerate([headers, *rows], start=1):
        row = ET.Element(f"{{{MAIN_NS}}}row", {"r": str(row_index)})
        for column_index, value in enumerate(values):
            if value not in ("", None):
                row.append(_make_cell(column_index, row_index, value))
        sheet_data.append(row)
    _update_dimension(sheet_root, len(headers), len(rows) + 1)


def replace_workbook_sheet_table(path: Path, sheet_name: str, frame: pd.DataFrame) -> None:
    editor = WorkbookXmlEditor(Path(path))
    if sheet_name not in editor.sheet_paths:
        raise ValueError(f"{sheet_name} sheet was not found in the active workbook.")
    headers = [str(column) for column in frame.columns]
    rows: list[list[object]] = []
    for record in frame.to_dict("records"):
        values = []
        for header in headers:
            value = record.get(header, "")
            if pd.isna(value):
                value = ""
            elif hasattr(value, "date"):
                value = value.date()
            values.append(value)
        rows.append(values)
    root = editor.sheet_root(sheet_name)
    _replace_sheet_table(root, headers, rows)
    editor.set_sheet_root(sheet_name, root)
    editor.save()


def _canonical_column(headers: list[str], aliases: dict[str, set[str]], canonical: str) -> int | None:
    accepted = {normalize_label(canonical), *(normalize_label(alias) for alias in aliases.get(canonical, set()))}
    for index, header in enumerate(headers):
        if normalize_label(header) in accepted:
            return index
    return None


def _canonical_name(header: str, aliases: dict[str, set[str]]) -> str:
    normalized = normalize_label(header)
    for canonical, options in aliases.items():
        accepted = {normalize_label(canonical), *(normalize_label(alias) for alias in options)}
        if normalized in accepted:
            return canonical
    return normalized.replace(" ", "_")


def _metric_row(frame: pd.DataFrame, metric: str) -> int | None:
    if "Metric" not in frame:
        return None
    normalized = normalize_label(metric)
    matches = frame.index[frame["Metric"].fillna("").map(normalize_label).eq(normalized)].tolist()
    return int(matches[0]) if matches else None


class WorkbookXmlEditor:
    def __init__(self, path: Path):
        self.path = path
        with ZipFile(path, "r") as archive:
            self.files = {name: archive.read(name) for name in archive.namelist()}
        workbook_root = ET.fromstring(self.files["xl/workbook.xml"])
        relationships_root = ET.fromstring(self.files["xl/_rels/workbook.xml.rels"])
        targets = {relation.attrib["Id"]: relation.attrib["Target"] for relation in relationships_root}
        self.sheet_paths: dict[str, str] = {}
        for sheet in workbook_root.findall("m:sheets/m:sheet", NS):
            raw_target = targets[sheet.attrib[f"{{{REL_NS}}}id"]].lstrip("/")
            target = raw_target if raw_target.startswith("xl/") else normpath(join("xl", raw_target))
            self.sheet_paths[sheet.attrib["name"]] = target
        self.modified: dict[str, bytes] = {}

    def sheet_root(self, sheet_name: str) -> ET.Element:
        return ET.fromstring(self.files[self.sheet_paths[sheet_name]])

    def set_sheet_root(self, sheet_name: str, root: ET.Element) -> None:
        self.modified[self.sheet_paths[sheet_name]] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    def save(self) -> None:
        with tempfile.NamedTemporaryFile(dir=self.path.parent, suffix=".xlsx", delete=False) as handle:
            temporary_path = Path(handle.name)
        try:
            with ZipFile(temporary_path, "w", ZIP_DEFLATED) as archive:
                for name, payload in self.files.items():
                    archive.writestr(name, self.modified.get(name, payload))
            temporary_path.replace(self.path)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise


def _append_timeline(editor: WorkbookXmlEditor, draft: ServiceEventDraft, raw_timeline: pd.DataFrame) -> None:
    headers = [str(column) for column in raw_timeline.columns]
    date_index = _canonical_column(headers, TIMELINE_ALIASES, "event_date")
    root = editor.sheet_root("Timeline")
    if date_index is None:
        headers.append("Date")
        date_index = len(headers) - 1
        header_row = root.find("m:sheetData/m:row[@r='1']", NS)
        if header_row is not None:
            _set_row_value(header_row, date_index, "Date")

    values = [""] * len(headers)
    assignments = {
        "event_number": draft.event_number,
        "client": draft.client,
        "city": draft.city,
        "region_code": draft.region_code,
        "state_region": draft.state_region,
        "status": draft.status,
        "notes": draft.notes,
        "event_date": draft.event_date,
    }
    for canonical, value in assignments.items():
        index = date_index if canonical == "event_date" else _canonical_column(headers, TIMELINE_ALIASES, canonical)
        if index is not None:
            values[index] = value
    _append_row(root, values)
    editor.set_sheet_root("Timeline", root)


def _pipeline_headers(raw_pipeline: pd.DataFrame) -> list[str]:
    headers = [str(column) for column in raw_pipeline.columns]
    required = {"client", "location", "event_date", "status", "notes"}
    canonical_headers = {_canonical_name(header, PIPELINE_ALIASES) for header in headers}
    if not headers or not required.issubset(canonical_headers):
        return PIPELINE_HEADERS.copy()
    return headers


def _pipeline_record_value(record: dict, header: str) -> object:
    canonical = _canonical_name(header, PIPELINE_ALIASES)
    value = record.get(header, record.get(canonical, ""))
    return "" if pd.isna(value) else value


def _replace_timeline_completed(
    editor: WorkbookXmlEditor,
    raw_timeline: pd.DataFrame,
    completed_timeline: pd.DataFrame,
) -> None:
    headers = [str(column) for column in raw_timeline.columns]
    root = editor.sheet_root("Timeline")
    if not headers:
        headers = ["Visit #", "Client", "City", "Region Code", "State/Region", "Status", "Notes", "Date"]

    event_index = _canonical_column(headers, TIMELINE_ALIASES, "event_number")
    if event_index is None:
        headers.insert(0, "Visit #")
        event_index = 0
    rows = []
    completed = _renumber_completed_timeline(completed_timeline)
    for record in completed.to_dict("records"):
        values = [""] * len(headers)
        assignments = {
            "event_number": record.get("event_number", ""),
            "event_date": record.get("event_date", ""),
            "client": record.get("client", ""),
            "city": record.get("city", ""),
            "region_code": record.get("region_code", ""),
            "state_region": record.get("state_region", ""),
            "status": "Completed",
            "notes": record.get("notes", ""),
        }
        assigned_indexes = set()
        for canonical, value in assignments.items():
            index = _canonical_column(headers, TIMELINE_ALIASES, canonical)
            if index is not None:
                if canonical == "event_date" and pd.isna(value):
                    value = ""
                elif canonical == "event_date" and hasattr(value, "date"):
                    value = value.date()
                values[index] = value
                assigned_indexes.add(index)
        for index, header in enumerate(headers):
            if index in assigned_indexes:
                continue
            canonical = _canonical_name(header, TIMELINE_ALIASES)
            value = record.get(canonical, "")
            if pd.isna(value):
                value = ""
            elif hasattr(value, "date"):
                value = value.date()
            values[index] = value
        rows.append(values)
    _replace_sheet_table(root, headers, rows)
    editor.set_sheet_root("Timeline", root)


def _renumber_completed_timeline(completed_timeline: pd.DataFrame) -> pd.DataFrame:
    completed = completed_timeline.copy()
    if completed.empty:
        return completed
    completed["_sort_number"] = pd.to_numeric(completed.get("event_number", pd.Series(dtype=float)), errors="coerce")
    completed = completed.sort_values(["_sort_number", "client"], na_position="last").reset_index(drop=True)
    completed["event_number"] = range(1, len(completed) + 1)
    return completed.drop(columns=["_sort_number"])


def _append_pipeline(editor: WorkbookXmlEditor, draft: ServiceEventDraft, raw_pipeline: pd.DataFrame) -> None:
    if "Pipeline" not in editor.sheet_paths:
        raise ValueError("Pipeline sheet is required for scheduled assignments.")
    headers = _pipeline_headers(raw_pipeline)
    root = editor.sheet_root("Pipeline")
    values = [""] * len(headers)
    assignments = {
        "event_number": "",
        "client": draft.client,
        "location": f"{draft.city}, {draft.region_code}",
        "event_date": draft.event_date,
        "status": "Scheduled",
        "notes": draft.notes,
    }
    for canonical, value in assignments.items():
        index = _canonical_column(headers, PIPELINE_ALIASES, canonical)
        if index is not None:
            values[index] = value
    _append_row(root, values)
    editor.set_sheet_root("Pipeline", root)


def _remove_pipeline_row(editor: WorkbookXmlEditor, raw_pipeline: pd.DataFrame, pipeline_index: int) -> None:
    if "Pipeline" not in editor.sheet_paths:
        return
    headers = _pipeline_headers(raw_pipeline)
    if pipeline_index < 0 or pipeline_index >= len(raw_pipeline):
        raise ValueError("Scheduled assignment could not be found.")

    remaining = raw_pipeline.drop(raw_pipeline.index[pipeline_index]).copy()
    rows = []
    for record in remaining.to_dict("records"):
        rows.append([_pipeline_record_value(record, header) for header in headers])

    root = editor.sheet_root("Pipeline")
    _replace_sheet_table(root, headers, rows)
    editor.set_sheet_root("Pipeline", root)


def _pipeline_row_values(headers: list[str], draft: ServiceEventDraft) -> list[object]:
    values = [""] * len(headers)
    assignments = {
        "event_number": "",
        "client": draft.client,
        "location": f"{draft.city}, {draft.region_code}",
        "event_date": draft.event_date,
        "status": draft.status,
        "notes": draft.notes,
    }
    for canonical, value in assignments.items():
        index = _canonical_column(headers, PIPELINE_ALIASES, canonical)
        if index is not None:
            values[index] = value
    return values


def _replace_pipeline_rows(
    editor: WorkbookXmlEditor,
    raw_pipeline: pd.DataFrame,
    remove_index: int | None = None,
    append_draft: ServiceEventDraft | None = None,
) -> None:
    if "Pipeline" not in editor.sheet_paths:
        if append_draft is not None:
            raise ValueError("Pipeline sheet is required for scheduled assignments.")
        return

    headers = _pipeline_headers(raw_pipeline)

    remaining = raw_pipeline.copy()
    if remove_index is not None:
        if remove_index < 0 or remove_index >= len(raw_pipeline):
            raise ValueError("Scheduled assignment could not be found.")
        remaining = remaining.drop(raw_pipeline.index[remove_index]).copy()

    rows = []
    for record in remaining.to_dict("records"):
        rows.append([_pipeline_record_value(record, header) for header in headers])
    if append_draft is not None:
        rows.append(_pipeline_row_values(headers, append_draft))

    root = editor.sheet_root("Pipeline")
    _replace_sheet_table(root, headers, rows)
    editor.set_sheet_root("Pipeline", root)


def _update_client_list(
    editor: WorkbookXmlEditor,
    draft: ServiceEventDraft,
    raw_clients: pd.DataFrame,
    data: WorkbookData,
) -> int:
    headers = [str(column) for column in raw_clients.columns]
    root = editor.sheet_root("Client List")
    client_index = _canonical_column(headers, CLIENT_ALIASES, "client")
    visits_index = _canonical_column(headers, CLIENT_ALIASES, "completed_visits")
    lifecycle_index = _canonical_column(headers, CLIENT_ALIASES, "lifecycle")
    notes_index = _canonical_column(headers, CLIENT_ALIASES, "notes")
    first_visit_index = _canonical_column(headers, CLIENT_ALIASES, "first_visit_number")
    first_status_index = _canonical_column(headers, CLIENT_ALIASES, "first_visit_status")
    client_number_index = _canonical_column(headers, CLIENT_ALIASES, "client_number")
    if client_index is None:
        raise ValueError("Client List is missing a Client column.")

    clients = data.clients.copy()
    match = clients.index[clients["client"].astype(str).str.casefold().eq(draft.client.casefold())].tolist()
    if match:
        frame_index = int(match[0])
        current_visits = int(clients.loc[frame_index, "completed_visits"]) if "completed_visits" in clients else 0
        updated_visits = current_visits + 1
        sheet_row = root.find(f"m:sheetData/m:row[@r='{frame_index + 2}']", NS)
        if sheet_row is None:
            raise ValueError("Unable to locate the matching Client List row.")
        if visits_index is not None:
            _set_row_value(sheet_row, visits_index, updated_visits)
        if lifecycle_index is not None:
            _set_row_value(sheet_row, lifecycle_index, "Repeat" if updated_visits > 1 else "Completed")
        if notes_index is not None and updated_visits > 1:
            _set_row_value(sheet_row, notes_index, "Repeat")
        editor.set_sheet_root("Client List", root)
        return updated_visits

    next_client_number = 1
    if "client_number" in clients:
        numeric = pd.to_numeric(clients["client_number"], errors="coerce").dropna()
        if not numeric.empty:
            next_client_number = int(numeric.max()) + 1

    values = [""] * len(headers)
    assignments = {
        client_number_index: next_client_number,
        client_index: draft.client,
        first_visit_index: draft.event_number,
        first_status_index: draft.status,
        visits_index: 1,
        lifecycle_index: "Completed",
        notes_index: "Single",
    }
    for index, value in assignments.items():
        if index is not None:
            values[index] = value
    _append_row(root, values)
    editor.set_sheet_root("Client List", root)
    return 1


def _ensure_client_header(headers: list[str], aliases: dict[str, set[str]], canonical: str, label: str) -> int:
    index = _canonical_column(headers, aliases, canonical)
    if index is None:
        headers.append(label)
        index = len(headers) - 1
    return index


def _replace_client_list_from_timeline(
    editor: WorkbookXmlEditor,
    raw_clients: pd.DataFrame,
    data: WorkbookData,
    completed_timeline: pd.DataFrame,
) -> pd.DataFrame:
    if "Client List" not in editor.sheet_paths:
        return data.clients.copy()

    headers = [str(column) for column in raw_clients.columns]
    if not headers:
        headers = ["Client", "Completed Visits", "Lifecycle", "First Visit", "First Visit Status", "Notes"]

    client_index = _ensure_client_header(headers, CLIENT_ALIASES, "client", "Client")
    visits_index = _ensure_client_header(headers, CLIENT_ALIASES, "completed_visits", "Completed Visits")
    lifecycle_index = _ensure_client_header(headers, CLIENT_ALIASES, "lifecycle", "Lifecycle")
    first_visit_index = _ensure_client_header(headers, CLIENT_ALIASES, "first_visit_number", "First Visit")
    first_status_index = _ensure_client_header(headers, CLIENT_ALIASES, "first_visit_status", "First Visit Status")
    notes_index = _ensure_client_header(headers, CLIENT_ALIASES, "notes", "Notes")

    completed = _renumber_completed_timeline(completed_timeline)
    completed = completed[completed.get("client", pd.Series(dtype=str)).fillna("").astype(str).str.strip().ne("")].copy()
    counts: dict[str, dict[str, object]] = {}
    if not completed.empty:
        for client, group in completed.groupby("client", sort=False):
            numbers = pd.to_numeric(group["event_number"], errors="coerce").dropna().astype(int)
            visits = int(len(group))
            first_visit = int(numbers.min()) if not numbers.empty else ""
            counts[str(client).casefold()] = {
                "client": str(client),
                "completed_visits": visits,
                "first_visit_number": first_visit,
                "first_visit_status": "Completed" if visits else "",
                "lifecycle": "Repeat" if visits > 1 else "Completed",
                "notes": "Repeat" if visits > 1 else "Single",
            }

    raw_records: dict[str, list[object]] = {}
    client_order: list[str] = []
    for record in raw_clients.to_dict("records"):
        values = ["" if pd.isna(record.get(column, "")) else record.get(column, "") for column in raw_clients.columns]
        values.extend([""] * (len(headers) - len(values)))
        client = str(values[client_index] or "").strip()
        if not client:
            continue
        key = client.casefold()
        if key not in raw_records:
            raw_records[key] = values
            client_order.append(key)

    for key in counts:
        if key not in raw_records:
            raw_records[key] = [""] * len(headers)
            raw_records[key][client_index] = counts[key]["client"]
            client_order.append(key)

    rows = []
    client_rows = []
    for key in client_order:
        values = list(raw_records[key])
        values.extend([""] * (len(headers) - len(values)))
        client_name = str(values[client_index] or counts.get(key, {}).get("client", "")).strip()
        count = counts.get(key)
        if count is not None:
            client_name = str(count["client"])
            values[client_index] = client_name
            values[visits_index] = count["completed_visits"]
            values[first_visit_index] = count["first_visit_number"]
            values[first_status_index] = count["first_visit_status"]
            values[lifecycle_index] = count["lifecycle"]
            values[notes_index] = count["notes"]
            completed_visits = int(count["completed_visits"])
            lifecycle = str(count["lifecycle"])
            first_visit = count["first_visit_number"]
        else:
            values[visits_index] = 0
            completed_visits = 0
            lifecycle = str(values[lifecycle_index] or "")
            first_visit = values[first_visit_index]
        rows.append(values[:len(headers)])
        client_rows.append(
            {
                "client": client_name,
                "completed_visits": completed_visits,
                "first_visit_number": first_visit,
                "first_visit_status": values[first_status_index],
                "lifecycle": lifecycle,
                "notes": values[notes_index],
            }
        )

    root = editor.sheet_root("Client List")
    _replace_sheet_table(root, headers, rows)
    editor.set_sheet_root("Client List", root)
    return pd.DataFrame(client_rows)


def _scorecard_updates(timeline: pd.DataFrame, clients: pd.DataFrame) -> dict[str, object]:
    completed = timeline[timeline["status"].eq("Completed")]
    unique_completed = clients[clients["completed_visits"].gt(0)]["client"].nunique()
    jurisdictions = completed["state_region"].replace("", pd.NA).dropna().nunique()
    return {
        "Completed Service Events": int(len(completed)),
        "Scheduled Timeline Entries": 0,
        "Total Timeline Positions": int(len(completed)),
        "Completed Unique Clients": int(unique_completed),
        "Forward-Looking Client Count": int(clients["client"].replace("", pd.NA).nunique()),
        "Jurisdictions Covered": int(jurisdictions),
    }


def _update_scorecard(editor: WorkbookXmlEditor, raw_scorecard: pd.DataFrame, updates: dict[str, object]) -> None:
    if raw_scorecard.empty:
        return
    headers = [str(column) for column in raw_scorecard.columns]
    value_index = _canonical_column(headers, SCORECARD_ALIASES, "value")
    source_index = _canonical_column(headers, SCORECARD_ALIASES, "source")
    if value_index is None:
        return
    root = editor.sheet_root("Scorecard")
    for metric, value in updates.items():
        row_index = _metric_row(raw_scorecard, metric)
        if row_index is None:
            continue
        row = root.find(f"m:sheetData/m:row[@r='{row_index + 2}']", NS)
        if row is None:
            continue
        _set_row_value(row, value_index, value)
        if source_index is not None and isinstance(value, int):
            _set_row_value(row, source_index, value)
    editor.set_sheet_root("Scorecard", root)


def _replace_repeat_clients(editor: WorkbookXmlEditor, timeline: pd.DataFrame) -> None:
    if "Repeat Clients" not in editor.sheet_paths:
        return
    completed = timeline[timeline["status"].eq("Completed")].copy()
    grouped = completed.groupby("client", dropna=True)
    rows = []
    for client, group in grouped:
        visits = len(group)
        if visits <= 1:
            continue
        numbers = pd.to_numeric(group["event_number"], errors="coerce").dropna().astype(int).sort_values().tolist()
        rows.append([client, visits, ", ".join(str(number) for number in numbers)])
    rows.sort(key=lambda row: (-row[1], str(row[0]).casefold()))
    root = editor.sheet_root("Repeat Clients")
    _replace_sheet_table(root, ["Client", "Completed Visits", "Visit Numbers"], rows)
    editor.set_sheet_root("Repeat Clients", root)


def _replace_state_coverage(editor: WorkbookXmlEditor, timeline: pd.DataFrame) -> None:
    if "State Coverage" not in editor.sheet_paths:
        return
    states = []
    preferred = ["Maryland", "Washington, D.C.", "Virginia", "Pennsylvania"]
    for state in preferred + sorted(timeline["state_region"].dropna().unique(), key=str.casefold):
        if state and state not in states:
            states.append(state)
    rows = []
    for state in states:
        state_rows = timeline[timeline["state_region"].eq(state)]
        if state_rows.empty:
            continue
        completed = int(state_rows["status"].eq("Completed").sum())
        scheduled = int(state_rows["status"].eq("Scheduled").sum())
        rows.append([state, completed, scheduled, int(len(state_rows))])
    rows.sort(key=lambda row: (-row[1], str(row[0]).casefold()))
    root = editor.sheet_root("State Coverage")
    _replace_sheet_table(root, ["State/Region", "Completed Visits", "Scheduled Visits", "Total Timeline Entries"], rows)
    editor.set_sheet_root("State Coverage", root)


def _update_validation(editor: WorkbookXmlEditor, raw_validation: pd.DataFrame, updates: dict[str, object]) -> None:
    if "Validation" not in editor.sheet_paths or raw_validation.empty or "Check" not in raw_validation:
        return
    headers = [str(column) for column in raw_validation.columns]
    expected_index = next((i for i, header in enumerate(headers) if normalize_label(header) == "expected"), None)
    formula_index = next((i for i, header in enumerate(headers) if normalize_label(header) == "formula value"), None)
    if expected_index is None:
        return
    root = editor.sheet_root("Validation")
    validation_map = {
        "Completed Service Events": "Completed Service Events",
        "Completed Unique Clients": "Completed Unique Clients",
        "Forward-Looking Client Count": "Forward-Looking Client Count",
        "Timeline Max Position": "Total Timeline Positions",
        "Scheduled Timeline Entries": "Scheduled Timeline Entries",
    }
    for row_index, row in raw_validation.iterrows():
        metric = validation_map.get(str(row.get("Check", "")).strip())
        if metric is None or metric not in updates:
            continue
        sheet_row = root.find(f"m:sheetData/m:row[@r='{row_index + 2}']", NS)
        if sheet_row is None:
            continue
        _set_row_value(sheet_row, expected_index, updates[metric])
        if formula_index is not None:
            _set_row_value(sheet_row, formula_index, updates[metric])
    editor.set_sheet_root("Validation", root)


def _timeline_record_from_draft(draft: ServiceEventDraft, base: pd.Series | dict | None = None) -> dict[str, object]:
    record = dict(base) if base is not None else {}
    record.update({
        "event_number": draft.event_number,
        "event_date": pd.Timestamp(draft.event_date),
        "client": draft.client,
        "city": draft.city,
        "region_code": draft.region_code,
        "state_region": draft.state_region,
        "status": draft.status,
        "notes": draft.notes,
    })
    return record


def _finalize_completed_timeline_update(
    editor: WorkbookXmlEditor,
    raw_timeline: pd.DataFrame,
    raw_clients: pd.DataFrame,
    raw_scorecard: pd.DataFrame,
    raw_validation: pd.DataFrame,
    data: WorkbookData,
    completed_timeline: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    completed_after = _renumber_completed_timeline(completed_timeline)
    _replace_timeline_completed(editor, raw_timeline, completed_after)
    clients_after = _replace_client_list_from_timeline(editor, raw_clients, data, completed_after)
    updates = _scorecard_updates(completed_after, clients_after)
    _update_scorecard(editor, raw_scorecard, updates)
    _replace_repeat_clients(editor, completed_after)
    _replace_state_coverage(editor, completed_after)
    _update_validation(editor, raw_validation, updates)
    return completed_after, clients_after


def _completed_timeline_without_event(data: WorkbookData, event_number: int) -> tuple[pd.DataFrame, pd.Series]:
    completed = data.timeline[data.timeline["status"].eq("Completed")].copy()
    numbers = pd.to_numeric(completed.get("event_number", pd.Series(dtype=float)), errors="coerce")
    matches = completed.index[numbers.eq(float(event_number))].tolist()
    if not matches:
        raise ValueError("Completed event could not be found.")
    match_index = matches[0]
    selected = completed.loc[match_index].copy()
    return completed.drop(index=match_index).reset_index(drop=True), selected


def update_existing_event(
    workbook_path: Path,
    event_ref: str,
    client: str,
    location: str,
    event_date: date,
    status: str,
    notes: str,
) -> SavedServiceEvent:
    data = load_workbook(workbook_path)
    normalized_status = str(status or "Completed").strip().title()
    if normalized_status not in {"Completed", "Scheduled"}:
        raise ValueError("Status must be Completed or Scheduled.")
    draft = build_service_event_draft(data, client, location, event_date, notes, normalized_status)

    raw_sheets = read_xlsx(workbook_path)
    raw_timeline = raw_sheets.get("Timeline", pd.DataFrame())
    raw_clients = raw_sheets.get("Client List", pd.DataFrame())
    raw_scorecard = raw_sheets.get("Scorecard", pd.DataFrame())
    raw_validation = raw_sheets.get("Validation", pd.DataFrame())
    raw_pipeline = raw_sheets.get("Pipeline", pd.DataFrame())

    editor = WorkbookXmlEditor(workbook_path)
    try:
        kind, identifier = str(event_ref).split(":", 1)
    except ValueError as error:
        raise ValueError("Select a valid existing event.") from error

    completed_visits: int | None = None
    if kind == "timeline":
        event_number = int(float(identifier))
        completed_after, selected = _completed_timeline_without_event(data, event_number)
        if normalized_status == "Completed":
            draft.event_number = event_number
            completed_after = pd.concat(
                [completed_after, pd.DataFrame([_timeline_record_from_draft(draft, selected)])],
                ignore_index=True,
            )
        else:
            draft.event_number = None
            _replace_pipeline_rows(editor, raw_pipeline, append_draft=draft)
        completed_after, clients_after = _finalize_completed_timeline_update(
            editor,
            raw_timeline,
            raw_clients,
            raw_scorecard,
            raw_validation,
            data,
            completed_after,
        )
        match = clients_after.index[clients_after["client"].astype(str).str.casefold().eq(draft.client.casefold())].tolist()
        if match:
            completed_visits = int(clients_after.loc[match[0], "completed_visits"])
        editor.save()
        return SavedServiceEvent(
            event_number=event_number if normalized_status == "Completed" else None,
            client=draft.client,
            city=draft.city,
            region_code=draft.region_code,
            state_region=draft.state_region,
            event_date=draft.event_date,
            status=draft.status,
            notes=draft.notes,
            existing_client=draft.existing_client,
            completed_visits=completed_visits,
        )

    if kind == "pipeline":
        pipeline_index = int(float(identifier))
        pipeline = data.pipeline.copy()
        if pipeline.empty or pipeline_index < 0 or pipeline_index >= len(pipeline):
            raise ValueError("Scheduled assignment could not be found.")
        if normalized_status == "Scheduled":
            draft.event_number = None
            _replace_pipeline_rows(editor, raw_pipeline, remove_index=pipeline_index, append_draft=draft)
            editor.save()
            return SavedServiceEvent(
                event_number=None,
                client=draft.client,
                city=draft.city,
                region_code=draft.region_code,
                state_region=draft.state_region,
                event_date=draft.event_date,
                status=draft.status,
                notes=draft.notes,
                existing_client=draft.existing_client,
                completed_visits=None,
            )

        _replace_pipeline_rows(editor, raw_pipeline, remove_index=pipeline_index)
        draft.event_number = next_visit_number(data)
        completed_after = pd.concat(
            [
                data.timeline[data.timeline["status"].eq("Completed")].copy(),
                pd.DataFrame([_timeline_record_from_draft(draft)]),
            ],
            ignore_index=True,
        )
        completed_after, clients_after = _finalize_completed_timeline_update(
            editor,
            raw_timeline,
            raw_clients,
            raw_scorecard,
            raw_validation,
            data,
            completed_after,
        )
        match = clients_after.index[clients_after["client"].astype(str).str.casefold().eq(draft.client.casefold())].tolist()
        if match:
            completed_visits = int(clients_after.loc[match[0], "completed_visits"])
        editor.save()
        return SavedServiceEvent(
            event_number=int(draft.event_number) if draft.event_number is not None else None,
            client=draft.client,
            city=draft.city,
            region_code=draft.region_code,
            state_region=draft.state_region,
            event_date=draft.event_date,
            status=draft.status,
            notes=draft.notes,
            existing_client=draft.existing_client,
            completed_visits=completed_visits,
        )

    raise ValueError("Select a valid existing event.")


def delete_existing_event(workbook_path: Path, event_ref: str) -> None:
    data = load_workbook(workbook_path)
    raw_sheets = read_xlsx(workbook_path)
    raw_timeline = raw_sheets.get("Timeline", pd.DataFrame())
    raw_clients = raw_sheets.get("Client List", pd.DataFrame())
    raw_scorecard = raw_sheets.get("Scorecard", pd.DataFrame())
    raw_validation = raw_sheets.get("Validation", pd.DataFrame())
    raw_pipeline = raw_sheets.get("Pipeline", pd.DataFrame())

    editor = WorkbookXmlEditor(workbook_path)
    try:
        kind, identifier = str(event_ref).split(":", 1)
    except ValueError as error:
        raise ValueError("Select a valid existing event.") from error

    if kind == "timeline":
        event_number = int(float(identifier))
        completed_after, _ = _completed_timeline_without_event(data, event_number)
        _finalize_completed_timeline_update(
            editor,
            raw_timeline,
            raw_clients,
            raw_scorecard,
            raw_validation,
            data,
            completed_after,
        )
        editor.save()
        return

    if kind == "pipeline":
        pipeline_index = int(float(identifier))
        _replace_pipeline_rows(editor, raw_pipeline, remove_index=pipeline_index)
        editor.save()
        return

    raise ValueError("Select a valid existing event.")


def append_service_event(workbook_path: Path, draft: ServiceEventDraft) -> SavedServiceEvent:
    data = load_workbook(workbook_path)
    draft.status = str(draft.status or "Completed").strip().title()
    draft.event_number = next_visit_number(data) if draft.status == "Completed" else None

    raw_sheets = read_xlsx(workbook_path)
    raw_timeline = raw_sheets.get("Timeline", pd.DataFrame())
    raw_clients = raw_sheets.get("Client List", pd.DataFrame())
    raw_scorecard = raw_sheets.get("Scorecard", pd.DataFrame())
    raw_validation = raw_sheets.get("Validation", pd.DataFrame())
    raw_pipeline = raw_sheets.get("Pipeline", pd.DataFrame())

    editor = WorkbookXmlEditor(workbook_path)
    if draft.status == "Scheduled":
        _append_pipeline(editor, draft, raw_pipeline)
        editor.save()
        return SavedServiceEvent(
            event_number=None,
            client=draft.client,
            city=draft.city,
            region_code=draft.region_code,
            state_region=draft.state_region,
            event_date=draft.event_date,
            status=draft.status,
            notes=draft.notes,
            existing_client=draft.existing_client,
            completed_visits=None,
        )

    existing_completed = data.timeline[data.timeline["status"].eq("Completed")].copy()
    timeline_after = pd.concat(
        [
            existing_completed,
            pd.DataFrame(
                [
                    {
                        "event_number": draft.event_number,
                        "event_date": pd.Timestamp(draft.event_date),
                        "client": draft.client,
                        "city": draft.city,
                        "region_code": draft.region_code,
                        "state_region": draft.state_region,
                        "status": draft.status,
                        "notes": draft.notes,
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    _, clients_after = _finalize_completed_timeline_update(
        editor,
        raw_timeline,
        raw_clients,
        raw_scorecard,
        raw_validation,
        data,
        timeline_after,
    )
    match = clients_after.index[clients_after["client"].astype(str).str.casefold().eq(draft.client.casefold())].tolist()
    completed_visits = int(clients_after.loc[match[0], "completed_visits"]) if match else None
    editor.save()

    return SavedServiceEvent(
        event_number=int(draft.event_number) if draft.event_number is not None else None,
        client=draft.client,
        city=draft.city,
        region_code=draft.region_code,
        state_region=draft.state_region,
        event_date=draft.event_date,
        status=draft.status,
        notes=draft.notes,
        existing_client=draft.existing_client,
        completed_visits=completed_visits,
    )


def complete_scheduled_assignment(workbook_path: Path, pipeline_index: int, completion_date: date | None = None) -> SavedServiceEvent:
    data = load_workbook(workbook_path)
    pipeline = data.pipeline.copy()
    if pipeline.empty or pipeline_index < 0 or pipeline_index >= len(pipeline):
        raise ValueError("Scheduled assignment could not be found.")

    row = pipeline.iloc[pipeline_index]
    status = str(row.get("status", "") or "").strip().title()
    if status != "Scheduled":
        raise ValueError("Only scheduled assignments can be marked completed.")

    client = str(row.get("client", "") or "").strip()
    location = str(row.get("location", "") or "").strip()
    notes = str(row.get("notes", "") or "").strip()
    if not client:
        raise ValueError("Scheduled assignment is missing a client.")
    if not location:
        raise ValueError("Scheduled assignment is missing a location.")

    draft = build_service_event_draft(
        data,
        client,
        location,
        completion_date or date.today(),
        notes,
        "Completed",
    )

    raw_sheets = read_xlsx(workbook_path)
    raw_timeline = raw_sheets.get("Timeline", pd.DataFrame())
    raw_clients = raw_sheets.get("Client List", pd.DataFrame())
    raw_scorecard = raw_sheets.get("Scorecard", pd.DataFrame())
    raw_validation = raw_sheets.get("Validation", pd.DataFrame())
    raw_pipeline = raw_sheets.get("Pipeline", pd.DataFrame())

    editor = WorkbookXmlEditor(workbook_path)
    _remove_pipeline_row(editor, raw_pipeline, pipeline_index)

    existing_completed = data.timeline[data.timeline["status"].eq("Completed")].copy()
    timeline_after = pd.concat(
        [
            existing_completed,
            pd.DataFrame(
                [
                    {
                        "event_number": draft.event_number,
                        "event_date": pd.Timestamp(draft.event_date),
                        "client": draft.client,
                        "city": draft.city,
                        "region_code": draft.region_code,
                        "state_region": draft.state_region,
                        "status": draft.status,
                        "notes": draft.notes,
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    _, clients_after = _finalize_completed_timeline_update(
        editor,
        raw_timeline,
        raw_clients,
        raw_scorecard,
        raw_validation,
        data,
        timeline_after,
    )
    match = clients_after.index[clients_after["client"].astype(str).str.casefold().eq(draft.client.casefold())].tolist()
    completed_visits = int(clients_after.loc[match[0], "completed_visits"]) if match else None
    editor.save()

    return SavedServiceEvent(
        event_number=int(draft.event_number) if draft.event_number is not None else None,
        client=draft.client,
        city=draft.city,
        region_code=draft.region_code,
        state_region=draft.state_region,
        event_date=draft.event_date,
        status=draft.status,
        notes=draft.notes,
        existing_client=draft.existing_client,
        completed_visits=completed_visits,
    )
