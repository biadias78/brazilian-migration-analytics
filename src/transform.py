import duckdb

from pathlib import Path

from .config import (
    CSV_TABLE,
    SUMMARY_TABLE,
    UNDESA_DB_FILE,
    UNDESA_TABLE,
    DB_FILE,
    YEAR_SUMMARY_TABLE,
)


def connect(db_file: Path) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(database=str(db_file))


def normalize_name(name: str) -> str:
    return name.strip().lower().replace("_", " ")


def pick_column(columns, candidates):
    normalized = {normalize_name(col): col for col in columns}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    for candidate in candidates:
        for norm_name, original in normalized.items():
            if candidate in norm_name:
                return original
    return None


def describe_table(conn, table_name):
    result = conn.execute(f"DESCRIBE {table_name}").fetchall()
    return [row[0] for row in result]


def make_summary_table(conn, source_table: str, summary_table: str) -> None:
    conn.execute("CREATE SCHEMA IF NOT EXISTS analytics")

    columns = describe_table(conn, source_table)
    destination_col = pick_column(columns, ["destination", "destination region"])
    destination_code_col = pick_column(columns, ["location code of destination", "destination code"])
    origin_col = pick_column(columns, ["origin", "origin region"])
    origin_code_col = pick_column(columns, ["location code of origin", "origin code"])
    year_col = pick_column(columns, ["year", "period", "date"])
    total_col = pick_column(columns, ["total", "total migrants", "total number of migrants", "total number of international migrants"])
    male_col = pick_column(columns, ["male"])
    female_col = pick_column(columns, ["female"])

    if not destination_col or not origin_col or not year_col or not total_col:
        raise ValueError(
            f"Unable to detect required columns from source table: {columns}"
        )

    select_columns = [
        f'"{destination_col}" AS destination',
        f'"{destination_code_col}" AS destination_code' if destination_code_col else "NULL AS destination_code",
        f'"{origin_col}" AS origin',
        f'"{origin_code_col}" AS origin_code' if origin_code_col else "NULL AS origin_code",
        f'CAST("{year_col}" AS INTEGER) AS year',
        f'CAST("{total_col}" AS DOUBLE) AS total',
        f'CAST("{male_col}" AS DOUBLE) AS male' if male_col else "NULL::DOUBLE AS male",
        f'CAST("{female_col}" AS DOUBLE) AS female' if female_col else "NULL::DOUBLE AS female",
    ]

    conn.execute(
        f"CREATE OR REPLACE TABLE {summary_table} AS\n"
        f"SELECT {', '.join(select_columns)}\n"
        f"FROM {source_table}\n"
        f"WHERE \"{total_col}\" IS NOT NULL"
    )


def create_summary_table() -> None:
    conn = connect(UNDESA_DB_FILE)
    try:
        make_summary_table(conn, UNDESA_TABLE, SUMMARY_TABLE)
    finally:
        conn.close()


def quote_column(column_name: str) -> str:
    return '"' + column_name.replace('"', '""') + '"'


def make_year_summary_table(conn, source_table: str, summary_table: str) -> None:
    conn.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    columns = describe_table(conn, source_table)

    if "number" not in columns:
        raise ValueError(
            f"Unable to detect numeric count column in year-folder source table: {columns}"
        )

    group_columns = [col for col in columns if col != "number"]
    quoted_group_columns = [quote_column(col) for col in group_columns]
    select_columns = quoted_group_columns + ["SUM(CAST(number AS DOUBLE)) AS total"]

    if quoted_group_columns:
        conn.execute(
            f"CREATE OR REPLACE TABLE {summary_table} AS\n"
            f"SELECT {', '.join(select_columns)}\n"
            f"FROM {source_table}\n"
            f"GROUP BY {', '.join(quoted_group_columns)}"
        )
    else:
        conn.execute(
            f"CREATE OR REPLACE TABLE {summary_table} AS\n"
            f"SELECT SUM(CAST(number AS DOUBLE)) AS total\n"
            f"FROM {source_table}"
        )


def create_year_summary_table() -> None:
    conn = connect(DB_FILE)
    try:
        make_year_summary_table(conn, CSV_TABLE, YEAR_SUMMARY_TABLE)
    finally:
        conn.close()


def fetch_recent_trend(limit: int = 20):
    conn = connect(UNDESA_DB_FILE)
    result = conn.execute(
        f"SELECT destination, origin, year, total FROM {SUMMARY_TABLE} "
        f"ORDER BY total DESC LIMIT {limit}"
    )
    columns = [col[0] for col in result.description]
    rows = result.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


def fetch_brazil_outflow(limit: int = 20, year: int | None = None):
    conn = connect(UNDESA_DB_FILE)
    filters = ["(lower(origin) LIKE '%brazil%' OR lower(CAST(origin_code AS VARCHAR)) = 'bra')"]
    if year is not None:
        filters.append(f"year = {int(year)}")

    select_columns = [
        "destination",
        "destination_code",
        "SUM(total) AS total",
        "SUM(male) AS male",
        "SUM(female) AS female",
    ]
    group_by = "destination, destination_code"

    if year is not None:
        select_columns.append("CAST(year AS INTEGER) AS year")
        group_by += ", year"

    result = conn.execute(
        f"SELECT {', '.join(select_columns)} "
        f"FROM {SUMMARY_TABLE} "
        f"WHERE {' AND '.join(filters)} "
        f"GROUP BY {group_by} "
        f"ORDER BY total DESC LIMIT {limit}"
    )
    columns = [col[0] for col in result.description]
    rows = result.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]
