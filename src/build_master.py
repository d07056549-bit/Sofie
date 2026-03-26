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

# --- NEW MERGE FUNCTION FOR THE CSV ---
def merge_owid_conflict_yearly(spine):
    csv_path = Path(r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw\Conflict\countries-in-conflict-data.csv")
    if not csv_path.exists():
        print(f"Warning: {csv_path} not found. Skipping.")
        return spine

    print(f"Merging OWID Conflict deaths: {csv_path.name}")
    df = pd.read_csv(csv_path)
    
    # Rename the long column for easier handling
    death_col = "Deaths in ongoing conflicts in a country (best estimate) - Conflict type: all"
    df = df.rename(columns={death_col: "deaths"})

    # Pivot: Index = Year, Columns = Country, Values = deaths
    df_pivoted = df.pivot(index="Year", columns="Country", values="deaths")
    
    # Add prefix
    df_pivoted = df_pivoted.add_prefix("owid_conflict_")
    df_pivoted = df_pivoted.add_suffix("_deaths_yearly")

    # Convert Year to datetime (Jan 1st) and reindex/ffill to spine
    df_pivoted.index = pd.to_datetime(df_pivoted.index.astype(str) + "-01-01")
    df_pivoted = df_pivoted.reindex(spine.index, method="ffill")

    return spine.join(df_pivoted, how="left")

# --- EXISTING MERGE FUNCTIONS ---
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

# --- METADATA HELPER ---
def get_metadata(col, source):
    desc, unit, note = f"Indicator for {col}", "Standard units", ""
    
    if "acled" in source:
        note = "Sourced from Armed Conflict Location & Event Data Project (ACLED)."
        if "FATALITIES" in col: desc, unit = "Total reported fatalities from conflict events", "Count"
        elif "EVENTS" in col: desc, unit = "Total number of conflict events recorded", "Count"
        elif "EVENT_TYPE" in col: desc, unit = "Classification of the conflict event", "Category"
            
    elif "ucdp" in source:
        note = "Sourced from Uppsala Conflict Data Program (UCDP)."
        if "intensity_level" in col: desc, unit = "Conflict intensity level (e.g., minor vs war)", "Ordinal Scale"

    elif "owid_conflict" in col:
        country = col.replace("owid_conflict_", "").replace("_deaths_yearly", "").replace("_", " ")
        desc = f"Best estimate of annual deaths in ongoing conflicts for {country}."
        unit = "Count (Persons)"
        note = "Sourced from Our World in Data (OWID). Yearly data forward-filled to weekly."

    elif "gpr" in source:
        unit = "Index Points"
        desc = "Frequency of news articles related to geopolitical tensions"
        note = "Based on Caldara and Iacoviello methodology."

    elif "mobility" in source:
        unit = "Percent change (%)"
        note = "Baseline: median value for corresponding day Jan 3–Feb 6, 2020."

    if "_yearly" in col and "owid_conflict" not in col:
        note += " Forward-filled from yearly source data."
    elif "_monthly" in col:
        note += " Forward-filled from monthly source data."

    return desc, unit, note

def main():
    spine = build_spine()
    
    # Merge datasets
    mobility_path = Path(r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\weekly\Black Swan\Global_Mobility_Report.parquet")
    mobility = load_and_prefix(mobility_path, "mobility")
    spine = merge_into_spine(spine, mobility)

    spine = merge_acled_weekly(spine)
    spine = merge_ucdp_weekly(spine)
    spine = merge_gpr_weekly(spine)
    spine = merge_owid_conflict_yearly(spine)  # New function call
    spine = merge_monthly(spine)
    spine = merge_yearly(spine)
    
    # Save outputs
    out_dir = Path(r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed\master")
    out_dir.mkdir(parents=True, exist_ok=True)
    spine.to_parquet(out_dir / "master.parquet")

    # Generate Metadata
    metadata = {
        "name": "Global Master Dataset",
        "created_at": pd.Timestamp.now().isoformat(),
        "rows": len(spine),
        "columns": len(spine.columns),
        "date_range": {"start": str(spine.index.min().date()), "end": str(spine.index.max().date())}
    }
    with open(out_dir / "master_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    # Generate Schema
    schema = {}
    for col in spine.columns:
        source_prefix = col.split("_")[0]
        desc, unit, note = get_metadata(col, source_prefix)
        schema[col] = {"dtype": str(spine[col].dtype), "source": source_prefix, "description": desc, "units": unit, "notes": note}
    
    with open(out_dir / "master_schema.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=4)

    # Generate Feature List
    with open(out_dir / "master_feature_list.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(spine.columns))

    print(f"Build complete. Master sheet contains {len(spine.columns)} columns.")

if __name__ == "__main__":
    main()
