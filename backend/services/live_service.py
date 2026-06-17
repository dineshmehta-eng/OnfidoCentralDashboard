from typing import Dict, Any
from filtering import apply_filters, enrich_rows_with_filter_metadata, filter_value, has_dimension_filters
from services.sql_snapshot import get_rows

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
    force_refresh = bool((filters or {}).get("forceRefresh"))
    try:
        audits = get_rows("vw_audits", "SELECT * FROM vw_audits ORDER BY synced_at DESC", force_refresh)
    except Exception:
        audits = []

    try:
        poa_live = get_rows("vw_poa_live", "SELECT * FROM vw_poa_live ORDER BY synced_at DESC", force_refresh)
    except Exception:
        poa_live = []

    try:
        apr = get_rows("vw_apr", "SELECT * FROM vw_apr ORDER BY synced_at DESC", force_refresh)
    except Exception:
        apr = []

    try:
        month = filter_value(filters, "month", "Month")
        if month:
            doc_etm = get_rows(
                'vw_doc_etm:{"month": "' + str(month) + '"}',
                "SELECT * FROM vw_doc_etm WHERE month_idx = :month ORDER BY date DESC",
                force_refresh,
                {"month": month},
            )
        else:
            doc_etm = get_rows("vw_doc_etm", "SELECT * FROM vw_doc_etm ORDER BY date DESC", force_refresh)
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
