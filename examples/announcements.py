#!/usr/bin/env python3
"""Print a mosque's current announcements and events.

Usage:
    uv run examples/announcements.py darul-quran-london
"""

import argparse

from pymawaqit import Mawaqit


def main() -> None:
    parser = argparse.ArgumentParser(description="Show a mosque's announcements")
    parser.add_argument("slug", help="Mosque slug (from a search result)")
    parser.add_argument("--lang", default="en", help="Page language (default en)")
    args = parser.parse_args()

    with Mawaqit() as client:
        conf = client.conf_data(args.slug, lang=args.lang)

    notices = list(conf.announcements) + list(conf.events)
    if not notices:
        raise SystemExit(f"{conf.name} has no announcements right now")

    for notice in notices:
        window = f"{notice.start_date} -> {notice.end_date}"
        print(f"\n[{window}] {notice.title}")
        if notice.content:
            print(notice.content)


if __name__ == "__main__":
    main()
