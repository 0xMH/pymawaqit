#!/usr/bin/env python3
"""Search mosques by city or name and print today's prayer times.

Usage:
    uv run examples/search_city.py amsterdam
    uv run examples/search_city.py "grande mosquee" --page 2
"""

import argparse

from mawaqit_py import Mawaqit


def main() -> None:
    parser = argparse.ArgumentParser(description="Search MAWAQIT mosques by name or city")
    parser.add_argument("word", help="City, name, or association to search for")
    parser.add_argument("--page", type=int, default=1, help="Result page (default 1)")
    args = parser.parse_args()

    with Mawaqit() as client:
        mosques = client.search(args.word, page=args.page)

    if not mosques:
        raise SystemExit("No mosques found")

    for mosque in mosques:
        print(f"\n{mosque.name}  ({mosque.localisation})")
        for prayer, time in mosque.times.prayers.items():
            print(f"  {prayer.title():<8} {time}")
        print(f"  Jumua: {mosque.jumua}")


if __name__ == "__main__":
    main()
