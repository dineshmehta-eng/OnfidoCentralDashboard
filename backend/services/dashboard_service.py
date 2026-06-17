from db import engine
from sqlalchemy import text
from utils.dates import get_current_month_str
from utils import metrics
from config import settings
from typing import Dict, Any, List
import pandas as pd
import calendar
import threading
import time
from functools import lru_cache

# Column mapping helpers to normalize possible naming variations in views
POSSIBLE_COLS = {
    "total_task": ["Total_Task", "TotalTask", "total_task", "Tasks"],
    "total_aht": ["Total_AHT", "TotalAHT", "total_aht", "AHT"],
    "poa_task": ["POA_Task", "POATask", "poa_task"],
    "poa_aht": ["POA_AHT", "POAAHT", "poa_aht"],
    "poa_audits": ["POA_Audits", "POAAudits", "poa_audits"],
    "poa_error": ["POA_Error", "POAError", "poa_error"],
    "cre": ["CRE", "cre"],
    "crq": ["CRQ", "crq"],
    "mis_fraud": ["Mis_Fraud", "MisFraud", "mis_fraud"],
    "total_fraud": ["Total_Fraud", "TotalFraud", "total_fraud"],
    "wrn_fraud": ["WRN_Fraud", "WRNFraud", "wrn_fraud"],
    "total_clear": ["Total_Clear", "TotalClear", "total_clear"],
    "ext_extraction": ["Ext_Extraction", "ExtExtraction", "ext_extraction"],
    "ext_ext_error": ["Ext_Ext_Error", "ExtExtError", "ext_ext_error"],
    "ext_raw_extraction": ["Ext_Raw_Extraction", "ExtRawExtraction", "ext_raw_extraction"],
    "ext_raw_error": ["Ext_RawError", "ExtRawError", "ext_rawerror", "ext_raw_error"],
    "ext_mis_fraud": ["Ext_Mis_Fraud", "ExtMisFraud", "ext_mis_fraud"],
    "ext_total_fraud": ["Ext_Total_Fraud", "ExtTotalFraud", "ext_total_fraud"],
    "ext_wrn_fraud": ["Ext_WRN_Fraud", "ExtWRNFraud", "ext_wrn_fraud"],
    "ext_total_clear": ["Ext_Total_Clear", "ExtTotalClear", "ext_total_clear"],
    "ext_poa_audits": ["Ext_POA_Audits", "ExtPOAAudits", "ext_poa_audits"],
    "ext_poa_error": ["Ext_POA_Error", "ExtPOAError", "ext_poa_error"],
    "ext_manual_far_error": ["ext_manual_farerror", "Ext_Manual_FARError", "ExtManualFARError", "ext_manual_far_error"],
    "ext_manual_far": ["ext_manual_far", "Ext_Manual_FAR", "ExtManualFAR", "ext_manual_far"],
    "ext_manual_frr_error": ["ext_manual_frrerror", "Ext_Manual_FRRError", "ExtManualFRRError", "ext_manual_frr_error"],
    "ext_manual_frr": ["ext_manual_frr", "Ext_Manual_FRR", "ExtManualFRR", "ext_manual_frr"],
    "int_ext_error": ["int_ext_error", "Int_Ext_Error", "IntExtError", "int_ext_error"],
    "int_ext_audits": ["int_ext_audits", "Int_Ext_Audits", "IntExtAudits", "int_ext_audits"],
    "int_raw_ext_error": ["int_raw_exterror", "Int_Raw_ExtError", "IntRawExtError", "int_raw_ext_error"],
    "int_raw_ext_audits": ["int_raw_ext_audits", "Int_Raw_Ext_Audits", "IntRawExtAudits", "int_raw_ext_audits"],
    "analyst_email": ["Analyst_Email", "AnalystEmail", "analyst_email", "Email"],
    "tl_name": ["TL_Name", "TL Name", "TLName", "tl_name"],
    "am": ["AM", "am"],
    "qa_name": ["QA_Name", "QA Name", "QAName", "qa_name"],
    "category": ["Legecy_queue", "Legecy queue", "Legacy_queue", "Legacy queue", "Category", "category"],
    "location": ["Location", "location"],
    "aon_wise": ["AON_Wise", "AON Wise", "AONWise", "aon_wise"],
    "date": ["Date", "date", "dt"],
    "month": ["month_idx", "Month", "month"],
}

