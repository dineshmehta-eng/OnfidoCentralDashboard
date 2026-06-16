from db import fetch_all
from typing import Dict, Any
from filtering import apply_filters, enrich_rows_with_filter_metadata, has_dimension_filters

def _analytics(rows: list[dict], source: str) -> Dict[str, Any]:
    latest_sync = ""
    if rows:
        latest_sync = max(str(r.get("synced_at") or "") for r in rows)
    return {
        "currentMonth": "",
        "dayMinus1": "",
        "rowCount": len(rows),
        "currentMonthTotal": len(rows),
        "dayMinus1Total": 0,
        "lastUpdated": latest_sync,
        "source": source,
    }

def get_slot_utilization(filters: Dict[str, Any]) -> Dict[str, Any]:
    slot_perf = []
    util = []
    try:
        slot_perf = fetch_all("SELECT * FROM vw_slot_wise_performance ORDER BY bst_slot, ist_slot")
    except Exception:
        slot_perf = []

    try:
        util = fetch_all("SELECT * FROM vw_utilization ORDER BY analyst_email")
    except Exception:
        util = []

    if not slot_perf:
        try:
            slot_perf = fetch_all("""
                SELECT
                    bst_slot,
                    ist_slot,
                    tl_s_name,
                    am_s_name,
                    COUNT(*) as total_records,
                    SUM(TRY_CONVERT(FLOAT, total_time_spent_processing_mins)) as total_processing_mins,
                    SUM(TRY_CONVERT(FLOAT, total_time_spent_inactive_mins)) as total_inactive_mins,
                    SUM(TRY_CONVERT(FLOAT, total_time_spent_unassigned_mins)) as total_unassigned_mins,
                    AVG(TRY_CONVERT(FLOAT, REPLACE(avail, '%', ''))) as avg_avail_pct,
                    COUNT(DISTINCT analyst_email) as active_analysts,
                    MAX(synced_at) as synced_at
                FROM vw_apr
                GROUP BY bst_slot, ist_slot, tl_s_name, am_s_name
                ORDER BY bst_slot, ist_slot
            """)
        except Exception:
            slot_perf = []

    if not util:
        try:
            util = fetch_all("""
                SELECT
                    analyst_email,
                    tl_s_name,
                    am_s_name,
                    SUM(TRY_CONVERT(FLOAT, total_time_spent_processing_mins)) as processing_mins,
                    SUM(TRY_CONVERT(FLOAT, total_time_spent_inactive_mins)) as inactive_mins,
                    SUM(TRY_CONVERT(FLOAT, total_time_spent_unassigned_mins)) as unassigned_mins,
                    AVG(TRY_CONVERT(FLOAT, REPLACE(avail, '%', ''))) as avg_avail_pct,
                    COUNT(*) as total_records,
                    MAX(synced_at) as synced_at
                FROM vw_apr
                GROUP BY analyst_email, tl_s_name, am_s_name
                ORDER BY analyst_email
            """)
        except Exception:
            util = []

    if has_dimension_filters(filters):
        slot_perf = enrich_rows_with_filter_metadata(slot_perf)
        util = enrich_rows_with_filter_metadata(util)
    slot_perf = apply_filters(slot_perf, filters)
    util = apply_filters(util, filters)

    return {
        "success": True,
        "slotWisePerformance": slot_perf,
        "utilization": util,
        "slot": {
            "analytics": _analytics(slot_perf, "Slot Wise Performance"),
            "rows": slot_perf,
            "actualSheetName": "vw_slot_wise_performance",
        },
        "lastUpdated": max(
            [str(r.get("synced_at") or "") for r in slot_perf + util] or [""]
        ),
    }
