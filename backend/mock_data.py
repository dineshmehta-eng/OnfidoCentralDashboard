"""
Mock data generator for local development and UI verification.
Activated when MOCK_DB=true in .env.
All response shapes mirror the real SQL-backed services exactly.
"""
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

from utils.dates import get_current_month_str
from filtering import apply_filters, filter_value

MONTHS = ["Jan-26", "Feb-26", "Mar-26", "Apr-26", "May-26"]
PROCESS_OVERVIEW_REFERENCE = {
    "Jan-26": {"total_task": 1181637, "avg_aht": 75.82, "poa_task": 77415, "poa_avg_aht": 229.57, "poa_err": 1.04, "ext_poa": 0.90, "cre": 31, "crq": 38, "int_ext": 2.39, "ext_ext": 1.43, "int_raw": 2.72, "ext_raw": 0.84, "int_far": 1.02, "ext_far": 1.58, "int_frr": 0.32, "ext_frr": 0.31, "ext_manual_far": 0.86, "ext_manual_frr": 0.52},
    "Feb-26": {"total_task": 1233481, "avg_aht": 73.83, "poa_task": 67763, "poa_avg_aht": 215.75, "poa_err": 0.91, "ext_poa": 0.54, "cre": 41, "crq": 65, "int_ext": 2.50, "ext_ext": 1.31, "int_raw": 3.89, "ext_raw": 0.91, "int_far": 1.38, "ext_far": 1.76, "int_frr": 0.26, "ext_frr": 0.24, "ext_manual_far": 1.33, "ext_manual_frr": 0.14},
    "Mar-26": {"total_task": 1288020, "avg_aht": 72.64, "poa_task": 69081, "poa_avg_aht": 219.66, "poa_err": 0.54, "ext_poa": 0.38, "cre": 66, "crq": 111, "int_ext": 5.26, "ext_ext": 2.84, "int_raw": 8.62, "ext_raw": 1.29, "int_far": 1.85, "ext_far": 1.34, "int_frr": 0.46, "ext_frr": 0.46, "ext_manual_far": 2.21, "ext_manual_frr": 0.28},
    "Apr-26": {"total_task": 1062370, "avg_aht": 71.37, "poa_task": 63993, "poa_avg_aht": 212.58, "poa_err": 0.87, "ext_poa": 0.52, "cre": 39, "crq": 82, "int_ext": 3.50, "ext_ext": 1.71, "int_raw": 4.78, "ext_raw": 0.97, "int_far": 1.67, "ext_far": 1.76, "int_frr": 0.35, "ext_frr": 0.22, "ext_manual_far": 2.69, "ext_manual_frr": 0.36},
    "May-26": {"total_task": 721859, "avg_aht": 77.43, "poa_task": 69340, "poa_avg_aht": 208.24, "poa_err": 0.92, "ext_poa": 0.44, "cre": 51, "crq": 243, "int_ext": 2.43, "ext_ext": 1.42, "int_raw": 4.14, "ext_raw": 1.68, "int_far": 2.15, "ext_far": 1.87, "int_frr": 0.23, "ext_frr": 0.45, "ext_manual_far": 4.93, "ext_manual_frr": 3.68},
}
ANALYSTS = [
    "alice@onfido.com", "bob@onfido.com", "charlie@onfido.com",
    "diana@onfido.com", "eve@onfido.com", "frank@onfido.com",
    "grace@onfido.com", "henry@onfido.com"
]
TLS = ["TL_Alice", "TL_Bob", "TL_Charlie"]
AMS = ["AM_North", "AM_South"]
QAS = ["QA_X", "QA_Y", "QA_Z"]
CATEGORIES = ["Doc", "POA", "Fraud", "Clear"]
LOCATIONS = ["Noida", "Hyderabad", "Remote"]
AONS = ["AON_A", "AON_B", "AON_C"]


def _split_total(total: int, parts: int) -> List[int]:
    base = total // parts
    remainder = total % parts
    return [base + (1 if i < remainder else 0) for i in range(parts)]