CONSOLIDATED_TABLE = "stg_consolidated"
CONSOLIDATED_SELECT_COLS = [
    ("analyst_email", "analyst_email"),
    ("tl_name", "tl_name"),
    ("am", "am"),
    ("qa_name", "qa_name"),
    ("category", "category"),
    ("location", "location"),
    ("aon_wise", "aon_wise"),
    ("month", "month"),
    ("date", "date"),
    ("total_task", "total_task"),
    ("total_aht", "total_aht"),
    ("poa_task", "poa_task"),
    ("poa_aht", "poa_aht"),
    ("poa_audits", "poa_audits"),
    ("poa_error", "poa_error"),
    ("ext_poa_audits", "ext_poa_audits"),
    ("ext_poa_error", "ext_poa_error"),
    ("cre", "cre"),
    ("crq", "crq"),
    ("mis_fraud", "mis_fraud"),
    ("total_fraud", "total_fraud"),
    ("wrn_fraud", "wrn_fraud"),
    ("total_clear", "total_clear"),
    ("ext_extraction", "ext_extraction"),
    ("ext_ext_error", "ext_ext_error"),
    ("ext_raw_extraction", "ext_raw_extraction"),
    ("ext_raw_error", "ext_rawerror"),
    ("ext_mis_fraud", "ext_mis_fraud"),
    ("ext_total_fraud", "ext_total_fraud"),
    ("ext_wrn_fraud", "ext_wrn_fraud"),
    ("ext_total_clear", "ext_total_clear"),
    ("ext_manual_far_error", "ext_manual_farerror"),
    ("ext_manual_far", "ext_manual_far"),
    ("ext_manual_frr_error", "ext_manual_frrerror"),
    ("ext_manual_frr", "ext_manual_frr"),
    ("int_ext_error", "int_ext_error"),
    ("int_ext_audits", "int_ext_audits"),
    ("int_raw_ext_error", "int_raw_exterror"),
    ("int_raw_ext_audits", "int_raw_ext_audits"),
]
NUMERIC_KEYS = [
    "total_task", "total_aht", "poa_task", "poa_aht", "poa_audits", "poa_error",
    "ext_poa_audits", "ext_poa_error", "cre", "crq", "mis_fraud", "total_fraud",
    "wrn_fraud", "total_clear", "ext_extraction", "ext_ext_error",
    "ext_raw_extraction", "ext_raw_error", "ext_mis_fraud", "ext_total_fraud",
    "ext_wrn_fraud", "ext_total_clear", "ext_manual_far_error", "ext_manual_far",
    "ext_manual_frr_error", "ext_manual_frr", "int_ext_error", "int_ext_audits",
    "int_raw_ext_error", "int_raw_ext_audits",
]
_SNAPSHOT_LOCK = threading.RLock()
_CONSOLIDATED_SNAPSHOT: Dict[str, Any] = {"loaded_at": 0.0, "df": None}


def resolve_col(df: pd.DataFrame, key: str):
    candidates = POSSIBLE_COLS.get(key, [key])
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _qident(name: str) -> str:
    return "[" + str(name).replace("]", "]]") + "]"


@lru_cache(maxsize=8)
def _table_columns(table: str) -> List[str]:
    try:
        rows = pd.read_sql(
            text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = :table"),
            engine,
            params={"table": table},
        )
        return [str(v) for v in rows["COLUMN_NAME"].tolist()]
    except Exception:
        return []


def resolve_table_col(table: str, key: str) -> str:
    columns = _table_columns(table)
    if not columns:
        return POSSIBLE_COLS.get(key, [key])[0]
    by_lower = {c.lower(): c for c in columns}
    for candidate in POSSIBLE_COLS.get(key, [key]):
        found = by_lower.get(str(candidate).lower())
        if found:
            return found
    return POSSIBLE_COLS.get(key, [key])[0]


def _select_expr(table: str, key: str, alias: str | None = None) -> str:
    return f"{_qident(resolve_table_col(table, key))} AS {_qident(alias or key)}"


def _consolidated_select_sql() -> str:
    return "SELECT " + ", ".join(
        _select_expr(CONSOLIDATED_TABLE, logical, alias)
        for logical, alias in CONSOLIDATED_SELECT_COLS
    ) + f" FROM {CONSOLIDATED_TABLE}"


def _normalize_match(value: Any) -> str:
    text_value = " ".join(str(value or "").strip().lower().split())
    return text_value.replace("above then 90", "above than 90")


def _load_consolidated_df() -> pd.DataFrame:
    df = pd.read_sql(text(_consolidated_select_sql()), engine)
    for key in NUMERIC_KEYS:
        col = resolve_col(df, key)
        if col:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    date_col = resolve_col(df, "date")
    if date_col:
        values = df[date_col].astype(str).str.strip()
        parsed = pd.to_datetime(values, format="%d-%b-%y", errors="coerce")
        missing = parsed.isna()
        if missing.any():
            parsed.loc[missing] = pd.to_datetime(values.loc[missing], format="%Y-%m-%d", errors="coerce")
        missing = parsed.isna()
        if missing.any():
            parsed.loc[missing] = pd.to_datetime(values.loc[missing], format="%d/%m/%Y", errors="coerce")
        df["__date_parsed"] = parsed
    return df


