import yaml
from pathlib import Path

from .logging_conf import setup_logging
from .io_utils import list_data_files
from .harmonize import harmonize_single_file, save_harmonized, save_yearly


def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    logger = setup_logging()

    settings = load_yaml(Path("config/settings.yaml"))

    raw_root = Path(settings["raw_root"])
    processed_root = Path(settings["processed_root"])

    files = list_data_files(raw_root)
    logger.info(f"Found {len(files)} files under {raw_root}")

    for f in files:
        logger.info(f"Processing {f}")

        result = harmonize_single_file(f, settings, logger)
        if result is None:
            continue

        # Always compute relative path at the same indentation level
        rel_path = f.relative_to(raw_root)

        # YEAR‑ONLY datasets
        if result.get("is_year_only"):
            save_yearly(
                result["yearly"],
                processed_root,
                rel_path
            )
            logger.info(f"Saved YEAR-only dataset for {f}")
            continue

        # WEEKLY + MONTHLY datasets
        save_harmonized(
            result["weekly"],
            result["monthly"],
            processed_root,
            settings["weekly_folder"],
            settings["monthly_folder"],
            rel_path,
        )

        logger.info(f"Saved outputs for {f}")


if __name__ == "__main__":
    main()
