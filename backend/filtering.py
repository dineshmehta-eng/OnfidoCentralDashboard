from datetime import date, datetime
from functools import lru_cache
from typing import Any, Dict, Iterable, List


FILTER_KEYS = {
    "analyst": ["analyst", "AnalystEmail", "analyst_email"],
    "tl": ["tl", "TLName", "tl_name", "TL_Name"],
    "am": ["am", "AM"],
    "qa": ["qa", "QAName", "qa_name", "QA_Name"],
    "category": ["category", "Category", "cat"],
    "location": ["location", "Location"],
    "aon_wise": ["aon_wise", "AONWise", "AON_Wise", "aon"],
}

ROW_KEYS = {
    "analyst": [
        "Analyst_Email", "analyst_email", "task_information_analyst_email",
        "manual_tasks_events_event_data_unassigned_from_email",
        "proof_of_address_task_analyst_email", "analyst_name",
    ],
    "tl": ["TL_Name", "tl_name", "tl_s_name", "TLName"],
    "am": ["AM", "am", "am_name", "am_s_name"],
    "qa": ["QA_Name", "qa_name", "qa_s_name", "QAName"],
    "category": ["Category", "category", "Legecy_queue", "legecy_queue", "Legacy_queue", "legacy_queue"],
    "location": ["Location", "location"],
    "aon_wise": ["AON_Wise", "aon_wise", "AONWise", "aon", "aon_wise_2"],
}

DATE_KEYS = [
    "Date", "date", "dt", "manual_tasks_events_timestamp_time",
    "task_information_task_completed_time", "synced_at",
]


def filter_value(filters: Dict[str, Any] | None, *keys: str) -> str:
    filters = filters or {}
    for key in keys:
        value = filters.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _row_value(row: Dict[str, Any], aliases: Iterable[str]):
    if not isinstance(row, dict):
        return None
    for key in aliases:
        if key in row and row.get(key) not in (None, ""):
            return row.get(key)
    lower = {str(k).lower(): k for k in row.keys()}
    for key in aliases:
        actual = lower.get(str(key).lower())
        if actual is not None and row.get(actual) not in (None, ""):
            return row.get(actual)
    return None


def _norm(value: Any) -> str:
    text = " ".join(str(value or "").strip().lower().split())
    return text.replace("above then 90", "above than 90")


def _name_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    if "@" in text:
        text = text.split("@", 1)[0]
        text = text.replace(".", " ").replace("_", " ")
        text = "".join(ch for ch in text if not ch.isdigit())
    return " ".join(text.split())


def has_dimension_filters(filters: Dict[str, Any] | None) -> bool:
    filters = filters or {}
    return any(filter_value(filters, *aliases) for aliases in FILTER_KEYS.values())


@lru_cache(maxsize=1)
def _filter_metadata():
    try:
        from db import fetch_all

        rows = fetch_all("""
            WITH ranked AS (
                SELECT
                    analyst_email,
                    tl_name,
                    am,
                    qa_name,
                    aon_wise,
                    COALESCE(NULLIF(category, ''), NULLIF(legecy_queue, '')) AS category,
                    ROW_NUMBER() OVER (
                        PARTITION BY LOWER(LTRIM(RTRIM(analyst_email)))
                        ORDER BY
                            COALESCE(
                                TRY_CONVERT(date, [date], 23),
                                TRY_CONVERT(date, [date], 106),
                                TRY_CONVERT(date, [date])
                            ) DESC,
                            month_idx DESC
                    ) AS rn
                FROM stg_consolidated
                WHERE analyst_email IS NOT NULL AND LTRIM(RTRIM(analyst_email)) <> ''
            )
            SELECT analyst_email, tl_name, am, qa_name, aon_wise, category
            FROM ranked
            WHERE rn = 1
        """)
    except Exception:
        rows = []

    by_email: Dict[str, Dict[str, Any]] = {}
    by_name: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        email = _norm(row.get("analyst_email"))
        if not email:
            continue
        meta = {
            "TL_Name": row.get("tl_name"),
            "AM": row.get("am"),
            "QA_Name": row.get("qa_name"),
            "AON_Wise": row.get("aon_wise"),
            "Category": row.get("category"),
        }
        by_email[email] = meta
        name = _name_key(row.get("analyst_email"))
        if name and name not in by_name:
            by_name[name] = meta
    return by_email, by_name


def enrich_rows_with_filter_metadata(rows: List[Dict[str, Any]] | None) -> List[Dict[str, Any]]:
    if not rows:
        return []
    by_email, by_name = _filter_metadata()
    if not by_email and not by_name:
        return rows

    enriched = []
    for row in rows:
        if not isinstance(row, dict):
            enriched.append(row)
            continue
        meta = None
        email = _row_value(row, ROW_KEYS["analyst"])
        if email:
            meta = by_email.get(_norm(email))
        if not meta:
            name = _row_value(row, ["emp_name", "analyst_name"])
            if name:
                meta = by_name.get(_name_key(name))
        if not meta:
            enriched.append(row)
            continue
        new_row = dict(row)
        for key, value in meta.items():
            if value not in (None, "") and _row_value(new_row, [key]) in (None, ""):
                new_row[key] = value
        enriched.append(new_row)
    return enriched


def _parse_date(value: Any):
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    if len(text) >= 10 and text[4:5] == "-" and text[7:8] == "-":
        text = text[:10]
    for fmt in (
        "%Y-%m-%d",
        "%d-%b-%y",
        "%d-%b-%Y",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def row_matches_filters(row: Dict[str, Any], filters: Dict[str, Any] | None) -> bool:
    filters = filters or {}
    for filter_key, filter_aliases in FILTER_KEYS.items():
        wanted = filter_value(filters, *filter_aliases)
        if not wanted:
            continue
        actual = _row_value(row, ROW_KEYS[filter_key])
        if actual is None:
            return False
        if _norm(actual) != _norm(wanted):
            return False

    date_from = filter_value(filters, "from", "date_from")
    date_to = filter_value(filters, "to", "date_to")
    if date_from or date_to:
        row_date = _parse_date(_row_value(row, DATE_KEYS))
        if row_date is None:
            return True
        start = _parse_date(date_from)
        end = _parse_date(date_to)
        if start and row_date < start:
            return False
        if end and row_date > end:
            return False

    return True


def apply_filters(rows: List[Dict[str, Any]] | None, filters: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    if not rows:
        return []
    return [row for row in rows if row_matches_filters(row, filters)]