def get_consolidated_snapshot(force_refresh: bool = False) -> pd.DataFrame:
    ttl = max(1, int(getattr(settings, "CACHE_TTL_SECONDS", 300) or 300))
    now = time.time()
    with _SNAPSHOT_LOCK:
        df = _CONSOLIDATED_SNAPSHOT.get("df")
        loaded_at = float(_CONSOLIDATED_SNAPSHOT.get("loaded_at") or 0)
        if force_refresh or df is None or (now - loaded_at) > ttl:
            df = _load_consolidated_df()
            _CONSOLIDATED_SNAPSHOT["df"] = df
            _CONSOLIDATED_SNAPSHOT["loaded_at"] = now
        return df


def refresh_consolidated_snapshot() -> pd.DataFrame:
    return get_consolidated_snapshot(force_refresh=True)


def _latest_month(df: pd.DataFrame) -> str:
    month_col = resolve_col(df, "month")
    if not month_col or df.empty:
        return get_current_month_str()
    months = [m for m in df[month_col].dropna().astype(str).str.strip().unique().tolist() if m]
    if not months:
        return get_current_month_str()
    return sorted(months, key=_month_sort_key)[-1]


def _filter_df(df: pd.DataFrame, filters: Dict[str, Any], include_month: bool) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    mask = pd.Series(True, index=df.index)

    date_from = (filters.get("from") or filters.get("date_from") or "").strip()
    date_to = (filters.get("to") or filters.get("date_to") or "").strip()
    if "__date_parsed" in df.columns and (date_from or date_to):
        if date_from:
            start = pd.to_datetime(date_from, errors="coerce")
            if pd.notna(start):
                mask &= df["__date_parsed"] >= start
        if date_to:
            end = pd.to_datetime(date_to, errors="coerce")
            if pd.notna(end):
                mask &= df["__date_parsed"] <= end

    if include_month:
        month = filters.get("month") or ""
        month_col = resolve_col(df, "month")
        if month and month_col:
            mask &= df[month_col].astype(str).str.strip() == str(month).strip()

    for logical_col, aliases in [
        ("analyst_email", ["analyst", "AnalystEmail", "analyst_email"]),
        ("tl_name", ["tl", "TLName", "tl_name"]),
        ("am", ["am", "AM"]),
        ("qa_name", ["qa", "QAName", "qa_name"]),
        ("category", ["category", "Category"]),
        ("location", ["location", "Location"]),
        ("aon_wise", ["aon_wise", "AONWise", "aon"]),
    ]:
        value = ""
        for alias in aliases:
            candidate = filters.get(alias)
            if candidate is not None and str(candidate).strip():
                value = str(candidate).strip()
                break
        if not value:
            continue
        col = resolve_col(df, logical_col)
        if col:
            mask &= df[col].map(_normalize_match) == _normalize_match(value)

    return df.loc[mask].copy()


def get_init_data(force_refresh: bool = False) -> Dict[str, Any]:
    df = get_consolidated_snapshot(force_refresh=force_refresh)
    filters: Dict[str, Any] = {}
    for logical_col, key in [
        ("analyst_email", "analysts"),
        ("tl_name", "tls"),
        ("am", "ams"),
        ("qa_name", "qas"),
        ("category", "categories"),
        ("aon_wise", "aons"),
        ("location", "locations"),
        ("month", "months"),
    ]:
        col = resolve_col(df, logical_col)
        if not col:
            filters[key] = []
            continue
        values = df[col].dropna().astype(str).str.strip()
        filters[key] = sorted([v for v in values.unique().tolist() if v], key=lambda v: _month_sort_key(v) if key == "months" else str(v).lower())

    date_col = resolve_col(df, "date")
    parsed = df["__date_parsed"].dropna() if "__date_parsed" in df.columns else pd.Series([], dtype="datetime64[ns]")
    min_date = parsed.min().strftime("%Y-%m-%d") if not parsed.empty else (str(df[date_col].min()) if date_col else "")
    max_date = parsed.max().strftime("%Y-%m-%d") if not parsed.empty else (str(df[date_col].max()) if date_col else "")
    return {
        "success": True,
        "filters": filters,
        "totalRows": int(len(df)),
        "minDate": min_date,
        "maxDate": max_date,
        "currentMonth": _latest_month(df),
        "source": "SQL Server",
        "snapshotLoadedAt": _CONSOLIDATED_SNAPSHOT.get("loaded_at"),
    }


