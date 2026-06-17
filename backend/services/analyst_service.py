from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List

from db import fetch_all


COLS = {
    "analyst": ["Analyst_Email", "AnalystEmail", "analyst_email", "Email"],
    "tl": ["TL_Name", "TLName", "tl_name"],
    "am": ["AM", "am"],
    "qa": ["QA_Name", "QAName", "qa_name"],
    "category": ["Category", "category"],
    "aon": ["AON_Wise", "AONWise", "aon_wise"],
    "location": ["Location", "location"],
    "date": ["Date", "date", "dt"],
    "month": ["Month", "month", "month_idx"],
    "total_task": ["Total_Task", "TotalTask", "total_task", "Tasks"],
    "total_aht": ["Total_AHT", "TotalAHT", "total_aht", "AHT"],
    "poa_task": ["POA_Task", "POATask", "poa_task"],
    "poa_aht": ["POA_AHT", "POAAHT", "poa_aht"],
    "poa_audits": ["POA_Audits", "POAAudits", "poa_audits"],
    "poa_error": ["POA_Error", "POAError", "poa_error"],
    "ext_poa_audits": ["Ext_POA_Audits", "ExtPOAAudits", "ext_poa_audits"],
    "ext_poa_error": ["Ext_POA_Error", "ExtPOAError", "ext_poa_error"],
    "cre": ["CRE", "cre"],
    "crq": ["CRQ", "crq"],
    "int_class_audits": ["Int_ClassAudits", "Int ClassAudits", "int_classaudits"],
    "int_class_error": ["Int_ClassError", "Int ClassError", "int_classerror"],
    "int_ext_audits": ["Int_Ext_Audits", "Int Ext Audits", "int_ext_audits"],
    "int_ext_error": ["Int_Ext_Error", "Int Ext Error", "int_ext_error"],
    "int_raw_audits": ["Int_Raw_Ext_Audits", "Int Raw Ext Audits", "int_raw_ext_audits"],
    "int_raw_error": ["Int_Raw_ExtError", "Int Raw ExtError", "int_raw_exterror", "int_raw_ext_error"],
    "int_add_ext_audits": ["Int_Add_Ext_Audits", "Int Add Ext Audits", "int_add_ext_audits"],
    "int_add_ext_error": ["Int_Add_Ext_Error", "Int Add Ext Error", "int_add_ext_error"],
    "int_cdq_audit": ["Int_CDQ_Audit", "Int CDQ Audit", "int_cdq_audit"],
    "int_cdq_error": ["Int_CDQ_Error", "Int CDQ Error", "int_cdq_error"],
    "int_fraud": ["Int_Fraud", "Int Fraud", "int_fraud"],
    "fraud_error": ["Fraud_Error", "Fraud Error", "fraud_error"],
    "ext_classification": ["Ext_Classification", "Ext Classification", "ext_classification"],
    "ext_class_error": ["Ext_ClassError", "Ext ClassError", "ext_classerror"],
    "ext_extraction": ["Ext_Extraction", "Ext Extraction", "ext_extraction"],
    "ext_ext_error": ["Ext_Ext_Error", "Ext Ext Error", "ext_ext_error"],
    "ext_add_extraction": ["Ext_Add_Extraction", "Ext Add Extraction", "ext_add_extraction"],
    "ext_add_error": ["Ext_AddError", "Ext AddError", "ext_adderror"],
    "ext_raw_extraction": ["Ext_Raw_Extraction", "Ext Raw Extraction", "ext_raw_extraction"],
    "ext_raw_error": ["Ext_RawError", "Ext RawError", "ext_rawerror", "ext_raw_error"],
    "ext_manual_far": ["Ext_Manual_FAR", "Ext Manual FAR", "ext_manual_far"],
    "ext_manual_far_error": ["Ext_Manual_FARError", "Ext Manual FARError", "ext_manual_farerror", "ext_manual_far_error"],
    "ext_manual_frr": ["Ext_Manual_FRR", "Ext Manual FRR", "ext_manual_frr"],
    "ext_manual_frr_error": ["Ext_Manual_FRRError", "Ext Manual FRRError", "ext_manual_frrerror", "ext_manual_frr_error"],
    "ext_total_fraud_audits": ["Ext_TotalFraud_Audis", "Ext TotalFraud Audis", "ext_totalfraud_audis"],
    "ext_fraud_error": ["Ext_FraudError", "Ext FraudError", "ext_frauderror"],
    "mis_fraud": ["Mis_Fraud", "Mis Fraud", "mis_fraud"],
    "total_fraud": ["Total_Fraud", "Total Fraud", "total_fraud"],
    "wrn_fraud": ["WRN_Fraud", "WRN Fraud", "wrn_fraud"],
    "total_clear": ["Total_Clear", "Total Clear", "total_clear"],
    "ext_mis_fraud": ["Ext_Mis_Fraud", "Ext Mis Fraud", "ext_mis_fraud"],
    "ext_total_fraud": ["Ext_Total_Fraud", "Ext Total Fraud", "ext_total_fraud"],
    "ext_wrn_fraud": ["Ext_WRN_Fraud", "Ext WRN Fraud", "ext_wrn_fraud"],
    "ext_total_clear": ["Ext_Total_Clear", "Ext Total Clear", "ext_total_clear"],
}


