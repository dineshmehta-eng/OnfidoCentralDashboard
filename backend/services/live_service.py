from db import fetch_all
from typing import Dict, Any
from filtering import apply_filters, enrich_rows_with_filter_metadata, has_dimension_filters

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

    if has_dimension_filters(filters):
        doc_etm = enrich_rows_with_filter_metadata(doc_etm)
        audits = enrich_rows_with_filter_metadata(audits)
        poa_live = enrich_rows_with_filter_metadata(poa_live)
        apr = enrich_rows_with_filter_metadata(apr)

    sheets = {
        "DOC Live AHT": apply_filters(doc_etm, filters),
        "Audits": apply_filters(audits, filters),
        "POA Live": apply_filters(poa_live, filters),
        "APR": apply_filters(apr, filters)
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