def _sum(df: pd.DataFrame, key: str):
    col = resolve_col(df, key)
    if col and not df.empty:
        return float(pd.to_numeric(df[col], errors='coerce').sum())
    return 0.0


def _group_agg(df: pd.DataFrame, group_key: str, sum_keys: List[str]) -> List[Dict[str, Any]]:
    grp_col = resolve_col(df, group_key)
    if not grp_col or df.empty:
        return []
    for sk in sum_keys:
        c = resolve_col(df, sk)
        if c and c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    agg_dict = {}
    for sk in sum_keys:
        c = resolve_col(df, sk)
        if c:
            agg_dict[c] = "sum"
    if not agg_dict:
        return []
    grp = df.groupby(grp_col).agg(agg_dict).reset_index()
    records = []
    for _, row in grp.iterrows():
        label = metrics.to_native(row[grp_col])
        rec = {grp_col: label, "key": label, "name": label}
        for sk in sum_keys:
            c = resolve_col(df, sk)
            if c and c in row:
                val = row[c]
                rec[sk] = metrics.to_native(val) if pd.notna(val) else 0
        records.append(rec)
    return records


def get_dashboard_data(filters: Dict[str, Any]) -> Dict[str, Any]:
    filters = dict(filters or {})
    date_from = (filters.get("from") or filters.get("date_from") or "").strip()
    date_to = (filters.get("to") or filters.get("date_to") or "").strip()
    has_date_range = bool(date_from or date_to)
    month = filters.get("month") or ""
    view_mode = filters.get("viewMode", "daily")
    force_refresh = str(filters.get("forceRefresh") or "").lower() in ("1", "true", "yes")
    source_df = get_consolidated_snapshot(force_refresh=force_refresh)

    if not month and not has_date_range:
        month = _latest_month(source_df)

    if month:
        filters["month"] = month

    all_df = _filter_df(source_df, filters, include_month=False)
    df = _filter_df(source_df, filters, include_month=True)

    return metrics.sanitize_dict({
        "success": True,
        "currentMonth": month,
        "overview": _build_overview(df, month, all_df),
        "productivity": _build_productivity(df),
        "quality": _build_quality(df),
        "poa": _build_poa(df, all_df),
        "trends": _build_trends(all_df if view_mode != "daily" else df, view_mode),
        "alerts": {"alerts": _build_alerts(df)}
    })


def _month_sort_key(label: Any) -> int:
    text_label = str(label or "").strip()
    mon = text_label[:3].title()
    try:
        m = list(calendar.month_abbr).index(mon)
    except ValueError:
        m = 0
    try:
        y = int(text_label[-2:])
    except ValueError:
        y = 0
    return y * 100 + m


