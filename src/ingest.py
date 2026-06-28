import csv
import zipfile
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import requests

from .config import (
    CLEAN_CSV_FILE,
    CSV_FILE,
    CSV_SOURCE,
    CSV_TABLE,
    DB_FILE,
    DATA_DIR,
    ZIP_FILE,
    SOURCE_FILE,
    UNDESA_DB_FILE,
    UNDESA_TABLE,
)


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)


def find_source_path() -> Path:
    if SOURCE_FILE.exists():
        return SOURCE_FILE

    excel_files = sorted(DATA_DIR.rglob("*.xlsx")) + sorted(DATA_DIR.rglob("*.xls"))
    if excel_files:
        for candidate in excel_files:
            if "undesa" in candidate.name.lower():
                return candidate
        return excel_files[0]

    csv_files = sorted(DATA_DIR.rglob("*.csv"))
    if csv_files:
        return csv_files[0]

    zip_files = sorted(DATA_DIR.rglob("*.zip"))
    if zip_files:
        return zip_files[0]

    raise FileNotFoundError(
        f"No source file found in {DATA_DIR}. Search paths: *.xlsx, *.xls, *.csv, *.zip"
    )


def cleanup_previous() -> None:
    for path in {CLEAN_CSV_FILE, DB_FILE, UNDESA_DB_FILE, ZIP_FILE}:
        if path.exists():
            path.unlink()
    if CSV_FILE.exists() and CSV_FILE != Path(CSV_SOURCE):
        CSV_FILE.unlink()


def find_year_csv_paths() -> list[Path]:
    paths = [
        path for path in sorted(DATA_DIR.rglob("*.csv"))
        if path.name not in {CSV_FILE.name, CLEAN_CSV_FILE.name}
    ]
    return [path for path in paths if path.is_file()]


def quote_column(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def download_csv() -> Path:
    ensure_directories()
    source_path = find_source_path()

    if source_path.exists():
        if source_path.suffix.lower() == ".zip":
            if ZIP_FILE.exists():
                ZIP_FILE.unlink()
            with zipfile.ZipFile(source_path) as archive:
                csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
                if not csv_names:
                    raise ValueError("Local archive does not contain a CSV file")
                csv_name = csv_names[0]
                with archive.open(csv_name) as source, CSV_FILE.open("wb") as target:
                    target.write(source.read())
            return CSV_FILE
        return source_path

    if CSV_FILE.exists():
        with CSV_FILE.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            if any(row and any(cell.strip() for cell in row) for row in reader):
                return CSV_FILE
        CSV_FILE.unlink()

    if ZIP_FILE.exists():
        ZIP_FILE.unlink()

    response = requests.get(str(CSV_SOURCE), timeout=60)
    response.raise_for_status()
    content = response.content

    if content.startswith(b"PK"):
        ZIP_FILE.write_bytes(content)
        with zipfile.ZipFile(ZIP_FILE) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_names:
                raise ValueError("Downloaded archive does not contain a CSV file")
            csv_name = csv_names[0]
            with archive.open(csv_name) as source, CSV_FILE.open("wb") as target:
                target.write(source.read())
        return CSV_FILE

    CSV_FILE.write_bytes(content)
    return CSV_FILE


def build_clean_csv(source_path: Path) -> Path:
    if CLEAN_CSV_FILE.exists() and CLEAN_CSV_FILE.stat().st_mtime >= source_path.stat().st_mtime:
        return CLEAN_CSV_FILE

    with source_path.open(newline="", encoding="utf-8") as source, CLEAN_CSV_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as target:
        reader = csv.reader(source)
        writer = csv.writer(target)

        header = None
        for row in reader:
            if row and any(cell.strip() for cell in row):
                header = row
                writer.writerow(header)
                break

        if header is None:
            raise ValueError("Could not find a non-empty header row in the CSV file")

        for row in reader:
            if row:
                writer.writerow(row)

    return CLEAN_CSV_FILE


def read_excel_source(source_path: Path) -> pd.DataFrame:
    # Only read the worksheet that the pipeline expects (Table 1)
    df = pd.read_excel(source_path, sheet_name="Table 1", header=10, engine="openpyxl")
    tidy = tidy_excel_dataframe(df)
    tidy["sheet_name"] = "Table 1"
    return tidy


def tidy_excel_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.iloc[:, :31].copy()
    df.columns = [str(col).strip() if not pd.isna(col) else "" for col in df.columns]

    meta = df.iloc[:, :7].copy()
    meta.columns = [
        "source_index",
        "destination",
        "coverage",
        "data_type",
        "destination_code",
        "origin",
        "origin_code",
    ]

    years = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2024]
    total = df.iloc[:, 7:15].copy()
    male = df.iloc[:, 15:23].copy()
    female = df.iloc[:, 23:31].copy()
    total.columns = years
    male.columns = years
    female.columns = years

    total = total.apply(pd.to_numeric, errors="coerce")
    male = male.apply(pd.to_numeric, errors="coerce")
    female = female.apply(pd.to_numeric, errors="coerce")

    row_count = len(meta)
    tidy = pd.DataFrame(
        {
            "destination": pd.Series(np.repeat(meta["destination"].values, len(years))),
            "destination_code": pd.Series(np.repeat(meta["destination_code"].values, len(years))),
            "origin": pd.Series(np.repeat(meta["origin"].values, len(years))),
            "origin_code": pd.Series(np.repeat(meta["origin_code"].values, len(years))),
            "coverage": pd.Series(np.repeat(meta["coverage"].values, len(years))),
            "data_type": pd.Series(np.repeat(meta["data_type"].values, len(years))),
            "year": pd.Series(np.tile(years, row_count)),
            "total": pd.Series(total.to_numpy().reshape(-1, order="C")),
            "male": pd.Series(male.to_numpy().reshape(-1, order="C")),
            "female": pd.Series(female.to_numpy().reshape(-1, order="C")),
        }
    )

    tidy = tidy.dropna(subset=["destination", "origin", "year"])
    tidy["year"] = tidy["year"].astype(int)
    tidy["destination"] = tidy["destination"].astype(str).str.strip()
    tidy["origin"] = tidy["origin"].astype(str).str.strip()
    tidy["destination_code"] = tidy["destination_code"].astype(object)
    tidy["origin_code"] = tidy["origin_code"].astype(object)
    return tidy


