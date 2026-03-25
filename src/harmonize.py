from pathlib import Path
import pandas as pd

from .cleaning import (
    find_date_column,
    standardize_date_index,
    detect_numeric_columns,
    clean_numeric_columns,
    add_provenance,
)
from .io_utils import ensure_dir, load_table


# ---------------------------------------------------------
# Save YEAR-only datasets
# ---------------------------------------------------------
def save_yearly(df_year, processed_root, rel_path):
    yearly_dir = Path(processed_root) / "years" / rel_path.parent
    ensure_dir(yearly_dir)
    df_year.to_parquet(yearly_dir / (rel_path.stem + ".parquet"))


# ---------------------------------------------------------
# Resample weekly + monthly
# ---------------------------------------------------------
def resample_to_frequencies(df, numeric_cols, weekly_freq, monthly_freq):
    agg = {col: "sum" for col in numeric_cols}
    weekly = df.resample(weekly_freq).agg(agg)
    monthly = df.resample(monthly_freq).agg(agg)
    return weekly, monthly


# ---------------------------------------------------------
# Main harmonization function
# ---------------------------------------------------------
def harmonize_single_file(path, settings, logger):
    try:
        df = load_table(path)
    except Exception as e:
        logger.error(f"Failed to load {path}: {e}")
        return None

    # -------------------------------
    # 1. Detect date column
    # -------------------------------
    date_col = find_date_column(df, settings["date_column_candidates"])

    # -------------------------------
    # 2. YEAR-only dataset (no date column)
    # -------------------------------
    if not date_col:
        year_cols = [c for c in df.columns if c.lower() == "year"]

        if year_cols:
            df_year = df.copy()
            df_year["year"] = pd.to_numeric(df_year[year_cols[0]], errors="coerce")
            df_year = df_year.dropna(subset=["year"])
            df_year["year"] = df_year["year"].astype(int)

            return {
                "yearly": df_year,
                "is_year_only": True
            }

        logger.info(f"Skipping non-time-series file: {path}")
        return None

    # -------------------------------
    # 3. YEAR-only dataset (date column contains only YYYY)
    # -------------------------------
    if df[date_col].astype(str).str.match(r"^\d{4}$").all():
        df_year = df.copy()
        df_year["year"] = pd.to_numeric(df_year[date_col], errors="coerce")
        df_year = df_year.dropna(subset=["year"])
        df_year["year"] = df_year["year"].astype(int)

        return {
            "yearly": df_year,
            "is_year_only": True
        }

    # -------------------------------
    # 4. Full time-series dataset
    # -------------------------------
    df = standardize_date_index(df, date_col)
    if df.empty:
        logger.warning(f"No valid dates in {path}, skipping.")
        return None

    numeric_cols = detect_numeric_columns(df, settings["numeric_column_patterns"])
    if not numeric_cols:
        logger.warning(f"No numeric columns in {path}, skipping.")
        return None

    df = clean_numeric_columns(df, numeric_cols)
    df = add_provenance(df, str(path))

    weekly, monthly = resample_to_frequencies(
        df,
        numeric_cols,
        settings["weekly_frequency"],
        settings["monthly_frequency"],
    )

    return {
        "weekly": weekly,
        "monthly": monthly,
        "is_year_only": False
    }


# ---------------------------------------------------------
# Save weekly + monthly
# ---------------------------------------------------------
def save_harmonized(weekly, monthly, processed_root, weekly_folder, monthly_folder, rel_path):
    weekly_dir = Path(processed_root) / weekly_folder / rel_path.parent
    monthly_dir = Path(processed_root) / monthly_folder / rel_path.parent

    ensure_dir(weekly_dir)
    ensure_dir(monthly_dir)

    weekly.to_parquet(weekly_dir / (rel_path.stem + ".parquet"))
    monthly.to_parquet(monthly_dir / (rel_path.stem + ".parquet"))