def _summary_from_df(df: pd.DataFrame, label: str, label_key: str) -> Dict[str, Any]:
    total_task = _sum(df, "total_task")
    total_aht = _sum(df, "total_aht")
    poa_task = _sum(df, "poa_task")
    poa_aht = _sum(df, "poa_aht")
    poa_audits = _sum(df, "poa_audits")
    poa_error = _sum(df, "poa_error")
    ext_poa_audits = _sum(df, "ext_poa_audits")
    ext_poa_error = _sum(df, "ext_poa_error")

    mis = _sum(df, "mis_fraud")
    tfraud = _sum(df, "total_fraud")
    wrn = _sum(df, "wrn_fraud")
    tclear = _sum(df, "total_clear")
    ext_ext_aud = _sum(df, "ext_extraction")
    ext_ext_err = _sum(df, "ext_ext_error")
    ext_raw_aud = _sum(df, "ext_raw_extraction")
    ext_raw_err = _sum(df, "ext_raw_error")
    ext_mis = _sum(df, "ext_mis_fraud")
    ext_tfraud = _sum(df, "ext_total_fraud")
    ext_wrn = _sum(df, "ext_wrn_fraud")
    ext_tclear = _sum(df, "ext_total_clear")
    em_far_err = _sum(df, "ext_manual_far_error")
    em_far = _sum(df, "ext_manual_far")
    em_frr_err = _sum(df, "ext_manual_frr_error")
    em_frr = _sum(df, "ext_manual_frr")
    ie_err = _sum(df, "int_ext_error")
    ie_aud = _sum(df, "int_ext_audits")
    ir_err = _sum(df, "int_raw_ext_error")
    ir_aud = _sum(df, "int_raw_ext_audits")

    avg_aht = round(metrics.calc_avg_aht(total_aht, total_task), 2)
    poa_avg_aht = round(metrics.calc_poa_avg_aht(poa_aht, poa_task), 2)
    row = {
        label_key: label,
        "key": label,
        "name": label,
        "Task": int(total_task),
        "AHT": avg_aht,
        "Total_AHT": total_aht,
        "Total_Task": int(total_task),
        "Total_Tasks": int(total_task),
        "Avg_AHT": avg_aht,
        "Avg_AHT_S": avg_aht,
        "POA_Task": int(poa_task),
        "POA_AHT": poa_avg_aht,
        "POA_Avg_AHT": poa_avg_aht,
        "POA_Avg_AHT_S": poa_avg_aht,
        "POA_Audits_Raw": int(poa_audits),
        "POA_Error_Raw": int(poa_error),
        "Ext_POA_Audits_Raw": int(ext_poa_audits),
        "Ext_POA_Error_Raw": int(ext_poa_error),
        "POA_Err_r": metrics.safe_div(poa_error, poa_audits),
        "Ext_POA_r": metrics.safe_div(ext_poa_error, ext_poa_audits),
        "CRE": int(_sum(df, "cre")),
        "CRQ": int(_sum(df, "crq")),
        "Int_Ext_r": metrics.calc_int_ext(ie_err, ie_aud) if ie_aud else 0,
        "Ext_Ext_r": metrics.safe_div(ext_ext_err, ext_ext_aud),
        "Int_Raw_r": metrics.calc_int_raw(ir_err, ir_aud) if ir_aud else 0,
        "Ext_Raw_r": metrics.safe_div(ext_raw_err, ext_raw_aud),
        "Int_FAR_r": metrics.calc_int_far(mis, tfraud),
        "Ext_FAR_r": metrics.calc_ext_far(ext_mis, ext_tfraud) if (ext_tfraud or ext_mis) else 0,
        "Int_FRR_r": metrics.calc_int_frr(wrn, tclear),
        "Ext_FRR_r": metrics.calc_ext_frr(ext_wrn, ext_tclear) if (ext_wrn or ext_tclear) else 0,
        "Ext_Manual_FAR_r": metrics.calc_ext_manual_far(em_far_err, em_far) if em_far else 0,
        "Ext_Manual_FRR_r": metrics.calc_ext_manual_frr(em_frr_err, em_frr) if em_frr else 0,
    }
    row.update({
        "POA_Err": f"{row['POA_Err_r'] * 100:.2f}%",
        "Ext_POA": f"{row['Ext_POA_r'] * 100:.2f}%",
        "Int_Ext": f"{row['Int_Ext_r'] * 100:.2f}%",
        "Ext_Ext": f"{row['Ext_Ext_r'] * 100:.2f}%",
        "Int_Raw": f"{row['Int_Raw_r'] * 100:.2f}%",
        "Ext_Raw": f"{row['Ext_Raw_r'] * 100:.2f}%",
        "Int_FAR": f"{row['Int_FAR_r'] * 100:.2f}%",
        "Ext_FAR": f"{row['Ext_FAR_r'] * 100:.2f}%",
        "Int_FRR": f"{row['Int_FRR_r'] * 100:.2f}%",
        "Ext_FRR": f"{row['Ext_FRR_r'] * 100:.2f}%",
        "Ext_Manual_FAR": f"{row['Ext_Manual_FAR_r'] * 100:.2f}%",
        "Ext_Manual_FRR": f"{row['Ext_Manual_FRR_r'] * 100:.2f}%",
    })
    return row


def _group_quality_rows(df: pd.DataFrame, group_key: str, limit: int | None = None, grand_total: bool = True) -> List[Dict[str, Any]]:
    grp_col = resolve_col(df, group_key)
    if df.empty or not grp_col:
        return []
    rows = []
    for label, grp in df.groupby(grp_col):
        if label is None or str(label).strip() == "":
            continue
        row = _summary_from_df(grp, metrics.to_native(label), "name")
        row["key"] = metrics.to_native(label)
        rows.append(row)
    rows.sort(key=lambda r: (-float(r.get("Task") or 0), str(r.get("name") or "")))
    if limit:
        rows = rows[:limit]
    if grand_total:
        gt = _summary_from_df(df, "Grand Total", "name")
        gt["key"] = "Grand Total"
        gt["isGT"] = True
        rows.append(gt)
    return rows


def _monthly_summary(all_df: pd.DataFrame) -> List[Dict[str, Any]]:
    month_col = resolve_col(all_df, "month")
    if all_df.empty or not month_col:
        return []
    rows = []
    for label, grp in all_df.groupby(month_col):
        rows.append(_summary_from_df(grp, metrics.to_native(label), "Month"))
    return sorted(rows, key=lambda r: _month_sort_key(r.get("Month")))


