from db import fetch_all
from typing import Dict, Any

def get_live_data(filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns live dashboard data in the shape the original GAS UI expects.
    The original frontend expects:
      {
        success: true,
        order: ['DOC Live AHT','Audits','POA Live','APR'],
        sheets: {
          'DOC Live AHT': [...],
          'Audits': [...],
          'POA Live': [...],
          'APR': [...]
        }
      }
    """
    try:
        audits = fetch_all("SELECT * FROM vw_audits ORDER BY synced_at DESC")
    except Exception:
        audits = []

    try:
        poa_live = fetch_all("SELECT * FROM vw_poa_live ORDER BY synced_at DESC")
    except Exception:
        poa_live = []

    try:
        apr = fetch_all("SELECT * FROM vw_apr ORDER BY synced_at DESC")
    except Exception:
        apr = []

    try:
        doc_etm = fetch_all("SELECT * FROM vw_doc_etm ORDER BY synced_at DESC")
    except Exception:
        doc_etm = []

    sheets = {
        "DOC Live AHT": doc_etm,
        "Audits": audits,
        "POA Live": poa_live,
        "APR": apr
    }
    live = []
    for sheet_name in ["DOC Live AHT", "Audits", "POA Live", "APR"]:
        for row in sheets.get(sheet_name, []):
            if isinstance(row, dict):
                live.append({"source": sheet_name, **row})

    return {
        "success": True,
        "order": ["DOC Live AHT", "Audits", "POA Live", "APR"],
        "sheets": sheets,
        "live": live,
        "count": len(live)
    }
