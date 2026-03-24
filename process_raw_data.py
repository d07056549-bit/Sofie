import os
import pandas as pd

RAW_ROOT = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\raw"
PROCESSED_ROOT = r"C:\Users\Empok\Documents\GitHub\Sofie\Data\processed"

os.makedirs(PROCESSED_ROOT, exist_ok=True)

def process_file(input_path, output_path, folder_name, file_name):
    # Load CSV or Excel
    if file_name.endswith(".csv"):
    try:
        df = pd.read_csv(input_path, low_memory=False)
    except Exception:
        df = pd.read_csv(input_path, encoding="latin1", low_memory=False)

    elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
        df = pd.read_excel(input_path)

    else:
        return  # skip unsupported files

    # Add metadata columns
    df["dataset_folder"] = folder_name
    df["source_file"] = file_name
    df["source_path"] = input_path

    # Save as CSV in processed folder
    df.to_csv(output_path, index=False)
    print(f"Processed: {output_path}")

def main():
    for root, dirs, files in os.walk(RAW_ROOT):
        for file in files:
            if not (file.endswith(".csv") or file.endswith(".xlsx") or file.endswith(".xls")):
                continue

            input_path = os.path.join(root, file)
            folder_name = os.path.basename(root)

            # Output filename pattern: folder__file.csv
            output_filename = f"{folder_name}__{file}.csv"
            output_path = os.path.join(PROCESSED_ROOT, output_filename)

            process_file(input_path, output_path, folder_name, file)

    print("\nAll files processed successfully.")

if __name__ == "__main__":
    main()
