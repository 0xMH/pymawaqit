#!/usr/bin/env python3
"""Find the mosques nearest to a coordinate.

Usage:
    uv run examples/nearest_mosques.py 48.8566 2.3522
    uv run examples/nearest_mosques.py 52.3702 4.8952 --page 2
"""

import argparse

from mawaqit_py import Mawaqit


def main() -> None:
    parser = argparse.ArgumentParser(description="Find mosques nearest to a coordinate")
    parser.add_argument("lat", type=float, help="Latitude")
    parser.add_argument("lon", type=float, help="Longitude")
    parser.add_argument("--page", type=int, default=1, help="Result page (default 1)")
    args = parser.parse_args()

    with Mawaqit() as client:
        mosques = client.nearby(args.lat, args.lon, page=args.page)

    if not mosques:
        raise SystemExit("No mosques found nearby")

    for mosque in mosques:
        coords = mosque.coordinates
        where = f"{coords[0]:.4f}, {coords[1]:.4f}" if coords else "?"
        print(f"{mosque.name:<45} [{where}]  Fajr {mosque.times.fajr}")


if __name__ == "__main__":
    main()
