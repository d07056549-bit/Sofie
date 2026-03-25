import pandas as pd

# ---------------------------------------------------------
# 1. Identify the date column
# ---------------------------------------------------------
def find_date_column(df, candidates):
    cols_lower = {c.lower(): c for c in df.columns}

    # First: try explicit candidate names
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]

    # Second: try to detect any column that can be parsed as dates
    for c in df.columns:
        try:
            # Try parsing WITHOUT infer_datetime_format
            pd.to_datetime(
                df[c],
                errors="raise",
                dayfirst=True
            )
            return c
        except Exception:
            continue

    return None
    
# ---------------------------------------------------------
# 2. Standardize the date index
# ---------------------------------------------------------
def standardize_date_index(df, date_col):
    df = df.copy()

    # Detect ISO format (YYYY-MM-DD)
    sample = df[date_col].astype(str).dropna().iloc[0]

    if sample.count("-") == 2 and len(sample.split("-")[0]) == 4:
        # ISO format → safe to parse without dayfirst
        df[date_col] = pd.to_datetime(
            df[date_col],
            errors="coerce",
            dayfirst=False
        )
    else:
        # Ambiguous formats → use dayfirst=True
        df[date_col] = pd.to_datetime(
            df[date_col],
            errors="coerce",
            dayfirst=True
        )

    df = df.dropna(subset=[date_col])
    df = df.set_index(date_col).sort_index()
    df.index.name = "date"

    return df



# ---------------------------------------------------------
# 3. Detect numeric columns
# ---------------------------------------------------------
def detect_numeric_columns(df, patterns):
    numeric_cols = []

    for col in df.columns:
        col_lower = col.lower()
        if any(p in col_lower for p in patterns):
            numeric_cols.append(col)

    if not numeric_cols:
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    return numeric_cols


# ---------------------------------------------------------
# 4. Clean numeric columns
# ---------------------------------------------------------
def clean_numeric_column(series):
    s = series.astype(str)
    s = s.str.replace(",", "", regex=False)
    s = s.str.replace(r"[<>]", "", regex=True)
    s = s.str.strip()
    return pd.to_numeric(s, errors="coerce")


def clean_numeric_columns(df, numeric_cols):
    df = df.copy()
    for col in numeric_cols:
        df[col] = clean_numeric_column(df[col])
    return df


# ---------------------------------------------------------
# 5. Add provenance metadata
# ---------------------------------------------------------
def add_provenance(df, source_file):
    df = df.copy()
    df["source_file"] = source_file
    return df
