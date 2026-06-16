from db import engine
from sqlalchemy import text
from utils.dates import get_current_month_str
from utils import metrics
from typing import Dict, Any, List
import pandas as pd
import calendar
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
    date_from = (filters.get("from") or filters.get("date_from") or "").strip()
    date_to = (filters.get("to") or filters.get("date_to") or "").strip()
    has_date_range = bool(date_from or date_to)
    month = filters.get("month") or ""
    view_mode = filters.get("viewMode", "daily")
    table_name = "stg_consolidated"

    if not month and not has_date_range:
        from db import fetch_one
        month_lookup_col = _qident(resolve_table_col(table_name, "month"))
        try:
            latest = fetch_one(f"SELECT MAX({month_lookup_col}) as latest_month FROM {table_name}", {})
            month = latest["latest_month"] if latest and latest.get("latest_month") else get_current_month_str()
        except Exception:
            month = get_current_month_str()

    base_where = ["1=1"]
    where_clauses = ["1=1"]
    params: Dict[str, Any] = {}
    all_params: Dict[str, Any] = {}

    month_col = resolve_table_col(table_name, "month")
    if month:
        where_clauses.append(f"{_qident(month_col)} = :month")
        params["month"] = month

    date_col = _qident(resolve_table_col(table_name, "date"))
    date_expr = f"COALESCE(TRY_CONVERT(date, {date_col}, 23), TRY_CONVERT(date, {date_col}, 106), TRY_CONVERT(date, {date_col}))"
    if date_from:
        where_clauses.append(f"{date_expr} >= TRY_CONVERT(date, :date_from, 23)")
        base_where.append(f"{date_expr} >= TRY_CONVERT(date, :date_from, 23)")
        params["date_from"] = date_from
        all_params["date_from"] = date_from
    if date_to:
        where_clauses.append(f"{date_expr} <= TRY_CONVERT(date, :date_to, 23)")
        base_where.append(f"{date_expr} <= TRY_CONVERT(date, :date_to, 23)")
        params["date_to"] = date_to
        all_params["date_to"] = date_to

    for api_key, logical_col in [
        ("analyst", "analyst_email"),
        ("tl", "tl_name"),
        ("am", "am"),
        ("qa", "qa_name"),
        ("category", "category"),
        ("location", "location"),
        ("aon_wise", "aon_wise"),
    ]:
        val = filters.get(api_key)
        if val and str(val).strip():
            db_col = _qident(resolve_table_col(table_name, logical_col))
            where_clauses.append(f"{db_col} = :{api_key}")
            base_where.append(f"{db_col} = :{api_key}")
            params[api_key] = str(val).strip()
            all_params[api_key] = str(val).strip()

    select_cols = [
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
        ("ext_raw_error", "ext_raw_error"),
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
    select_sql = "SELECT " + ", ".join(
        _select_expr(table_name, logical, alias) for logical, alias in select_cols
    ) + f" FROM {table_name} WHERE "

    sql = text(select_sql + ' AND '.join(where_clauses))
    all_sql = text(select_sql + ' AND '.join(base_where))
    df = pd.read_sql(sql, engine, params=params)
    all_df = pd.read_sql(all_sql, engine, params=all_params)

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


def _build_poa_entity_month_detail(df: pd.DataFrame, group_key: str, limit: int | None = None) -> List[Dict[str, Any]]:
    group_col = resolve_col(df, group_key)
    month_col = resolve_col(df, "month")
    date_col = resolve_col(df, "date")
    if df.empty or not group_col:
        return []

    month_labels = set()
    for _, row in df.iterrows():
        label = _poa_month_label(row, month_col, date_col)
        if label:
            month_labels.add(label)
    months = sorted(month_labels, key=_month_sort_key)

    rows: List[Dict[str, Any]] = []
    for label, grp in df.groupby(group_col):
        if label is None or str(label).strip() == "":
            continue
        total = _summary_from_df(grp, metrics.to_native(label), "name")
        row = {
            "key": metrics.to_native(label),
            "name": metrics.to_native(label),
            "totalPoaTask": total.get("POA_Task", 0),
            "POA_Task": total.get("POA_Task", 0),
            "POA_Avg_AHT": total.get("POA_Avg_AHT", 0),
            "POA_Error_Pct": total.get("POA_Err_r", 0),
            "Ext_POA_Error_Pct": total.get("Ext_POA_r", 0),
            "months": {},
        }
        if month_col or date_col:
            for month in months:
                mask = grp.apply(lambda r: _poa_month_label(r, month_col, date_col) == month, axis=1)
                month_grp = grp[mask]
                q = _summary_from_df(month_grp, month, "Month") if not month_grp.empty else {}
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
