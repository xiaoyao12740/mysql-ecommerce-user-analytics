from pathlib import Path
from src.database.sql_runner import query_file
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/"reports/tables"
ANALYTICS = ROOT / "sql" / "analytics"
EXPORTS = (
    "daily_kpis", "monthly_kpis", "conversion_funnel",
    "strict_conversion_funnel", "channel_funnel", "retention_cohort",
    "rfm_segments", "product_performance", "repeat_purchase",
    "behavior_transitions",
)
def export():
    OUT.mkdir(parents=True,exist_ok=True)
    result = {}
    for name in EXPORTS:
        sql_path = ANALYTICS / f"{name}.sql"
        df = query_file(sql_path)
        df.to_csv(OUT / f"{name}.csv", index=False)
        result[name] = df
        print(f"exported {name}: {len(df):,} rows from {sql_path.relative_to(ROOT)}")
    return result
if __name__=="__main__": print({k:len(v) for k,v in export().items()})
