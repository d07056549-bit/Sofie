from pathlib import Path
import pandas as pd

def list_data_files(root, exts=(".csv", ".xlsx", ".xls")):
    root_path = Path(root)
    return [
        p for p in root_path.rglob("*")
        if p.is_file() and p.suffix.lower() in exts
    ]

def load_table(path):
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, dtype=str, low_memory=False)
    return pd.read_excel(path)

def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)
