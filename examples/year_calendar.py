#!/usr/bin/env python3
"""Pull a mosque's full-year prayer calendar and dump one day or a month.

Usage:
    uv run examples/year_calendar.py grande-mosquee-de-paris --month 7 --day 1
    uv run examples/year_calendar.py grande-mosquee-de-paris --month 12 --csv december.csv
"""

import argparse
import csv

from mawaqit_py import Mawaqit
from mawaqit_py.constants import TIME_NAMES


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch a mosque's full-year calendar")
    parser.add_argument("slug", help="Mosque slug (from a search result)")
    parser.add_argument("--month", type=int, help="Month 1-12 to print")
    parser.add_argument("--day", type=int, help="Day of month to print")
    parser.add_argument("--lang", default="en", help="Page language (default en)")
    parser.add_argument("--csv", help="Write the whole year to this CSV file")
    args = parser.parse_args()

    with Mawaqit() as client:
        calendar = client.calendar(args.slug, lang=args.lang)

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["month", "day", *TIME_NAMES])
            for month, day, times in calendar:
                writer.writerow([month, day, *[times[name] for name in TIME_NAMES]])
        print(f"Wrote year calendar to {args.csv}")
        return

    if args.month and args.day:
        times = calendar.day(args.month, args.day)
        if times is None:
            raise SystemExit(f"No entry for {args.month:02d}-{args.day:02d}")
        print(f"{args.month:02d}-{args.day:02d}:", dict(times.prayers))
        return

    if args.month:
        for month, day, times in calendar:
            if month == args.month:
                print(f"{month:02d}-{day:02d}", dict(times.prayers))
        return

    raise SystemExit("Pass --month (and optionally --day), or --csv")


if __name__ == "__main__":
    main()
