import argparse

from .ingest import ingest
from .transform import create_summary_table, fetch_recent_trend, fetch_brazil_outflow


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Brazilian migration analytics pipeline."
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="all",
        choices=["ingest", "transform", "outflow", "all"],
        help="Select which step to run: ingest, transform, outflow, or all"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Limit the number of rows returned for summary or outflow queries"
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Optional year filter for Brazil outflow queries"
    )
    args = parser.parse_args()

    if args.mode in ("ingest", "all"):
        ingest()

    if args.mode in ("transform", "all", "outflow"):
        create_summary_table()
        print("Created analytics.migration_summary")

    if args.mode == "all":
        trend = fetch_recent_trend(args.limit)
        print("Top migration flows by total migrants:")
        for row in trend:
            print(row)

    if args.mode == "outflow":
        outflow = fetch_brazil_outflow(args.limit, year=args.year)
        if args.year is not None:
            print(f"Top destinations for migrants leaving Brazil in {args.year}:")
        else:
            print("Top destinations for migrants leaving Brazil:")
        for row in outflow:
            print(row)


if __name__ == "__main__":
    main()
