"""
Seed synthetic test data into Onfido_DB staging tables.
Run this after creating the database and views so you can verify
the dashboard end-to-end before connecting the real ETL.
"""
import os
import sys
import random
from datetime import datetime, timedelta

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "backend"))

from db import engine
from sqlalchemy import text

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MONTHS = ["Apr-26", "May-26", "Jun-26"]
ANALYSTS = [
    "analyst1@onfido.com", "analyst2@onfido.com", "analyst3@onfido.com",
    "analyst4@onfido.com", "analyst5@onfido.com"
]
TLS = ["TL_A", "TL_B", "TL_C"]
AMS = ["AM_1", "AM_2"]
QAS = ["QA_X", "QA_Y"]
CATEGORIES = ["Doc", "POA", "Fraud", "Clear"]
LOCATIONS = ["Noida", "Hyderabad", "Remote"]
AONS = ["AON_A", "AON_B"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def random_date(month_str: str):
    dt = datetime.strptime(month_str, "%b-%y")
    start = dt.replace(day=1)
    _, last_day = (31, 30)[dt.month - 1] if dt.month != 2 else (28, 29)
    # rough day pick
    day = random.randint(1, min(last_day, 28))
    return start + timedelta(days=day - 1)


def seed_consolidated():
    rows = []
    for month in MONTHS:
        for _ in range(150):
            total_task = random.randint(10, 200)
            total_aht = round(random.uniform(1.0, 8.0) * total_task, 2)
            poa_task = random.randint(0, total_task)
            poa_aht = round(random.uniform(1.2, 9.0) * poa_task, 2) if poa_task else 0
            mis_fraud = random.randint(0, 5)
            total_fraud = random.randint(mis_fraud, 20)
            wrn_fraud = random.randint(0, 3)
            total_clear = random.randint(50, 300)
            ext_mis_fraud = random.randint(0, 4)
            ext_total_fraud = random.randint(ext_mis_fraud, 15)
            ext_wrn_fraud = random.randint(0, 3)
            ext_total_clear = random.randint(40, 250)
            ext_manual_far_err = random.randint(0, 3)
            ext_manual_far = random.randint(ext_manual_far_err, 10)
            ext_manual_frr_err = random.randint(0, 2)
            ext_manual_frr = random.randint(ext_manual_frr_err, 10)
            int_ext_err = random.randint(0, 5)
            int_ext_aud = random.randint(int_ext_err, 20)
            int_raw_ext_err = random.randint(0, 4)
            int_raw_ext_aud = random.randint(int_raw_ext_err, 18)

            rows.append({
                "Date": random_date(month).strftime("%Y-%m-%d"),
                "Month": month,
                "Analyst_Email": random.choice(ANALYSTS),
                "TL_Name": random.choice(TLS),
                "AM": random.choice(AMS),
                "QA_Name": random.choice(QAS),
                "Category": random.choice(CATEGORIES),
                "Location": random.choice(LOCATIONS),
                "AON_Wise": random.choice(AONS),
                "Total_Task": total_task,
                "Total_AHT": total_aht,
                "POA_Task": poa_task,
                "POA_AHT": poa_aht,
                "Mis_Fraud": mis_fraud,
                "Total_Fraud": total_fraud,
                "WRN_Fraud": wrn_fraud,
                "Total_Clear": total_clear,
                "Ext_Mis_Fraud": ext_mis_fraud,
                "Ext_Total_Fraud": ext_total_fraud,
                "Ext_WRN_Fraud": ext_wrn_fraud,
                "Ext_Total_Clear": ext_total_clear,
                "Ext_Manual_FARError": ext_manual_far_err,
                "Ext_Manual_FAR": ext_manual_far,
                "Ext_Manual_FRRError": ext_manual_frr_err,
                "Ext_Manual_FRR": ext_manual_frr,
                "Int_Ext_Error": int_ext_err,
                "Int_Ext_Audits": int_ext_aud,
                "Int_Raw_ExtError": int_raw_ext_err,
                "Int_Raw_Ext_Audits": int_raw_ext_aud,
            })

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE stg_consolidated"))
        conn.execute(
            text("""
            INSERT INTO stg_consolidated (
                Date, Month, Analyst_Email, TL_Name, AM, QA_Name, Category, Location, AON_Wise,
                Total_Task, Total_AHT, POA_Task, POA_AHT, Mis_Fraud, Total_Fraud, WRN_Fraud, Total_Clear,
                Ext_Mis_Fraud, Ext_Total_Fraud, Ext_WRN_Fraud, Ext_Total_Clear,
                Ext_Manual_FARError, Ext_Manual_FAR, Ext_Manual_FRRError, Ext_Manual_FRR,
                Int_Ext_Error, Int_Ext_Audits, Int_Raw_ExtError, Int_Raw_Ext_Audits
            ) VALUES (
                :Date, :Month, :Analyst_Email, :TL_Name, :AM, :QA_Name, :Category, :Location, :AON_Wise,
                :Total_Task, :Total_AHT, :POA_Task, :POA_AHT, :Mis_Fraud, :Total_Fraud, :WRN_Fraud, :Total_Clear,
                :Ext_Mis_Fraud, :Ext_Total_Fraud, :Ext_WRN_Fraud, :Ext_Total_Clear,
                :Ext_Manual_FARError, :Ext_Manual_FAR, :Ext_Manual_FRRError, :Ext_Manual_FRR,
                :Int_Ext_Error, :Int_Ext_Audits, :Int_Raw_ExtError, :Int_Raw_Ext_Audits
            )
            """),
            rows,
        )
    print(f"Seeded {len(rows)} rows into stg_consolidated")


def seed_other_tables():
    # vw_slot_wise_performance -> stg_slot_wise_performance
    slot_rows = [
        {"Slot": "Morning", "Analyst_Email": a, "Tasks": random.randint(10, 80), "Month": "Jun-26"}
        for a in ANALYSTS for _ in range(3)
    ] + [
        {"Slot": "Evening", "Analyst_Email": a, "Tasks": random.randint(10, 80), "Month": "Jun-26"}
        for a in ANALYSTS for _ in range(3)
    ]

    # vw_utilization -> stg_utilization
    util_rows = [
        {"Analyst_Email": a, "Utilization": round(random.uniform(0.6, 1.0), 2), "Month": "Jun-26"}
        for a in ANALYSTS
    ]

    # vw_poa_live -> stg_poa_live
    live_rows = [
        {"Analyst_Email": a, "Live_POA": random.randint(0, 20), "Status": random.choice(["Active", "Idle"])}
        for a in ANALYSTS
    ]

    # vw_doc_etm -> stg_doc_etm
    doc_etm = [
        {"Analyst_Email": a, "ETM": round(random.uniform(0.5, 1.2), 2), "Month": "Jun-26"}
        for a in ANALYSTS
    ]

    # vw_poa_etm -> stg_poa_etm
    poa_etm = [
        {"Analyst_Email": a, "ETM": round(random.uniform(0.4, 1.1), 2), "Month": "Jun-26"}
        for a in ANALYSTS
    ]

    # vw_doc_task_skip -> stg_doc_task_skip
    task_skip = [
        {"Analyst_Email": a, "Skipped": random.randint(0, 5), "Reason": random.choice(["Break", "System"]), "Month": "Jun-26"}
        for a in ANALYSTS
    ]

    # vw_agent_wise -> stg_agent_wise
    agent_wise = [
        {"Analyst_Email": a, "Tenure_Months": random.randint(1, 24), "Attrition_Risk": random.choice(["Low", "Medium", "High"])}
        for a in ANALYSTS
    ]

    with engine.begin() as conn:
        for table, data in [
            ("stg_slot_wise_performance", slot_rows),
            ("stg_utilization", util_rows),
            ("stg_poa_live", live_rows),
            ("stg_doc_etm", doc_etm),
            ("stg_poa_etm", poa_etm),
            ("stg_doc_task_skip", task_skip),
            ("stg_agent_wise", agent_wise),
        ]:
            if not data:
                continue
            conn.execute(text(f"TRUNCATE TABLE {table}"))
            columns = list(data[0].keys())
            cols = ", ".join(columns)
            placeholders = ", ".join([f":{c}" for c in columns])
            conn.execute(text(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"), data)
            print(f"Seeded {len(data)} rows into {table}")


if __name__ == "__main__":
    print("Seeding test data...")
    seed_consolidated()
    seed_other_tables()
    print("Done. You can now open http://localhost:8000/ to verify the dashboard.")