def load_csv_to_duckdb() -> None:
    source_path = download_csv()

    ensure_directories()
    conn = duckdb.connect(database=str(DB_FILE))
    conn.execute("CREATE SCHEMA IF NOT EXISTS analytics")

    if source_path.suffix.lower() in {".xlsx", ".xls"}:
        df = read_excel_source(source_path)
        conn.register("source_df", df)
        conn.execute(f"CREATE OR REPLACE TABLE {CSV_TABLE} AS SELECT * FROM source_df")
        conn.unregister("source_df")
    else:
        clean_path = build_clean_csv(source_path)
        conn.execute(
            f"CREATE OR REPLACE TABLE {CSV_TABLE} AS SELECT * FROM read_csv_auto('{clean_path}', header=True)"
        )

    conn.close()


def load_year_csvs_to_duckdb() -> None:
    year_csv_paths = find_year_csv_paths()
    if not year_csv_paths:
        raise FileNotFoundError(f"No year CSV files found under {DATA_DIR}")

    ensure_directories()
    conn = duckdb.connect(database=str(DB_FILE))
    conn.execute("CREATE SCHEMA IF NOT EXISTS analytics")

    data_frames = []
    seen = set()
    superset_columns = []

    for path in year_csv_paths:
        df = pd.read_csv(
            path,
            header=0,
            encoding="utf-8",
            engine="python",
            sep=",",
            quotechar='"',
            skipinitialspace=True,
            dtype=str,
            keep_default_na=False,
            na_filter=False,
        )
        df.columns = [col.strip() for col in df.columns]
        df["data_period"] = path.parent.name
        df["source_file"] = path.name
        data_frames.append((path, df))

        for col in df.columns:
            if col not in seen:
                seen.add(col)
                superset_columns.append(col)

    if not superset_columns:
        conn.close()
        raise ValueError("Unable to infer columns from year CSV files")

    normalized_frames = []
    for _, df in data_frames:
        normalized_frames.append(df.reindex(columns=superset_columns))

    combined = pd.concat(normalized_frames, ignore_index=True)
    conn.register("year_df", combined)
    conn.execute(f"CREATE OR REPLACE TABLE {CSV_TABLE} AS SELECT * FROM year_df")
    conn.unregister("year_df")
    conn.close()


def load_undesa_to_duckdb() -> None:
    source_path = find_source_path()
    ensure_directories()
    conn = duckdb.connect(database=str(DB_FILE))
    conn.execute("CREATE SCHEMA IF NOT EXISTS analytics")

    if source_path.suffix.lower() in {".xlsx", ".xls"}:
        df = read_excel_source(source_path)
        conn.register("source_df", df)
        conn.execute(f"CREATE OR REPLACE TABLE {UNDESA_TABLE} AS SELECT * FROM source_df")
        conn.unregister("source_df")
    else:
        clean_path = build_clean_csv(source_path)
        conn.execute(
            f"CREATE OR REPLACE TABLE {UNDESA_TABLE} AS SELECT * FROM read_csv_auto('{clean_path}', header=True)"
        )
    conn.close()


def ingest() -> None:
    cleanup_previous()
    load_year_csvs_to_duckdb()
    load_undesa_to_duckdb()