def _poa_month_label(row: pd.Series, month_col: str | None, date_col: str | None) -> str:
    if month_col and pd.notna(row.get(month_col)):
        return str(row.get(month_col)).strip()
    if date_col and pd.notna(row.get(date_col)):
        parsed = pd.to_datetime(row.get(date_col), errors="coerce")
        if pd.notna(parsed):
            return parsed.strftime("%b-%y")
    return ""


def _poa_month_record(label: Any, sums: pd.Series) -> Dict[str, Any]:
    poa_task = float(sums.get("poa_task", 0) or 0)
    poa_aht = float(sums.get("poa_aht", 0) or 0)
    poa_audits = float(sums.get("poa_audits", 0) or 0)
    poa_error = float(sums.get("poa_error", 0) or 0)
    ext_audits = float(sums.get("ext_poa_audits", 0) or 0)
    ext_error = float(sums.get("ext_poa_error", 0) or 0)
    poa_avg = round(metrics.calc_poa_avg_aht(poa_aht, poa_task), 2) if poa_task else 0
    poa_err = metrics.safe_div(poa_error, poa_audits)
    ext_poa = metrics.safe_div(ext_error, ext_audits)
    return {
        "key": metrics.to_native(label),
        "name": metrics.to_native(label),
        "totalPoaTask": int(poa_task),
        "POA_Task": int(poa_task),
        "POA_AHT": poa_avg,
        "POA_Avg_AHT": poa_avg,
        "POA_Error_Pct": poa_err,
        "POA_Err_r": poa_err,
        "Ext_POA_Error_Pct": ext_poa,
        "Ext_POA_r": ext_poa,
    }


def _build_poa_entity_month_detail(df: pd.DataFrame, group_key: str, limit: int | None = None) -> List[Dict[str, Any]]:
    group_col = resolve_col(df, group_key)
    month_col = resolve_col(df, "month")
    date_col = resolve_col(df, "date")
    if df.empty or not group_col:
        return []

    work = df.copy()
    if month_col:
        month_labels_series = work[month_col].fillna("").astype(str).str.strip()
    else:
        month_labels_series = pd.Series([""] * len(work), index=work.index)
    if date_col:
        missing_month = month_labels_series == ""
        if missing_month.any():
            parsed_dates = pd.to_datetime(work.loc[missing_month, date_col], errors="coerce")
            month_labels_series.loc[missing_month] = parsed_dates.dt.strftime("%b-%y").fillna("")
    work["__poa_month"] = month_labels_series

    month_labels = set(work.loc[work["__poa_month"] != "", "__poa_month"].tolist())
    months = sorted(month_labels, key=_month_sort_key)

    poa_cols = [
        c for c in [
            resolve_col(work, "poa_task"),
            resolve_col(work, "poa_aht"),
            resolve_col(work, "poa_audits"),
            resolve_col(work, "poa_error"),
            resolve_col(work, "ext_poa_audits"),
            resolve_col(work, "ext_poa_error"),
        ] if c
    ]
    for col in poa_cols:
        work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0)

    monthly_lookup: Dict[tuple[Any, str], Dict[str, Any]] = {}
    if months and poa_cols:
        month_work = work[work["__poa_month"] != ""]
        month_sums = month_work.groupby([group_col, "__poa_month"], dropna=True)[poa_cols].sum()
        for (entity, month), sums in month_sums.iterrows():
            monthly_lookup[(entity, month)] = _poa_month_record(month, sums)

    rows: List[Dict[str, Any]] = []
    if not poa_cols:
        return rows
    total_sums = work.groupby(group_col, dropna=True)[poa_cols].sum()
    for label, sums in total_sums.iterrows():
        if label is None or str(label).strip() == "":
            continue
        row = _poa_month_record(label, sums)
        row["months"] = {}
        for month in months:
            q = monthly_lookup.get((label, month), {})
            row["months"][month] = {
                "POA_Task": q.get("POA_Task", 0),
                "POA_AHT": q.get("POA_AHT", 0),
                "POA_Avg_AHT": q.get("POA_Avg_AHT", 0),
                "POA_Err_r": q.get("POA_Err_r", 0),
                "POA_Error_Pct": q.get("POA_Err_r", 0),
                "Ext_POA_r": q.get("Ext_POA_r", 0),
                "Ext_POA_Error_Pct": q.get("Ext_POA_r", 0),
            }
        rows.append(row)

    rows.sort(key=lambda r: (-float(r.get("totalPoaTask") or 0), str(r.get("name") or "")))
    if limit:
        rows = rows[:limit]
    return rows


def _day_trend(df: pd.DataFrame) -> List[Dict[str, Any]]:
    date_col = resolve_col(df, "date")
    if df.empty or not date_col:
        return []
    rows = []
    grouped = df.groupby(date_col)
    for label, grp in grouped:
        row = _summary_from_df(grp, metrics.to_native(label), "date")
        rows.append(row)
    return rows