def _make_consolidated_rows(month: str, count: int = 24) -> List[Dict[str, Any]]:
    rows = []
    ref = PROCESS_OVERVIEW_REFERENCE[month]
    base_date = datetime.strptime(month, "%b-%y")
    task_parts = _split_total(ref["total_task"], count)
    poa_parts = _split_total(ref["poa_task"], count)
    for i in range(count):
        total_task = task_parts[i]
        total_aht = total_task * ref["avg_aht"]
        poa_task = poa_parts[i]
        poa_aht = poa_task * ref["poa_avg_aht"]
        poa_audits = random.randint(max(1, poa_task // 8), max(2, poa_task // 3)) if poa_task else 0
        poa_error = random.randint(0, min(4, poa_audits)) if poa_audits else 0
        ext_poa_audits = random.randint(max(1, poa_task // 10), max(2, poa_task // 4)) if poa_task else 0
        ext_poa_error = random.randint(0, min(4, ext_poa_audits)) if ext_poa_audits else 0
        mis_fraud = random.randint(0, 5)
        total_fraud = random.randint(mis_fraud, 20)
        wrn_fraud = random.randint(0, 3)
        total_clear = random.randint(50, 300)
        ext_mis = random.randint(0, 4)
        ext_tfraud = random.randint(ext_mis, 15)
        ext_wrn = random.randint(0, 3)
        ext_tclear = random.randint(40, 250)
        ext_extraction = random.randint(20, 120)
        ext_ext_error = random.randint(0, min(5, ext_extraction))
        ext_raw_extraction = random.randint(20, 120)
        ext_raw_error = random.randint(0, min(5, ext_raw_extraction))
        em_far_err = random.randint(0, 3)
        em_far = random.randint(em_far_err, 10)
        em_frr_err = random.randint(0, 2)
        em_frr = random.randint(em_frr_err, 10)
        ie_err = random.randint(0, 5)
        ie_aud = random.randint(ie_err, 20)
        ir_err = random.randint(0, 4)
        ir_aud = random.randint(ir_err, 18)

        rows.append({
            "Date": (base_date + timedelta(days=i % 28)).strftime("%Y-%m-%d"),
            "Month": month,
            "Analyst_Email": ANALYSTS[i % len(ANALYSTS)],
            "TL_Name": TLS[i % len(TLS)],
            "AM": AMS[i % len(AMS)],
            "QA_Name": QAS[i % len(QAS)],
            "Category": CATEGORIES[i % len(CATEGORIES)],
            "Location": LOCATIONS[i % len(LOCATIONS)],
            "AON_Wise": AONS[i % len(AONS)],
            "Total_Task": total_task,
            "Total_AHT": total_aht,
            "POA_Task": poa_task,
            "POA_AHT": poa_aht,
            "POA_Audits": poa_audits,
            "POA_Error": poa_error,
            "Ext_POA_Audits": ext_poa_audits,
            "Ext_POA_Error": ext_poa_error,
            "CRE": random.randint(0, 2),
            "CRQ": random.randint(0, 2),
            "Mis_Fraud": mis_fraud,
            "Total_Fraud": total_fraud,
            "WRN_Fraud": wrn_fraud,
            "Total_Clear": total_clear,
            "Ext_Mis_Fraud": ext_mis,
            "Ext_Total_Fraud": ext_tfraud,
            "Ext_WRN_Fraud": ext_wrn,
            "Ext_Total_Clear": ext_tclear,
            "Ext_Extraction": ext_extraction,
            "Ext_Ext_Error": ext_ext_error,
            "Ext_Raw_Extraction": ext_raw_extraction,
            "Ext_RawError": ext_raw_error,
            "Ext_Manual_FARError": em_far_err,
            "Ext_Manual_FAR": em_far,
            "Ext_Manual_FRRError": em_frr_err,
            "Ext_Manual_FRR": em_frr,
            "Int_Ext_Error": ie_err,
            "Int_Ext_Audits": ie_aud,
            "Int_Raw_ExtError": ir_err,
            "Int_Raw_Ext_Audits": ir_aud,
        })
    return rows


class MockStore:
    def __init__(self):
        self.rows = []
        for month in MONTHS:
            self.rows.extend(_make_consolidated_rows(month))

    def get_filters(self) -> Dict[str, Any]:
        return {
            "analysts": sorted(set(ANALYSTS)),
            "tls": sorted(set(TLS)),
            "ams": sorted(set(AMS)),
            "qas": sorted(set(QAS)),
            "categories": sorted(set(CATEGORIES)),
            "aons": sorted({r["AON_Wise"] for r in self.rows}),
            "locations": sorted(set(LOCATIONS)),
            "months": MONTHS,
        }

    def get_init(self) -> Dict[str, Any]:
        return {
            "success": True,
            "filters": self.get_filters(),
            "totalRows": len(self.rows),
            "minDate": "2026-01-01",
            "maxDate": "2026-05-31",
            "currentMonth": MONTHS[-1],
            "source": "MOCK"
        }

    def get_dashboard(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        def fval(*keys):
            return filter_value(filters, *keys)

        date_from = (filters.get("from") or filters.get("date_from") or "").strip()
        date_to = (filters.get("to") or filters.get("date_to") or "").strip()
        month = filters.get("month") or ("" if (date_from or date_to) else MONTHS[-1])
        view_mode = filters.get("viewMode", "daily")
        analyst_filter = fval("analyst", "AnalystEmail", "analyst_email")
        tl_filter = fval("tl", "TLName", "tl_name")
        am_filter = fval("am", "AM")
        qa_filter = fval("qa", "QAName", "qa_name")
        category_filter = fval("category", "Category")
        location_filter = fval("location", "Location")
        aon_filter = fval("aon_wise", "AONWise", "aon")
        has_scoped_filter = any([
            date_from, date_to, analyst_filter, tl_filter, am_filter,
            qa_filter, category_filter, location_filter, aon_filter
        ])

        # simple filter simulation. Keep an all-month copy for month-wise charts.
        all_filtered = list(self.rows)
        if analyst_filter:
            all_filtered = [r for r in all_filtered if r["Analyst_Email"] == analyst_filter]
        if tl_filter:
            all_filtered = [r for r in all_filtered if r["TL_Name"] == tl_filter]
        if am_filter:
            all_filtered = [r for r in all_filtered if r["AM"] == am_filter]
        if qa_filter:
            all_filtered = [r for r in all_filtered if r["QA_Name"] == qa_filter]
        if category_filter:
            all_filtered = [r for r in all_filtered if r["Category"] == category_filter]
        if location_filter:
            all_filtered = [r for r in all_filtered if r["Location"] == location_filter]
        if aon_filter:
            all_filtered = [r for r in all_filtered if r["AON_Wise"] == aon_filter]
        if date_from:
            all_filtered = [r for r in all_filtered if str(r["Date"]) >= date_from]
        if date_to:
            all_filtered = [r for r in all_filtered if str(r["Date"]) <= date_to]
        filtered = [r for r in all_filtered if not month or r["Month"] == month]

        total_task = sum(r["Total_Task"] for r in filtered)
        total_aht = sum(r["Total_AHT"] for r in filtered)
        avg_aht = round(total_aht / total_task, 2) if total_task else 0

        mis = sum(r["Mis_Fraud"] for r in filtered)
        tfraud = sum(r["Total_Fraud"] for r in filtered)
        wrn = sum(r["WRN_Fraud"] for r in filtered)
        tclear = sum(r["Total_Clear"] for r in filtered)
        int_far = round((mis / (tfraud + mis)) * 100, 2) if (tfraud + mis) else 0
        int_frr = round((wrn / (wrn + tclear)) * 100, 2) if (wrn + tclear) else 0

        ext_mis = sum(r["Ext_Mis_Fraud"] for r in filtered)
        ext_tfraud = sum(r["Ext_Total_Fraud"] for r in filtered)
        ext_wrn = sum(r["Ext_WRN_Fraud"] for r in filtered)
        ext_tclear = sum(r["Ext_Total_Clear"] for r in filtered)
        ext_far = round((ext_mis / (ext_tfraud + ext_mis)) * 100, 2) if (ext_tfraud + ext_mis) else 0
        ext_frr = round((ext_wrn / (ext_wrn + ext_tclear)) * 100, 2) if (ext_wrn + ext_tclear) else 0

        em_far_err = sum(r["Ext_Manual_FARError"] for r in filtered)
        em_far = sum(r["Ext_Manual_FAR"] for r in filtered)
        em_frr_err = sum(r["Ext_Manual_FRRError"] for r in filtered)
        em_frr = sum(r["Ext_Manual_FRR"] for r in filtered)
        ext_manual_far = round((em_far_err / em_far) * 100, 2) if em_far else 0
        ext_manual_frr = round((em_frr_err / em_frr) * 100, 2) if em_frr else 0

        ie_err = sum(r["Int_Ext_Error"] for r in filtered)
        ie_aud = sum(r["Int_Ext_Audits"] for r in filtered)
        ir_err = sum(r["Int_Raw_ExtError"] for r in filtered)
        ir_aud = sum(r["Int_Raw_Ext_Audits"] for r in filtered)
        int_ext = round((ie_err / ie_aud) * 100, 2) if ie_aud else 0
        int_raw = round((ir_err / ir_aud) * 100, 2) if ir_aud else 0
        overall_err = round(((mis + wrn + ext_mis + ext_wrn) / (tfraud + tclear + ext_tfraud + ext_tclear)) * 100, 2) if (tfraud + tclear + ext_tfraud + ext_tclear) else 0
        month_ref = PROCESS_OVERVIEW_REFERENCE.get(month)
        if month_ref and not has_scoped_filter:
            int_far = month_ref["int_far"] / 100
            int_frr = month_ref["int_frr"] / 100
            ext_far = month_ref["ext_far"] / 100
            ext_frr = month_ref["ext_frr"] / 100
            ext_manual_far = month_ref["ext_manual_far"] / 100
            ext_manual_frr = month_ref["ext_manual_frr"] / 100
            int_ext = month_ref["int_ext"] / 100
            int_raw = month_ref["int_raw"] / 100
            overall_err = month_ref["poa_err"] / 100

        def group_agg(rows, key, sums):
            out = {}
            for r in rows:
                k = r[key]
                if k not in out:
                    out[k] = {s: 0 for s in sums}
                    out[k][key] = k
                    out[k]["key"] = k
                    out[k]["name"] = k
                for s in sums:
                    out[k][s] += r[s]
            return list(out.values())

        def safe_div(n, d):
            return round(n / d, 2) if d else 0

        def month_summary(rows, use_reference_totals=False):
            grouped = {}
            sum_keys = [
                "Total_Task", "Total_AHT", "POA_Task", "POA_AHT", "POA_Audits", "POA_Error",
                "Ext_POA_Audits", "Ext_POA_Error", "CRE", "CRQ", "Mis_Fraud", "Total_Fraud",
                "WRN_Fraud", "Total_Clear", "Ext_Extraction", "Ext_Ext_Error",
                "Ext_Raw_Extraction", "Ext_RawError", "Ext_Mis_Fraud", "Ext_Total_Fraud",
                "Ext_WRN_Fraud", "Ext_Total_Clear", "Ext_Manual_FARError", "Ext_Manual_FAR",
                "Ext_Manual_FRRError", "Ext_Manual_FRR", "Int_Ext_Error", "Int_Ext_Audits",
                "Int_Raw_ExtError", "Int_Raw_Ext_Audits"
            ]
            for row in rows:
                bucket = grouped.setdefault(row["Month"], {key: 0 for key in sum_keys})
                for key in sum_keys:
                    bucket[key] += row.get(key, 0)

            out = []
            for label, row in grouped.items():
                total_task = row["Total_Task"]
                total_aht = row["Total_AHT"]
                poa_task = row["POA_Task"]
                poa_aht = row["POA_AHT"]
                poa_err_r = row["POA_Error"] / row["POA_Audits"] if row["POA_Audits"] else 0
                ext_poa_r = row["Ext_POA_Error"] / row["Ext_POA_Audits"] if row["Ext_POA_Audits"] else 0
                int_far_r = row["Mis_Fraud"] / (row["Total_Fraud"] + row["Mis_Fraud"]) if (row["Total_Fraud"] + row["Mis_Fraud"]) else 0
                int_frr_r = row["WRN_Fraud"] / (row["WRN_Fraud"] + row["Total_Clear"]) if (row["WRN_Fraud"] + row["Total_Clear"]) else 0
                ext_far_r = row["Ext_Mis_Fraud"] / (row["Ext_Total_Fraud"] + row["Ext_Mis_Fraud"]) if (row["Ext_Total_Fraud"] + row["Ext_Mis_Fraud"]) else 0
                ext_frr_r = row["Ext_WRN_Fraud"] / (row["Ext_WRN_Fraud"] + row["Ext_Total_Clear"]) if (row["Ext_WRN_Fraud"] + row["Ext_Total_Clear"]) else 0
                int_ext_r = row["Int_Ext_Error"] / row["Int_Ext_Audits"] if row["Int_Ext_Audits"] else 0
                int_raw_r = row["Int_Raw_ExtError"] / row["Int_Raw_Ext_Audits"] if row["Int_Raw_Ext_Audits"] else 0
                ext_ext_r = row["Ext_Ext_Error"] / row["Ext_Extraction"] if row["Ext_Extraction"] else 0
                ext_raw_r = row["Ext_RawError"] / row["Ext_Raw_Extraction"] if row["Ext_Raw_Extraction"] else 0
                ext_manual_far_r = row["Ext_Manual_FARError"] / row["Ext_Manual_FAR"] if row["Ext_Manual_FAR"] else 0
                ext_manual_frr_r = row["Ext_Manual_FRRError"] / row["Ext_Manual_FRR"] if row["Ext_Manual_FRR"] else 0

                summary = {
                    "Month": label,
                    "key": label,
                    "name": label,
                    "Task": total_task,
                    "Total_Task": total_task,
                    "Total_Tasks": total_task,
                    "AHT": safe_div(total_aht, total_task),
                    "Avg_AHT": safe_div(total_aht, total_task),
                    "Avg_AHT_S": safe_div(total_aht, total_task),
                    "POA_Task": poa_task,
                    "POA_AHT": safe_div(poa_aht, poa_task),
                    "POA_Avg_AHT": safe_div(poa_aht, poa_task),
                    "POA_Avg_AHT_S": safe_div(poa_aht, poa_task),
                    "CRE": row["CRE"],
                    "CRQ": row["CRQ"],
                    "POA_Err_r": poa_err_r,
                    "Ext_POA_r": ext_poa_r,
                    "Int_FAR_r": int_far_r,
                    "Int_FRR_r": int_frr_r,
                    "Ext_FAR_r": ext_far_r,
                    "Ext_FRR_r": ext_frr_r,
                    "Int_Ext_r": int_ext_r,
                    "Ext_Ext_r": ext_ext_r,
                    "Int_Raw_r": int_raw_r,
                    "Ext_Raw_r": ext_raw_r,
                    "Ext_Manual_FAR_r": ext_manual_far_r,
                    "Ext_Manual_FRR_r": ext_manual_frr_r,
                }
                ref = PROCESS_OVERVIEW_REFERENCE.get(label)
                if ref and use_reference_totals:
                    summary.update({
                        "Task": ref["total_task"],
                        "Total_Task": ref["total_task"],
                        "Total_Tasks": ref["total_task"],
                        "AHT": ref["avg_aht"],
                        "Avg_AHT": ref["avg_aht"],
                        "Avg_AHT_S": ref["avg_aht"],
                        "POA_Task": ref["poa_task"],
                        "POA_AHT": ref["poa_avg_aht"],
                        "POA_Avg_AHT": ref["poa_avg_aht"],
                        "POA_Avg_AHT_S": ref["poa_avg_aht"],
                        "CRE": ref["cre"],
                        "CRQ": ref["crq"],
                        "POA_Err_r": ref["poa_err"] / 100,
                        "Ext_POA_r": ref["ext_poa"] / 100,
                        "Int_FAR_r": ref["int_far"] / 100,
                        "Int_FRR_r": ref["int_frr"] / 100,
                        "Ext_FAR_r": ref["ext_far"] / 100,
                        "Ext_FRR_r": ref["ext_frr"] / 100,
                        "Int_Ext_r": ref["int_ext"] / 100,
                        "Ext_Ext_r": ref["ext_ext"] / 100,
                        "Int_Raw_r": ref["int_raw"] / 100,
                        "Ext_Raw_r": ref["ext_raw"] / 100,
                        "Ext_Manual_FAR_r": ref["ext_manual_far"] / 100,
                        "Ext_Manual_FRR_r": ref["ext_manual_frr"] / 100,
                    })
                for key in [
                    "POA_Err", "Ext_POA", "Int_FAR", "Int_FRR", "Ext_FAR", "Ext_FRR",
                    "Int_Ext", "Ext_Ext", "Int_Raw", "Ext_Raw", "Ext_Manual_FAR",
                    "Ext_Manual_FRR"
                ]:
                    summary[key] = f"{summary[key + '_r'] * 100:.2f}%"
                out.append(summary)
            return sorted(out, key=lambda r: MONTHS.index(r["Month"]) if r["Month"] in MONTHS else 999)

        def build_poa_entity_month_detail(rows, field, limit=None):
            grouped = {}
            months = sorted({r["Month"] for r in rows if r.get("Month")}, key=lambda m: MONTHS.index(m) if m in MONTHS else 999)
            for r in rows:
                name = r.get(field)
                month_key = r.get("Month")
                if not name or not month_key:
                    continue
                item = grouped.setdefault(name, {"all": [], "months": {}})
                item["all"].append(r)
                item["months"].setdefault(month_key, []).append(r)

            out = []
            for name, item in grouped.items():
                all_task = sum(r["POA_Task"] for r in item["all"])
                all_aht = sum(r["POA_AHT"] for r in item["all"])
                all_audits = sum(r["POA_Audits"] for r in item["all"])
                all_errors = sum(r["POA_Error"] for r in item["all"])
                all_ext_audits = sum(r["Ext_POA_Audits"] for r in item["all"])
                all_ext_errors = sum(r["Ext_POA_Error"] for r in item["all"])
                row = {
                    "key": name,
                    "name": name,
                    "totalPoaTask": all_task,
                    "POA_Task": all_task,
                    "POA_Avg_AHT": safe_div(all_aht, all_task),
                    "POA_Error_Pct": safe_div(all_errors, all_audits),
                    "Ext_POA_Error_Pct": safe_div(all_ext_errors, all_ext_audits),
                    "months": {},
                }
                for month_key in months:
                    mrows = item["months"].get(month_key, [])
                    task = sum(r["POA_Task"] for r in mrows)
                    aht = sum(r["POA_AHT"] for r in mrows)
                    audits = sum(r["POA_Audits"] for r in mrows)
                    errors = sum(r["POA_Error"] for r in mrows)
                    ext_audits = sum(r["Ext_POA_Audits"] for r in mrows)
                    ext_errors = sum(r["Ext_POA_Error"] for r in mrows)
                    row["months"][month_key] = {
                        "POA_Task": task,
                        "POA_AHT": safe_div(aht, task),
                        "POA_Avg_AHT": safe_div(aht, task),
                        "POA_Err_r": safe_div(errors, audits),
                        "POA_Error_Pct": safe_div(errors, audits),
                        "Ext_POA_r": safe_div(ext_errors, ext_audits),
                        "Ext_POA_Error_Pct": safe_div(ext_errors, ext_audits),
                    }
                out.append(row)
            out.sort(key=lambda r: r["totalPoaTask"], reverse=True)
            return out[:limit] if limit else out

        tl_rows = group_agg(filtered, "TL_Name", ["Total_Task", "Total_AHT"])
        for tr in tl_rows:
            tr["avgAht"] = safe_div(tr["Total_AHT"], tr["Total_Task"])

        am_rows = group_agg(filtered, "AM", ["Total_Task"])
        aon_rows = group_agg(filtered, "AON_Wise", ["Total_Task"])
        ana_rows = group_agg(filtered, "Analyst_Email", ["Total_Task", "Total_AHT"])
        for ar in ana_rows:
            ar["avgAht"] = safe_div(ar["Total_AHT"], ar["Total_Task"])

        prod_by_ana = group_agg(filtered, "Analyst_Email", ["Total_Task", "Total_AHT"])
        for pr in prod_by_ana:
            pr["avgAht"] = safe_div(pr["Total_AHT"], pr["Total_Task"])

        # Quality breakdown
        qual_by_ana = []
        for r in group_agg(filtered, "Analyst_Email", ["Mis_Fraud", "Total_Fraud", "WRN_Fraud", "Total_Clear"]):
            r["intFar"] = round((r["Mis_Fraud"] / (r["Total_Fraud"] + r["Mis_Fraud"])) * 100, 2) if (r["Total_Fraud"] + r["Mis_Fraud"]) else 0
            r["intFrr"] = round((r["WRN_Fraud"] / (r["WRN_Fraud"] + r["Total_Clear"])) * 100, 2) if (r["WRN_Fraud"] + r["Total_Clear"]) else 0
            qual_by_ana.append(r)

        # Trends
        if view_mode == "daily":
            trend_map = {}
            for r in filtered:
                d = r["Date"]
                trend_map[d] = trend_map.get(d, 0) + r["Total_Task"]
            trend_rows = [{"Date": k, "totalTasks": v} for k, v in sorted(trend_map.items())]
        else:
            trend_map = {}
            for r in filtered:
                m = r["Month"]
                trend_map[m] = trend_map.get(m, 0) + r["Total_Task"]
            trend_rows = [{"Month": k, "totalTasks": v} for k, v in sorted(trend_map.items())]

        # Alerts
        alerts = []
        if not filtered:
            alerts.append({"type": "warning", "message": "No tasks found for the selected period."})
        if int_far > 5:
            alerts.append({"type": "danger", "message": f"High Int FAR: {int_far}%"})

        return {
            "success": True,
            "currentMonth": month,
            "overview": {
                "metrics": {"totalTasks": total_task, "avgAht": avg_aht, "intFar": int_far, "intFrr": int_frr},
                "kpiExtra": {},
                "monthlySummary": month_summary(all_filtered, not has_scoped_filter),
                "dayTrend": [],
                "tlRows": tl_rows,
                "amRows": am_rows,
                "aonRows": aon_rows,
                "anaRows": ana_rows,
            },
            "productivity": {
                "metrics": {"totalTasks": total_task, "avgAht": avg_aht},
                "byAnalyst": prod_by_ana,
                "byTL": group_agg(filtered, "TL_Name", ["Total_Task"]),
                "byAM": group_agg(filtered, "AM", ["Total_Task"]),
                "byQA": group_agg(filtered, "QA_Name", ["Total_Task"]),
                "byCategory": group_agg(filtered, "Category", ["Total_Task"]),
            },
            "quality": {
                "metrics": {
                    "intFar": int_far,
                    "intFrr": int_frr,
                    "extFar": ext_far,
                    "extFrr": ext_frr,
                    "extManualFar": ext_manual_far,
                    "extManualFrr": ext_manual_frr,
                    "intExt": int_ext,
                    "intRaw": int_raw,
                    "overallError": overall_err,
                },
                "byAnalyst": qual_by_ana,
                "byTL": group_agg(filtered, "TL_Name", ["Mis_Fraud", "Total_Fraud"]),
                "byAM": group_agg(filtered, "AM", ["Mis_Fraud", "Total_Fraud"]),
                "byQA": group_agg(filtered, "QA_Name", ["Mis_Fraud", "Total_Fraud"]),
                "qualityMix": [],
            },
            "poa": {
                "metrics": {
                    "poaTasks": sum(r["POA_Task"] for r in filtered),
                    "poaAvgAht": round(sum(r["POA_AHT"] for r in filtered) / sum(r["POA_Task"] for r in filtered), 2) if any(r["POA_Task"] for r in filtered) else 0,
                },
                "byAnalyst": group_agg(filtered, "Analyst_Email", ["POA_Task", "POA_AHT"]),
                "byTL": group_agg(filtered, "TL_Name", ["POA_Task", "POA_AHT"]),
                "byAM": group_agg(filtered, "AM", ["POA_Task", "POA_AHT"]),
                "poaMonths": sorted({r["Month"] for r in all_filtered}, key=lambda m: MONTHS.index(m) if m in MONTHS else 999),
                "byAMMonth": build_poa_entity_month_detail(all_filtered, "AM"),
                "byTLMonth": build_poa_entity_month_detail(all_filtered, "TL_Name"),
                "byAnalystMonth": build_poa_entity_month_detail(all_filtered, "Analyst_Email", 50),
            },
            "trends": {"viewMode": view_mode, "rows": trend_rows},
            "alerts": {"alerts": alerts}
        }

    def get_etm(self, filters: Dict[str, Any] | None = None) -> Dict[str, Any]:
        doc, poa, skip = [], [], []
        task_types = ["Extraction Task", "Fraud Task", "Raw_Extraction Task", "Classification Task", "Address_Extraction Task", "Consistency Task", "Labelling Raw_Ext Task"]
        for month in MONTHS:
            base_date = datetime.strptime(month, "%b-%y")
            for i, analyst in enumerate(ANALYSTS):
                date_text = (base_date + timedelta(days=i + 1)).strftime("%Y-%m-%d")
                common = {
                    "date": date_text,
                    "month": month,
                    "am_name": AMS[i % len(AMS)],
                    "tl_name": TLS[i % len(TLS)],
                    "qa_name": QAS[i % len(QAS)],
                    "aon": AONS[i % len(AONS)],
                    "Category": CATEGORIES[i % len(CATEGORIES)],
                    "task_information_analyst_email": analyst,
                    "client_information_ims_client_name": f"Client_{(i % 4) + 1}",
                    "ims_client_ims_client_name": f"Client_{(i % 4) + 1}",
                    "task_information_task_type_old": task_types[i % len(task_types)],
                    "task_information_task_manual_processing_time_secs": PROCESS_OVERVIEW_REFERENCE[month]["avg_aht"],
                }
                doc.append({"Analyst_Email": analyst, "ETM": round(0.7 + (i % 5) * 0.07, 2), **common})
                poa.append({"Analyst_Email": analyst, "ETM": round(0.6 + (i % 4) * 0.08, 2), **common})
                skip.append({
                    "Analyst_Email": analyst,
                    "Skipped": i % 4,
                    "Reason": "System" if i % 2 else "Break",
                    "date": date_text,
                    "month": month,
                    "manual_tasks_events_event_data_unassigned_from_email": analyst,
                    "manual_tasks_events_event_data_task_type": task_types[i % len(task_types)],
                    "am_s_name": AMS[i % len(AMS)],
                    "tl_s_name": TLS[i % len(TLS)],
                    "qa_name": QAS[i % len(QAS)],
                    "aon": AONS[i % len(AONS)],
                    "Category": CATEGORIES[i % len(CATEGORIES)],
                    "slot": f"{6 + (i % 4):02d}:00-{7 + (i % 4):02d}:00",
                })
        doc = apply_filters(doc, filters)
        poa = apply_filters(poa, filters)
        skip = apply_filters(skip, filters)
        return {"success": True, "etm": {"doc_etm": doc, "poa_etm": poa}, "taskSkip": {"task_skip": skip}}

    def search_analyst(self, email: str) -> Dict[str, Any]:
        query = (email or "").strip().lower()
        matches = [r for r in self.rows if query in r["Analyst_Email"].lower() or query in r["Analyst_Email"].split("@")[0].lower()]
        if not matches:
            return {"success": False, "error": "Analyst not found for this Onfido Mail ID / Analyst Email."}
        main_email = matches[0]["Analyst_Email"]
        rows = [r for r in self.rows if r["Analyst_Email"] == main_email]

        def safe_div(n, d):
            return round(n / d, 4) if d else 0

        def metrics(rows):
            total_task = sum(r["Total_Task"] for r in rows)
            total_aht = sum(r["Total_AHT"] for r in rows)
            poa_task = sum(r["POA_Task"] for r in rows)
            poa_aht = sum(r["POA_AHT"] for r in rows)
            mis = sum(r["Mis_Fraud"] for r in rows)
            tfraud = sum(r["Total_Fraud"] for r in rows)
            wrn = sum(r["WRN_Fraud"] for r in rows)
            clear = sum(r["Total_Clear"] for r in rows)
            ext_mis = sum(r["Ext_Mis_Fraud"] for r in rows)
            ext_tfraud = sum(r["Ext_Total_Fraud"] for r in rows)
            ext_wrn = sum(r["Ext_WRN_Fraud"] for r in rows)
            ext_clear = sum(r["Ext_Total_Clear"] for r in rows)
            poa_err = sum(r["POA_Error"] for r in rows)
            poa_aud = sum(r["POA_Audits"] for r in rows)
            ext_poa_err = sum(r["Ext_POA_Error"] for r in rows)
            ext_poa_aud = sum(r["Ext_POA_Audits"] for r in rows)
            int_errors = mis + wrn + poa_err
            int_audits = tfraud + clear + poa_aud
            ext_errors = ext_mis + ext_wrn + ext_poa_err
            ext_audits = ext_tfraud + ext_clear + ext_poa_aud
            return {
                "Total_Tasks": total_task,
                "Total_AHT": total_aht,
                "Avg_AHT": round(total_aht / total_task, 2) if total_task else 0,
                "POA_Task": poa_task,
                "POA_AHT": poa_aht,
                "POA_Avg_AHT": round(poa_aht / poa_task, 2) if poa_task else 0,
                "Int_Audit_Total": int_audits,
                "Ext_Audit_Total": ext_audits,
                "Overall_Error_Pct": safe_div(int_errors + ext_errors, int_audits + ext_audits),
                "Int_FAR_Pct": safe_div(mis, tfraud + mis),
                "Int_FRR_Pct": safe_div(wrn, wrn + clear),
                "Ext_FAR_Pct": safe_div(ext_mis, ext_tfraud + ext_mis),
                "Ext_FRR_Pct": safe_div(ext_wrn, ext_wrn + ext_clear),
                "POA_Error_Pct": safe_div(poa_err, poa_aud),
                "Ext_POA_Error_Pct": safe_div(ext_poa_err, ext_poa_aud),
            }

        def pct(v):
            return f"{v * 100:.2f}%"

        monthly = []
        for month in MONTHS:
            mr = [r for r in rows if r["Month"] == month]
            if not mr:
                continue
            mm = metrics(mr)
            monthly.append({
                "month": month,
                "Total_Tasks": mm["Total_Tasks"],
                "Total_Task": mm["Total_Tasks"],
                "Avg_AHT": mm["Avg_AHT"],
                "POA_Task": mm["POA_Task"],
                "POA_Avg_AHT": mm["POA_Avg_AHT"],
                "Int_Audits": mm["Int_Audit_Total"],
                "Ext_Audits": mm["Ext_Audit_Total"],
                "Overall_Error": pct(mm["Overall_Error_Pct"]),
                "Int_FAR": pct(mm["Int_FAR_Pct"]),
                "Int_FRR": pct(mm["Int_FRR_Pct"]),
                "POA_Error": pct(mm["POA_Error_Pct"]),
                "Ext_POA": pct(mm["Ext_POA_Error_Pct"]),
                "CRE": sum(r["CRE"] for r in mr),
                "CRQ": sum(r["CRQ"] for r in mr),
                "INT EXT%": "0.00%",
                "EXT EXT%": "0.00%",
                "INT RAW%": "0.00%",
                "EXT RAW%": "0.00%",
                "EXT FAR%": pct(mm["Ext_FAR_Pct"]),
                "EXT FRR%": pct(mm["Ext_FRR_Pct"]),
                "EXT MANUAL FAR%": "0.00%",
                "EXT MANUAL FRR%": "0.00%",
            })

        by_date = {}
        for r in rows:
            by_date.setdefault(r["Date"], []).append(r)
        daily = []
        for date, dr in sorted(by_date.items()):
            dm = metrics(dr)
            daily.append({"key": date, "Total_Tasks": dm["Total_Tasks"], "Avg_AHT": dm["Avg_AHT"], "POA_Avg_AHT": dm["POA_Avg_AHT"], "Overall_Pct": round(dm["Overall_Error_Pct"] * 100, 2), "FAR_Pct": round(dm["Int_FAR_Pct"] * 100, 2), "FRR_Pct": round(dm["Int_FRR_Pct"] * 100, 2), "POA_Error_Pct": round(dm["POA_Error_Pct"] * 100, 2)})

        tl = rows[0]["TL_Name"]
        peer_rows = [r for r in self.rows if r["TL_Name"] == tl]
        peers = []
        for analyst in sorted({r["Analyst_Email"] for r in peer_rows}):
            ar = [r for r in peer_rows if r["Analyst_Email"] == analyst]
            am = metrics(ar)
            peers.append({"name": analyst.split("@")[0], "Total_Tasks": am["Total_Tasks"], "Overall_Error_Pct": am["Overall_Error_Pct"]})
        peers.sort(key=lambda r: r["Total_Tasks"], reverse=True)
        for idx, peer in enumerate(peers, start=1):
            peer["rank"] = idx

        attendance = [{"month": m["month"], "P": 20, "A": 1, "WO": 4, "LWP": 0, "CL": 1, "EL": 0, "UL": 1, "HD": 0, "Leave": 1} for m in monthly]
        my_rank = next((p["rank"] for p in peers if p["name"] == main_email.split("@")[0]), 0)
        return {
            "success": True,
            "email": main_email,
            "name": main_email.split("@")[0],
            "tl": tl,
            "am": rows[0]["AM"],
            "qa": rows[0]["QA_Name"],
            "aon": rows[0]["AON_Wise"],
            "category": rows[0]["Category"],
            "totalDays": len(by_date),
            "metrics": metrics(rows),
            "monthlyBreakdown": monthly,
            "dailyTrend": daily,
            "peerRanking": peers,
            "myRank": my_rank,
            "peerCount": len(peers),
            "attendanceMonthly": attendance,
            "attendanceDaily": [],
            "attendanceStatusList": ["P", "A", "WO", "LWP", "CL", "EL", "UL", "HD", "Leave"],
            "attendanceMatchedRows": len(attendance),
            "attendanceDatedRows": 0,
            "resolvedBy": "MOCK",
        }

    def get_live(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        order = ["DOC Live AHT", "Audits", "POA Live", "APR"]
        base_date = datetime.strptime(MONTHS[-1], "%b-%y")
        task_types = ["Visual", "Document", "Face", "Address"]
        clients = ["Client_A", "Client_B", "Client_C", "Client_D"]
        slots = ["06:00-07:00", "07:00-08:00", "08:00-09:00", "09:00-10:00"]

        def common_row(sheet: str, analyst: str, idx: int) -> Dict[str, Any]:
            dt = base_date + timedelta(days=idx % 28)
            date_text = dt.strftime("%Y-%m-%d")
            am = AMS[idx % len(AMS)]
            tl = TLS[idx % len(TLS)]
            aon = AONS[idx % len(AONS)]
            aht = random.randint(35, 125)
            return {
                "source": sheet,
                "date": date_text,
                "month": MONTHS[-1],
                "am_name": am,
                "tl_name": tl,
                "qa_name": QAS[idx % len(QAS)],
                "aon": aon,
                "Category": CATEGORIES[idx % len(CATEGORIES)],
                "slot": random.choice(slots),
                "task_information_analyst_email": analyst,
                "task_information_task_type_old": random.choice(task_types),
                "manual_tasks_events_event_data_task_type": random.choice(task_types),
                "task_information_task_manual_processing_time_secs": aht,
                "manual_processing_time_secs": aht,
                "ims_client_ims_client_name": random.choice(clients),
                "client_information_ims_client_name": random.choice(clients),
            }

        doc_rows = []
        poa_rows = []
        audit_rows = []
        apr_rows = []
        for i, analyst in enumerate(ANALYSTS):
            for j in range(4):
                idx = i * 4 + j
                doc_rows.append(common_row("DOC Live AHT", analyst, idx))
                poa = common_row("POA Live", analyst, idx + 3)
                poa.update({
                    "supported": random.randint(8, 40),
                    "unsupported": random.randint(0, 8),
                })
                poa_rows.append(poa)

                audit = common_row("Audits", analyst, idx + 6)
                is_error = random.random() < 0.12
                audit.update({
                    "classification_error": "Yes" if is_error else "No",
                    "was_there_a_classification_error": "Yes" if is_error else "No",
                    "Was there a Classification Error ? ( Yes/No )": "Yes" if is_error else "No",
                })
                audit_rows.append(audit)

                apr = common_row("APR", analyst, idx + 9)
                login = round(random.uniform(5.0, 8.5), 2)
                avail = round(random.uniform(70.0, 96.0), 2)
                apr.update({
                    "net_login_hours": login,
                    "avail": avail,
                    "availability": avail,
                    "task_information_task_manual_processing_time_secs": avail,
                    "manual_processing_time_secs": avail,
                })
                apr_rows.append(apr)

        sheets = {
            "DOC Live AHT": apply_filters(doc_rows, filters),
            "Audits": apply_filters(audit_rows, filters),
            "POA Live": apply_filters(poa_rows, filters),
            "APR": apply_filters(apr_rows, filters),
        }
        live = []
        for sheet_name in order:
            live.extend(sheets[sheet_name])
        return {"success": True, "order": order, "sheets": sheets, "live": live, "count": len(live)}

    def get_slot_util(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        slot = []
        util = []
        for i, analyst in enumerate(ANALYSTS):
            base = {
                "Analyst_Email": analyst,
                "AM": AMS[i % len(AMS)],
                "TL_Name": TLS[i % len(TLS)],
                "QA_Name": QAS[i % len(QAS)],
                "AON_Wise": AONS[i % len(AONS)],
                "Category": CATEGORIES[i % len(CATEGORIES)],
                "Month": "Jun-26",
            }
            for _ in range(2):
                slot.append({"Slot": random.choice(["Morning", "Evening"]), "Tasks": random.randint(10, 80), **base})
            util.append({"Utilization": round(random.uniform(0.6, 1.0), 2), **base})
        slot = apply_filters(slot, filters)
        util = apply_filters(util, filters)
        return {"success": True, "slotWisePerformance": slot, "utilization": util}

    def get_attrition(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        rows = []
        for i, analyst in enumerate(ANALYSTS):
            rows.append({
                "Analyst_Email": analyst,
                "AM": AMS[i % len(AMS)],
                "TL_Name": TLS[i % len(TLS)],
                "QA_Name": QAS[i % len(QAS)],
                "AON_Wise": AONS[i % len(AONS)],
                "Category": CATEGORIES[i % len(CATEGORIES)],
                "Tenure_Months": random.randint(1, 24),
                "Attrition_Risk": random.choice(["Low", "Medium", "High"]),
            })
        rows = apply_filters(rows, filters)
        return {"success": True, "attrition": rows, "count": len(rows)}

    def get_health(self) -> Dict[str, Any]:
        all_views = [
            "vw_dashboard_consolidated", "vw_slot_wise_performance", "vw_utilization",
            "vw_audits", "vw_poa_live", "vw_apr", "vw_tqbqmq", "vw_cre",
            "vw_doc_etm", "vw_doc_task_skip", "vw_poa_etm", "vw_agent_wise"
        ]
        all_tables = [
            "stg_consolidated", "stg_slot_wise_performance", "stg_utilization",
            "stg_audits", "stg_poa_live", "stg_apr", "stg_tqbqmq", "stg_cre",
            "stg_doc_etm", "stg_doc_task_skip", "stg_poa_etm", "stg_agent_wise",
            "etl_sync_log"
        ]
        return {
            "success": True,
            "db": {"database_name": "Onfido_DB (MOCK)", "server_time": datetime.now().isoformat()},
            "views": {v: True for v in all_views},
            "tables": {t: True for t in all_tables},
            "missingViews": [],
            "missingTables": [],
            "allOk": True
        }


mock_store = MockStore()
