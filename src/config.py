from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_DIR = ROOT / "duckdb"
DB_FILE = DB_DIR / "brazil_migration.duckdb"
SOURCE_FILE = DATA_DIR / "undesa_pd_2024_ims_stock_by_sex_destination_and_origin.xlsx"
CSV_SOURCE = SOURCE_FILE
CSV_FILE = DATA_DIR / "migration_source.csv"
CLEAN_CSV_FILE = DATA_DIR / "migration_cleaned.csv"
ZIP_FILE = DATA_DIR / "migration_source.zip"
CSV_TABLE = "analytics.brazil_net_migration"
SUMMARY_TABLE = "analytics.migration_summary"