def _build_overview(df: pd.DataFrame, month: str, all_df: pd.DataFrame | None = None) -> Dict[str, Any]:
    total_task = _sum(df, "total_task")
    total_aht = _sum(df, "total_aht")

    metrics_dict = {
        "totalTasks": int(total_task),
        "avgAht": round(metrics.calc_avg_aht(total_aht, total_task), 2),
    }

    mis = _sum(df, "mis_fraud")
    tfraud = _sum(df, "total_fraud")
    wrn = _sum(df, "wrn_fraud")
    tclear = _sum(df, "total_clear")
    metrics_dict["intFar"] = round(metrics.calc_int_far(mis, tfraud), 4)
    metrics_dict["intFrr"] = round(metrics.calc_int_frr(wrn, tclear), 4)
    metrics_dict["totalFraud"] = int(tfraud)
    metrics_dict["totalClear"] = int(tclear)
    metrics_dict["misFraud"] = int(mis)
    metrics_dict["wrnFraud"] = int(wrn)

    poa_task = _sum(df, "poa_task")
    poa_aht = _sum(df, "poa_aht")
    if poa_task:
        metrics_dict["poaAvgAht"] = round(metrics.calc_poa_avg_aht(poa_aht, poa_task), 2)
        metrics_dict["poaTasks"] = int(poa_task)

    tl_rows = _group_agg(df, "tl_name", ["total_task", "total_aht"])
    am_rows = _group_agg(df, "am", ["total_task"])
    aon_rows = _group_agg(df, "aon_wise", ["total_task"])
    ana_rows = _group_agg(df, "analyst_email", ["total_task", "total_aht"])

    return {
        "metrics": metrics_dict,
        "kpiExtra": {},
        "monthlySummary": _monthly_summary(all_df if all_df is not None else df),
        "dayTrend": _day_trend(df),
        "tlRows": _group_quality_rows(df, "tl_name"),
        "amRows": _group_quality_rows(df, "am"),
        "aonRows": _group_quality_rows(df, "aon_wise"),
        "anaRows": _group_quality_rows(df, "analyst_email", limit=20, grand_total=False)
    }


def _build_productivity(df: pd.DataFrame) -> Dict[str, Any]:
    metrics_dict = {}
    total_task = _sum(df, "total_task")
    total_aht = _sum(df, "total_aht")
    if total_task:
        metrics_dict["avgAht"] = round(metrics.calc_avg_aht(total_aht, total_task), 2)
        metrics_dict["totalTasks"] = int(total_task)

    return {
        "metrics": metrics_dict,
        "byAnalyst": _group_agg(df, "analyst_email", ["total_task", "total_aht"]),
        "byTL": _group_agg(df, "tl_name", ["total_task"]),
        "byAM": _group_agg(df, "am", ["total_task"]),
        "byQA": _group_agg(df, "qa_name", ["total_task"]),
        "byCategory": _group_agg(df, "category", ["total_task"]),
    }


def _build_quality(df: pd.DataFrame) -> Dict[str, Any]:
    metrics_dict = {}
    mis = _sum(df, "mis_fraud")
    tfraud = _sum(df, "total_fraud")
    wrn = _sum(df, "wrn_fraud")
    tclear = _sum(df, "total_clear")
    metrics_dict["intFar"] = round(metrics.calc_int_far(mis, tfraud), 4)
    metrics_dict["intFrr"] = round(metrics.calc_int_frr(wrn, tclear), 4)

    ext_mis = _sum(df, "ext_mis_fraud")
    ext_tfraud = _sum(df, "ext_total_fraud")
    ext_wrn = _sum(df, "ext_wrn_fraud")
    ext_tclear = _sum(df, "ext_total_clear")
    if ext_tfraud or ext_mis:
        metrics_dict["extFar"] = round(metrics.calc_ext_far(ext_mis, ext_tfraud), 4)
    if ext_wrn or ext_tclear:
        metrics_dict["extFrr"] = round(metrics.calc_ext_frr(ext_wrn, ext_tclear), 4)

    em_far_err = _sum(df, "ext_manual_far_error")
    em_far = _sum(df, "ext_manual_far")
    em_frr_err = _sum(df, "ext_manual_frr_error")
    em_frr = _sum(df, "ext_manual_frr")
    if em_far:
        metrics_dict["extManualFar"] = round(metrics.calc_ext_manual_far(em_far_err, em_far), 4)
    if em_frr:
        metrics_dict["extManualFrr"] = round(metrics.calc_ext_manual_frr(em_frr_err, em_frr), 4)

    ie_err = _sum(df, "int_ext_error")
    ie_aud = _sum(df, "int_ext_audits")
    ir_err = _sum(df, "int_raw_ext_error")
    ir_aud = _sum(df, "int_raw_ext_audits")
    if ie_aud:
        metrics_dict["intExt"] = round(metrics.calc_int_ext(ie_err, ie_aud), 4)
    if ir_aud:
        metrics_dict["intRaw"] = round(metrics.calc_int_raw(ir_err, ir_aud), 4)

    total_int_err = metrics.safe_add(mis, wrn)
    total_ext_err = metrics.safe_add(ext_mis, ext_wrn)
    total_int_aud = metrics.safe_add(tfraud, tclear)
    total_ext_aud = metrics.safe_add(ext_tfraud, ext_tclear)
    if total_int_aud or total_ext_aud:
        metrics_dict["overallError"] = round(
            metrics.calc_overall_error(total_int_err, total_ext_err, total_int_aud, total_ext_aud), 4
        )

    return {
        "metrics": metrics_dict,
        "byAnalyst": _group_agg(df, "analyst_email", ["mis_fraud", "total_fraud", "wrn_fraud", "total_clear"]),
        "byTL": _group_agg(df, "tl_name", ["mis_fraud", "total_fraud"]),
        "byAM": _group_agg(df, "am", ["mis_fraud", "total_fraud"]),
        "byQA": _group_agg(df, "qa_name", ["mis_fraud", "total_fraud"]),
        "qualityMix": []
    }


