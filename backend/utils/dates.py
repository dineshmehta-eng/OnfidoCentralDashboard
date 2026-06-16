from datetime import datetime, date
from calendar import monthrange

def get_current_month_str() -> str:
    return datetime.now().strftime("%b-%y")

def parse_month_to_date(month_str: str) -> date:
    return datetime.strptime(month_str.strip(), "%b-%y").date()

def get_month_start_end(month_str: str):
    dt = parse_month_to_date(month_str)
    start = dt.replace(day=1)
    _, last_day = monthrange(dt.year, dt.month)
    end = dt.replace(day=last_day)
    return start, end

def format_date_iso(dt) -> str:
    if isinstance(dt, (datetime, date)):
        return dt.strftime("%Y-%m-%d")
    return str(dt)
