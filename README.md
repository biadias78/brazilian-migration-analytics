# brazilian-migration-analytics
This project provides an automated data pipeline to analyze Brazilian emigration trends over the last decade. It identifies primary destination countries and performs trend analysis to forecast future migration patterns. This repository showcases end-to-end data engineering practices, from raw data extraction to analytical modeling.

## Docker

Build the image:

```bash
docker build -t brazilian-migration-analytics:latest .
```

Run a container in the background and mount the project directory:

```bash
docker run -d --name brazil-analytics -v "$PWD":/app -w /app brazilian-migration-analytics:latest tail -f /dev/null
```

Run the pipeline directly inside the container:

```bash
docker exec brazil-analytics python -m src.main all
```

Open a shell inside the running container:

```bash
docker exec -it brazil-analytics bash
```

Stop and remove the container when finished:

```bash
docker stop brazil-analytics && docker rm brazil-analytics
```

## Development

The Python code lives in `src/`.

### Dataset

This project expects you to download the raw source data yourself and place it in the `data/` directory.

Supported data forms:

- `data/undesa_pd_2024_ims_stock_by_sex_destination_and_origin.xlsx`

Download the source file from:

https://www.un.org/development/desa/pd/sites/www.un.org.development.desa.pd/files/undesa_pd_2024_ims_stock_by_sex_destination_and_origin.xlsx

For the UN Excel source, the pipeline reads `Table 1` and reshapes the wide year columns into a tidy format.

> Important: the data file is not tracked in git. Keep your raw files in `data/` only.

### Install dependencies locally

If you want a local dev environment, install dependencies with pip or a virtual environment. Example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install duckdb pandas openpyxl numpy requests
```

The Docker image is also updated to install `duckdb`, `pandas`, `openpyxl`, `numpy`, and `requests`.

### Run the pipeline

Use the main module to ingest and transform data:

```bash
python -m src.main all
```

### Notes

- The ingestion code loads the UN Excel migration dataset from `data/undesa_pd_2024_ims_stock_by_sex_destination_and_origin.xlsx` and stores it in DuckDB.
- The transform step creates a summary table in DuckDB at `analytics.migration_summary`.
- The project uses `src/config.py` for paths and DuckDB configuration.