def _build_poa(df: pd.DataFrame, all_df: pd.DataFrame | None = None) -> Dict[str, Any]:
    poa_task = _sum(df, "poa_task")
    poa_aht = _sum(df, "poa_aht")
    metrics_dict = {}
    if poa_task:
        metrics_dict["poaAvgAht"] = round(metrics.calc_poa_avg_aht(poa_aht, poa_task), 2)
        metrics_dict["poaTasks"] = int(poa_task)

    poa_source = all_df if all_df is not None else df
    poa_months = [r.get("Month") for r in _monthly_summary(poa_source) if r.get("Month")]

    return {
        "metrics": metrics_dict,
        "byAnalyst": _group_agg(df, "analyst_email", ["poa_task", "poa_aht"]),
        "byTL": _group_agg(df, "tl_name", ["poa_task", "poa_aht"]),
        "byAM": _group_agg(df, "am", ["poa_task", "poa_aht"]),
        "byQA": _group_agg(df, "qa_name", ["poa_task", "poa_aht"]),
        "poaMonths": poa_months,
        "byAMMonth": _build_poa_entity_month_detail(poa_source, "am"),
        "byTLMonth": _build_poa_entity_month_detail(poa_source, "tl_name"),
        "byAnalystMonth": _build_poa_entity_month_detail(poa_source, "analyst_email", limit=50),
    }


def _build_trends(df: pd.DataFrame, view_mode: str) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    if df.empty:
        return {"viewMode": view_mode, "rows": rows}

    if view_mode == "daily":
        col = resolve_col(df, "date")
    else:
        col = resolve_col(df, "month")

    if col:
        for label, grp in df.groupby(col):
            row = _summary_from_df(grp, metrics.to_native(label), col)
            row["key"] = metrics.to_native(label)
            row["totalTasks"] = row.get("Total_Tasks", 0)
            row["Overall_Pct"] = round((row.get("Int_FAR_r", 0) + row.get("Int_FRR_r", 0)) * 100, 2)
            row["FAR_Pct"] = round(row.get("Int_FAR_r", 0) * 100, 2)
            row["FRR_Pct"] = round(row.get("Int_FRR_r", 0) * 100, 2)
            row["POA_Error_Pct"] = round(row.get("POA_Err_r", 0) * 100, 2)
            rows.append(row)

        if view_mode == "daily":
            rows.sort(key=lambda r: str(r.get(col) or ""))
        else:
            rows.sort(key=lambda r: _month_sort_key(r.get(col)))

    return {"viewMode": view_mode, "rows": rows}


def _build_alerts(df: pd.DataFrame) -> List[Dict[str, Any]]:
    alerts = []
    if df.empty:
        return alerts

    total_task = _sum(df, "total_task")
    if total_task == 0:
        alerts.append({"type": "warning", "message": "No tasks found for the selected period."})

    mis = _sum(df, "mis_fraud")
    tfraud = _sum(df, "total_fraud")
    far = metrics.calc_int_far(mis, tfraud)
    if far > 0.05:
        alerts.append({"type": "danger", "message": f"High Int FAR: {round(far*100,2)}%"})

    return alerts