def _pick(row: Dict[str, Any], key: str, default: Any = "") -> Any:
    for name in COLS.get(key, [key]):
        if name in row and row[name] not in (None, ""):
            return row[name]
    return default


def _num(value: Any) -> float:
    try:
        text = str(value if value is not None else "").replace(",", "").replace("%", "").strip()
        return float(text) if text else 0.0
    except (TypeError, ValueError):
        return 0.0


def _sum(rows: Iterable[Dict[str, Any]], key: str) -> float:
    return sum(_num(_pick(row, key, 0)) for row in rows)


def _div(num: float, den: float) -> float:
    return num / den if den else 0.0


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _month_order(label: Any) -> int:
    months = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12}
    text = str(label or "").strip().lower()
    mon = next((m for m in months if text.startswith(m)), "")
    year_text = "".join(ch for ch in text[-4:] if ch.isdigit())
    year = int(year_text[-2:]) if year_text else 99
    if year < 100:
        year += 2000
    return year * 100 + months.get(mon, 99)


def _date_key(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    parsed = None
    for fmt in ("%Y-%m-%d", "%d-%b-%y", "%d-%b-%Y", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            parsed = datetime.strptime(str(value)[:10], fmt)
            break
        except ValueError:
            pass
    if parsed:
        return parsed.strftime("%Y-%m-%d")
    return str(value)[:10]


def _metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_tasks = _sum(rows, "total_task")
    total_aht = _sum(rows, "total_aht")
    poa_task = _sum(rows, "poa_task")
    poa_aht = _sum(rows, "poa_aht")

    int_audits = (
        _sum(rows, "int_class_audits") + _sum(rows, "int_ext_audits") + _sum(rows, "int_raw_audits")
        + _sum(rows, "int_add_ext_audits") + _sum(rows, "int_cdq_audit") + _sum(rows, "int_fraud")
        + _sum(rows, "poa_audits")
    )
    int_errors = (
        _sum(rows, "int_class_error") + _sum(rows, "int_ext_error") + _sum(rows, "int_raw_error")
        + _sum(rows, "int_add_ext_error") + _sum(rows, "int_cdq_error") + _sum(rows, "fraud_error")
        + _sum(rows, "poa_error")
    )
    ext_audits = (
        _sum(rows, "ext_classification") + _sum(rows, "ext_extraction") + _sum(rows, "ext_add_extraction")
        + _sum(rows, "ext_raw_extraction") + _sum(rows, "ext_manual_far") + _sum(rows, "ext_manual_frr")
        + _sum(rows, "ext_total_fraud_audits") + _sum(rows, "ext_poa_audits")
    )
    ext_errors = (
        _sum(rows, "ext_class_error") + _sum(rows, "ext_ext_error") + _sum(rows, "ext_add_error")
        + _sum(rows, "ext_raw_error") + _sum(rows, "ext_manual_far_error") + _sum(rows, "ext_manual_frr_error")
        + _sum(rows, "ext_fraud_error") + _sum(rows, "ext_poa_error")
    )

    mis = _sum(rows, "mis_fraud")
    total_fraud = _sum(rows, "total_fraud")
    wrn = _sum(rows, "wrn_fraud")
    clear = _sum(rows, "total_clear")
    ext_mis = _sum(rows, "ext_mis_fraud")
    ext_total_fraud = _sum(rows, "ext_total_fraud")
    ext_wrn = _sum(rows, "ext_wrn_fraud")
    ext_clear = _sum(rows, "ext_total_clear")

    poa_err = _sum(rows, "poa_error")
    poa_audits = _sum(rows, "poa_audits")
    ext_poa_err = _sum(rows, "ext_poa_error")
    ext_poa_audits = _sum(rows, "ext_poa_audits")

    return {
        "Total_Tasks": round(total_tasks),
        "Total_AHT": total_aht,
        "Avg_AHT": round(_div(total_aht, total_tasks), 2),
        "POA_Task": round(poa_task),
        "POA_AHT": poa_aht,
        "POA_Avg_AHT": round(_div(poa_aht, poa_task), 2),
        "Int_Audit_Total": round(int_audits),
        "Int_Error_Total": round(int_errors),
        "Ext_Audit_Total": round(ext_audits),
        "Ext_Error_Total": round(ext_errors),
        "Overall_Audit_Total": round(int_audits + ext_audits),
        "Overall_Error_Total": round(int_errors + ext_errors),
        "Overall_Error_Pct": _div(int_errors + ext_errors, int_audits + ext_audits),
        "Int_FAR_Pct": _div(mis, total_fraud + mis),
        "Int_FRR_Pct": _div(wrn, wrn + clear),
        "Ext_FAR_Pct": _div(ext_mis, ext_total_fraud + ext_mis),
        "Ext_FRR_Pct": _div(ext_wrn, ext_wrn + ext_clear),
        "POA_Error_Pct": _div(poa_err, poa_audits),
        "Ext_POA_Error_Pct": _div(ext_poa_err, ext_poa_audits),
        "CRE": round(_sum(rows, "cre")),
        "CRQ": round(_sum(rows, "crq")),
        "INT EXT%": _pct(_div(_sum(rows, "int_ext_error"), _sum(rows, "int_ext_audits"))),
        "EXT EXT%": _pct(_div(_sum(rows, "ext_ext_error"), _sum(rows, "ext_extraction"))),
        "INT RAW%": _pct(_div(_sum(rows, "int_raw_error"), _sum(rows, "int_raw_audits"))),
        "EXT RAW%": _pct(_div(_sum(rows, "ext_raw_error"), _sum(rows, "ext_raw_extraction"))),
        "EXT MANUAL FAR%": _pct(_div(_sum(rows, "ext_manual_far_error"), _sum(rows, "ext_manual_far"))),
        "EXT MANUAL FRR%": _pct(_div(_sum(rows, "ext_manual_frr_error"), _sum(rows, "ext_manual_frr"))),
    }


def _group(rows: Iterable[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        value = str(_pick(row, key, "")).strip()
        if value:
            grouped[value].append(row)
    return grouped


def _trend_rows(rows: List[Dict[str, Any]], key_name: str) -> List[Dict[str, Any]]:
    grouped = _group(rows, key_name)
    out = []
    for key, items in grouped.items():
        metric = _metrics(items)
        out.append({
            "key": _date_key(key) if key_name == "date" else key,
            "Total_Tasks": metric["Total_Tasks"],
            "Avg_AHT": metric["Avg_AHT"],
            "POA_Avg_AHT": metric["POA_Avg_AHT"],
            "Overall_Pct": round(metric["Overall_Error_Pct"] * 100, 2),
            "FAR_Pct": round(metric["Int_FAR_Pct"] * 100, 2),
            "FRR_Pct": round(metric["Int_FRR_Pct"] * 100, 2),
            "POA_Error_Pct": round(metric["POA_Error_Pct"] * 100, 2),
            "Overall_Audit_Total": metric["Overall_Audit_Total"],
            "Overall_Error_Total": metric["Overall_Error_Total"],
        })
    if key_name == "month":
        return sorted(out, key=lambda r: _month_order(r["key"]))
    return sorted(out, key=lambda r: str(r["key"]))


def _monthly_breakdown(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for month, items in _group(rows, "month").items():
        metric = _metrics(items)
        out.append({
            "month": month,
            "Total_Tasks": metric["Total_Tasks"],
            "Total_Task": metric["Total_Tasks"],
            "Avg_AHT": metric["Avg_AHT"],
            "POA_Task": metric["POA_Task"],
            "POA_Avg_AHT": metric["POA_Avg_AHT"],
            "Int_Audits": metric["Int_Audit_Total"],
            "Ext_Audits": metric["Ext_Audit_Total"],
            "Overall_Error": _pct(metric["Overall_Error_Pct"]),
            "Int_FAR": _pct(metric["Int_FAR_Pct"]),
            "Int_FRR": _pct(metric["Int_FRR_Pct"]),
            "POA_Error": _pct(metric["POA_Error_Pct"]),
            "Ext_POA": _pct(metric["Ext_POA_Error_Pct"]),
            "CRE": metric["CRE"],
            "CRQ": metric["CRQ"],
            "INT EXT%": metric["INT EXT%"],
            "EXT EXT%": metric["EXT EXT%"],
            "INT RAW%": metric["INT RAW%"],
            "EXT RAW%": metric["EXT RAW%"],
            "EXT FAR%": _pct(metric["Ext_FAR_Pct"]),
            "EXT FRR%": _pct(metric["Ext_FRR_Pct"]),
            "EXT MANUAL FAR%": metric["EXT MANUAL FAR%"],
            "EXT MANUAL FRR%": metric["EXT MANUAL FRR%"],
        })
    return sorted(out, key=lambda r: _month_order(r["month"]))


def _fetch_consolidated(where: str = "", params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    params = params or {}
    sql = "SELECT * FROM vw_dashboard_consolidated"
    if where:
        sql += " WHERE " + where
    try:
        return fetch_all(sql, params)
    except Exception:
        fallback = "SELECT * FROM stg_consolidated"
        if where:
            fallback += " WHERE " + where.lower().replace("analyst_email", "analyst_email").replace("tl_name", "tl_name")
        return fetch_all(fallback, params)


def _compact(value: Any, keep_digits: bool = True) -> str:
    text = str(value or "").lower()
    if "@" in text:
        text = text.split("@", 1)[0]
    chars = []
    for ch in text:
        if ch.isalpha() or (keep_digits and ch.isdigit()):
            chars.append(ch)
    return "".join(chars)


def _search_score(candidate: Any, query: Any) -> float:
    cand = str(candidate or "").strip().lower()
    qry = str(query or "").strip().lower()
    if not cand or not qry:
        return 0
    cand_local = cand.split("@", 1)[0]
    qry_local = qry.split("@", 1)[0]
    cand_compact = _compact(cand_local)
    qry_compact = _compact(qry_local)
    cand_name = _compact(cand_local, keep_digits=False)
    qry_name = _compact(qry_local, keep_digits=False)
    if cand == qry:
        return 120
    if cand_local == qry_local:
        return 115
    if cand_compact and cand_compact == qry_compact:
        return 110
    if cand_name and cand_name == qry_name:
        return 108
    if qry in cand or qry_local in cand_local:
        return 96
    if qry_compact and qry_compact in cand_compact:
        return 92
    if qry_name and qry_name in cand_name:
        return 90
    words = [w for w in qry.replace(".", " ").replace("_", " ").replace("-", " ").split() if w]
    if words and all(word in cand_local for word in words):
        return 88
    if qry_name and cand_name:
        ratio = SequenceMatcher(None, qry_name, cand_name).ratio()
        if ratio >= 0.82:
            return 70 + (ratio * 15)
    return 0


def _snapshot_rows() -> List[Dict[str, Any]]:
    try:
        from services import dashboard_service

        df = dashboard_service.get_consolidated_snapshot()
        return df.to_dict("records")
    except Exception:
        return _fetch_consolidated()


def _resolve_analyst(query: str, rows: List[Dict[str, Any]]) -> str:
    emails = sorted({str(_pick(row, "analyst", "")).strip() for row in rows if str(_pick(row, "analyst", "")).strip()})
    best_email = ""
    best_score = 0.0
    for email in emails:
        score = _search_score(email, query)
        if score > best_score:
            best_email = email
            best_score = score
    return best_email if best_score >= 82 else ""


def _same_analyst(value: Any, email: str) -> bool:
    left = str(value or "").strip().lower()
    right = str(email or "").strip().lower()
    return left == right or left.split("@", 1)[0] == right.split("@", 1)[0]


def _filter_rows(rows: List[Dict[str, Any]], filters: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    filters = filters or {}
    if not filters:
        return rows

    from filtering import filter_value, row_matches_filters

    month = filter_value(filters, "month", "Month")
    scoped = []
    for row in rows:
        if month and str(_pick(row, "month", "")).strip() != month:
            continue
        if not row_matches_filters(row, filters):
            continue
        scoped.append(row)
    return scoped


def search_analyst(email: str, filters: Dict[str, Any] | None = None) -> Dict[str, Any]:
    query = str(email or "").strip()
    if not query:
        return {"success": False, "error": "No email."}

    all_rows = _snapshot_rows()
    main_email = _resolve_analyst(query, all_rows)
    if not main_email:
        return {"success": False, "error": "Analyst not found for this Onfido Mail ID / Analyst Email."}

    analyst_rows = [row for row in all_rows if _same_analyst(_pick(row, "analyst"), main_email)]
    rows = _filter_rows(analyst_rows, filters)
    first = (rows or analyst_rows)[0]

    metric = _metrics(rows)
    tl = str(_pick(first, "tl", ""))
    am = str(_pick(first, "am", ""))
    qa = str(_pick(first, "qa", ""))
    aon = str(_pick(first, "aon", ""))
    category = str(_pick(first, "category", ""))

    peer_rows = [row for row in all_rows if str(_pick(row, "tl", "")).strip() == tl] if tl else analyst_rows
    peer_rows = _filter_rows(peer_rows, filters)
    ranking = []
    for analyst, items in _group(peer_rows, "analyst").items():
        m = _metrics(items)
        ranking.append({
            "name": analyst.split("@")[0],
            "Total_Tasks": m["Total_Tasks"],
            "Overall_Error_Pct": m["Overall_Error_Pct"],
        })
    ranking.sort(key=lambda r: (-r["Total_Tasks"], r["name"]))
    for idx, row in enumerate(ranking, start=1):
        row["rank"] = idx

    local_name = main_email.split("@")[0].lower()
    my_rank = next((row["rank"] for row in ranking if row["name"].lower() == local_name), 0)
    months = _monthly_breakdown(rows)
    attendance_monthly = [{"month": row["month"], "P": 0, "A": 0, "WO": 0, "LWP": 0, "CL": 0, "EL": 0, "UL": 0, "HD": 0, "Leave": 0} for row in months]

    dates = {_date_key(_pick(row, "date")) for row in rows if _date_key(_pick(row, "date"))}
    return {
        "success": True,
        "email": main_email,
        "name": main_email.split("@")[0],
        "tl": tl,
        "am": am,
        "qa": qa,
        "aon": aon,
        "category": category,
        "totalDays": len(dates),
        "metrics": metric,
        "monthlyBreakdown": months,
        "dailyTrend": _trend_rows(rows, "date"),
        "peerRanking": ranking,
        "myRank": my_rank,
        "peerCount": len(ranking),
        "attendanceMonthly": attendance_monthly,
        "attendanceDaily": [],
        "attendanceStatusList": ["P", "A", "WO", "LWP", "CL", "EL", "UL", "HD", "Leave"],
        "attendanceMatchedRows": 0,
        "attendanceDatedRows": 0,
        "resolvedBy": "SQL dashboard data",
    }
