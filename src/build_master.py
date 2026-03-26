import pandas as pd
from pathlib import Path
import json

def build_spine():
    spine = pd.DataFrame(
        index=pd.date_range("1980-01-01", "2030-12-31", freq="W-MON")
    )
    spine.index.name = "date"
    return spine

def load_and_prefix(path, prefix):
    df = pd.read_parquet(path)
    df = df.add_prefix(prefix + "_")
    return df

def merge_into_spine(spine, df):
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return spine.join(df, how="left")

def merge_acled_weekly(spine):
    acled_dir = Path(r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\weekly\Conflict\ACLED")
    for file in acled_dir.glob("*.parquet"):
        region_name = file.stem.split("_")[0].lower().replace("-", "_")
        prefix = f"acled_{region_name}"
        df = load_and_prefix(file, prefix)
        spine = merge_into_spine(spine, df)
    return spine

def merge_ucdp_weekly(spine):
    ucdp_dir = Path(r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\weekly\Conflict\UCDP")
    for file in ucdp_dir.glob("*.parquet"):
        prefix = "ucdp_" + file.stem.lower().replace("-", "_")
        df = load_and_prefix(file, prefix)
        spine = merge_into_spine(spine, df)
    return spine

def merge_gpr_weekly(spine):
    gpr_path = Path(r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\weekly\Events\Geopolitical Risk\data_gpr_export.parquet")
    df = load_and_prefix(gpr_path, "gpr")
    spine = merge_into_spine(spine, df)
    return spine

def merge_monthly(spine):
    monthly_dir = Path(r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\monthly")
    for file in monthly_dir.rglob("*.parquet"):
        parts = file.parts
        folder = parts[-2].lower().replace(" ", "_")
        prefix = f"{folder}_{file.stem.lower().replace('-', '_')}_monthly"
        df = load_and_prefix(file, prefix)
        df.index = pd.to_datetime(df.index)
        df = df.reindex(spine.index, method="ffill")
        spine = spine.join(df, how="left")
    return spine

def merge_yearly(spine):
    yearly_dir = Path(r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\years")
    for file in yearly_dir.rglob("*.parquet"):
        parts = file.parts
        folder = parts[-2].lower().replace(" ", "_")
        prefix = f"{folder}_{file.stem.lower().replace('-', '_')}_yearly"
        df = load_and_prefix(file, prefix)
        df.index = pd.to_datetime(df.index)
        df = df.reindex(spine.index, method="ffill")
        spine = spine.join(df, how="left")
    return spine

def get_metadata(col, source):
    """Maps column patterns to descriptions, units, and notes."""
    desc, unit, note = f"Indicator for {col}", "Standard units", ""
    
    if "acled" in source:
        note = "Sourced from Armed Conflict Location & Event Data Project (ACLED)."
        if "FATALITIES" in col:
            desc, unit = "Total reported fatalities from conflict events", "Count"
        elif "EVENTS" in col:
            desc, unit = "Total number of conflict events recorded", "Count"
        elif "EVENT_TYPE" in col:
            desc, unit = "Classification of the conflict event", "Category"
            
    elif "ucdp" in source:
        note = "Sourced from Uppsala Conflict Data Program (UCDP)."
        if "intensity_level" in col:
            desc, unit = "Conflict intensity level (e.g., minor vs war)", "Ordinal Scale"
        elif "side_a" in col or "side_b" in col:
            desc, unit = "Participants or parties involved in the conflict", "Entity Name"

    elif "gpr" in source:
        unit = "Index Points"
        desc = "Frequency of news articles related to geopolitical tensions"
        note = "Based on Caldara and Iacoviello methodology."
        if "SHARE" in col: unit = "Percentage (%)"

    elif "mobility" in source:
        unit = "Percent change (%)"
        note = "Baseline: median value for corresponding day Jan 3–Feb 6, 2020."
        if "retail" in col: desc = "Mobility trends for restaurants and shopping centers"
        elif "grocery" in col: desc = "Mobility trends for grocery markets and pharmacies"

    if "_yearly" in col:
        note += " Forward-filled from yearly source data."
    elif "_monthly" in col:
        note += " Forward-filled from monthly source data."

    return desc, unit, note

def main():
    # 1. Build Spine and Merge Data
    spine = build_spine()
    
    mobility_path = Path(r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\weekly\Black Swan\Global_Mobility_Report.parquet")
    mobility = load_and_prefix(mobility_path, "mobility")
    spine = merge_into_spine(spine, mobility)

    spine = merge_acled_weekly(spine)
    spine = merge_ucdp_weekly(spine)
    spine = merge_gpr_weekly(spine)
    spine = merge_monthly(spine)
    spine = merge_yearly(spine)
    
    # 2. Save Master Parquet
    out_dir = Path(r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\master")
    out_dir.mkdir(parents=True, exist_ok=True)
    spine.to_parquet(out_dir / "master.parquet")
    print(f"Master sheet saved: {len(spine.columns)} columns.")

    # 3. Generate Metadata JSON
    metadata = {
        "name": "Global Master Dataset",
        "created_at": pd.Timestamp.now().isoformat(),
        "rows": len(spine),
        "columns": len(spine.columns),
        "date_range": {"start": str(spine.index.min().date()), "end": str(spine.index.max().date())}
    }
    with open(out_dir / "master_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    # 4. Generate Schema JSON (Accesses 'spine' inside main)
    schema = {}
    for col in spine.columns:
        source_prefix = col.split("_")[0]
        desc, unit, note = get_metadata(col, source_prefix)
        schema[col] = {
            "dtype": str(spine[col].dtype),
            "source": source_prefix,
            "description": desc,
            "units": unit,
            "notes": note
        }
    with open(out_dir / "master_schema.json", "w") as f:
        json.dump(schema, f, indent=4)

    # 5. Generate Feature List
    with open(out_dir / "master_feature_list.txt", "w") as f:
        f.write("\n".join(spine.columns))

    print("Documentation generated successfully.")

if __name__ == "__main__":
    main()
