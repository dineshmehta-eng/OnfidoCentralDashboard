import os
from db import fetch_all
from typing import Dict, Any
from datetime import datetime, timedelta

def _count_month_day(rows: list, month_col: str = "month", date_col: str = "date") -> Dict[str, Any]:
    """Count rows by current month and yesterday from text date fields."""
    if not rows:
        return {"currentMonthTotal": 0, "dayMinus1Total": 0, "currentMonth": "", "dayMinus1": ""}

    # Detect current month from data or system date
    dates = [r.get(date_col, "") for r in rows if r.get(date_col)]
    months = [r.get(month_col, "") for r in rows if r.get(month_col)]

    # current month = most common month in data
    current_month = max(set(months), key=months.count) if months else ""

    # day minus 1 = most recent date - 1 day
    yesterday = ""
    if dates:
        # Try parsing latest date
        latest = dates[0]
        try:
            dt = datetime.strptime(str(latest).strip(), "%d-%b-%y")
            yesterday_dt = dt - timedelta(days=1)
            yesterday = yesterday_dt.strftime("%d-%b-%y")
        except Exception:
            yesterday = ""

    current_month_count = sum(1 for r in rows if r.get(month_col) == current_month)
    yesterday_count = sum(1 for r in rows if r.get(date_col) == yesterday)

    return {
        "currentMonthTotal": current_month_count,
        "dayMinus1Total": yesterday_count,
        "currentMonth": current_month,
        "dayMinus1": yesterday
    }


def get_etm_data() -> Dict[str, Any]:
    try:
        doc_etm = fetch_all("SELECT * FROM vw_doc_etm ORDER BY date DESC")
    except Exception:
        doc_etm = []

    try:
        poa_etm = fetch_all("SELECT * FROM vw_poa_etm ORDER BY date DESC")
    except Exception:
        poa_etm = []

    try:
        task_skip = fetch_all("SELECT * FROM vw_doc_task_skip ORDER BY date DESC")
    except Exception:
        task_skip = []

    # Compute analytics for DOC ETM
    doc_a = _count_month_day(doc_etm)
    doc_a["monthWise"] = []
    doc_a["amCurrentMonth"] = []
    doc_a["dayMinus1Wise"] = []
    doc_a["tlCurrentMonth"] = []
    doc_a["tlDayMinus1"] = []
    doc_a["aonCurrentMonth"] = []
    doc_a["aonDayMinus1"] = []
    doc_a["slotDay"] = []
    doc_a["analystDayTable"] = []
    doc_a["clientDayTable"] = []
    doc_a["docTypeDayTable"] = []

    # Compute analytics for POA ETM
    poa_a = _count_month_day(poa_etm)
    poa_a["monthWise"] = []
    poa_a["amCurrentMonth"] = []
    poa_a["dayMinus1Wise"] = []
    poa_a["tlCurrentMonth"] = []
    poa_a["tlDayMinus1"] = []
    poa_a["aonCurrentMonth"] = []
    poa_a["aonDayMinus1"] = []
    poa_a["slotDay"] = []
    poa_a["analystDayTable"] = []
    poa_a["clientDayTable"] = []
    poa_a["docTypeDayTable"] = []

    # Compute analytics for Task Skip
    skip_a = _count_month_day(task_skip)
    skip_a["monthWise"] = []
    skip_a["amCurrentMonth"] = []
    skip_a["dayMinus1Wise"] = []
    skip_a["tlCurrentMonth"] = []
    skip_a["tlDayMinus1"] = []
    skip_a["aonCurrentMonth"] = []
    skip_a["aonDayMinus1"] = []
    skip_a["slotDay"] = []
    skip_a["analystDayTable"] = []
    skip_a["clientDayTable"] = []
    skip_a["taskTypeDayTable"] = []

    return {
        "success": True,
        "etm": {
            "doc": {"analytics": doc_a, "source": "DOC ETM", "rows": doc_etm},
            "poa": {"analytics": poa_a, "source": "POA ETM", "rows": poa_etm},
            "doc_etm": doc_etm,
            "poa_etm": poa_etm
        },
        "taskSkip": {
            "analytics": skip_a,
            "source": "Task Skip",
            "task_skip": task_skip,
            "rowCount": len(task_skip),
            "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }
