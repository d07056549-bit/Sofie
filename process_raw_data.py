import os
import pandas as pd

RAW_ROOT = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw"
PROCESSED_ROOT = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed"

os.makedirs(PROCESSED_ROOT, exist_ok=True)

def load_file(path):
    """Load CSV or Excel safely."""
    if path.endswith(".csv"):
        try:
            return pd.read_csv(path, low_memory=False)
        except Exception:
            return pd.read_csv(path, encoding="latin1", low_memory=False)

    elif path.endswith(".xlsx") or path.endswith(".xls"):
        return pd.read_excel(path)

    return None


def process_folder(folder_path, folder_name):
    """Merge all CSV/XLS/XLSX files in a folder into one master CSV."""
    dfs = []

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        if not os.path.isfile(file_path):
            continue

        if file.endswith((".csv", ".xlsx", ".xls")):
            df = load_file(file_path)
            if df is not None:
                df["source_file"] = file
                df["source_path"] = file_path
                dfs.append(df)

    if dfs:
        merged = pd.concat(dfs, ignore_index=True)
        output_path = os.path.join(PROCESSED_ROOT, f"{folder_name}.csv")
        merged.to_csv(output_path, index=False)
        print(f"Created master CSV: {output_path}")


def main():
    for root, dirs, files in os.walk(RAW_ROOT):
        # Only process folders that contain data files
        data_files = [f for f in files if f.endswith((".csv", ".xlsx", ".xls"))]

        if data_files:
            folder_name = root.replace(RAW_ROOT, "").strip("\\/").replace("\\", "_")
            if folder_name == "":
                folder_name = "root"

            process_folder(root, folder_name)

    print("\nAll master CSVs created.")


if __name__ == "__main__":
    main()
