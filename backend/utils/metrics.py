import pandas as pd

def safe_div(numerator, denominator, default=0.0):
    try:
        num = float(numerator) if numerator is not None else 0.0
        den = float(denominator) if denominator is not None else 0.0
        if den != 0:
            return num / den
        return default
    except (TypeError, ValueError):
        return default

def safe_add(a, b):
    try:
        return (float(a) if a is not None else 0.0) + (float(b) if b is not None else 0.0)
    except (TypeError, ValueError):
        return 0.0

# Prevent numpy/pandas scalar serialization errors in FastAPI

def to_native(val):
    if val is None:
        return None
    # Let composite types pass through (handled by sanitize_dict recursion)
    if isinstance(val, (dict, list)):
        return val
    if isinstance(val, (pd.Timestamp, pd._libs.tslibs.timestamps.Timestamp)):
        return val.isoformat()
    # numpy scalar types
    if hasattr(val, "item"):
        return val.item()
    # pandas nullable types
    try:
        if pd.isna(val):
            return None
    except Exception:
        pass
    return val

def sanitize_dict(obj):
    if isinstance(obj, dict):
        return {k: sanitize_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_dict(v) for v in obj]
    return to_native(obj)

def calc_avg_aht(total_aht, total_task):
    return safe_div(total_aht, total_task)

def calc_poa_avg_aht(poa_aht, poa_task):
    return safe_div(poa_aht, poa_task)

def calc_int_far(mis_fraud, total_fraud):
    return safe_div(mis_fraud, safe_add(total_fraud, mis_fraud))

def calc_int_frr(wrn_fraud, total_clear):
    return safe_div(wrn_fraud, safe_add(wrn_fraud, total_clear))

def calc_ext_far(ext_mis_fraud, ext_total_fraud):
    return safe_div(ext_mis_fraud, safe_add(ext_total_fraud, ext_mis_fraud))

def calc_ext_frr(ext_wrn_fraud, ext_total_clear):
    return safe_div(ext_wrn_fraud, safe_add(ext_wrn_fraud, ext_total_clear))

def calc_ext_manual_far(ext_manual_far_error, ext_manual_far):
    return safe_div(ext_manual_far_error, ext_manual_far)

def calc_ext_manual_frr(ext_manual_frr_error, ext_manual_frr):
    return safe_div(ext_manual_frr_error, ext_manual_frr)

def calc_int_ext(int_ext_error, int_ext_audits):
    return safe_div(int_ext_error, int_ext_audits)

def calc_int_raw(int_raw_ext_error, int_raw_ext_audits):
    return safe_div(int_raw_ext_error, int_raw_ext_audits)

def calc_overall_error(total_int_error, total_ext_error, total_int_audits, total_ext_audits):
    num = safe_add(total_int_error, total_ext_error)
    den = safe_add(total_int_audits, total_ext_audits)
    return safe_div(num, den)
