# pymawaqit

**pymawaqit** is a small Python client for [mawaqit.net](https://mawaqit.net), the platform behind prayer times for 8000+ mosques worldwide. It wraps the public search API and the per-mosque `confData` blob, so you get clean typed objects for mosques, today's prayer times, iqama offsets, the full-year calendar, and announcements, without manual HTML parsing.

The search endpoint needs no authentication and already embeds today's prayer times in every result. The per-mosque year calendar and announcements are not exposed by the public API, so they are read from the `confData` blob on each mosque's web page.

## Installation

```bash
pip install mawaqit-py
```

For local development:

```bash
uv sync
uv run python -m unittest discover -s tests
```

## Quick Start

```python
from pymawaqit import Mawaqit

with Mawaqit() as client:
    # Search by name or city
    for mosque in client.search("amsterdam"):
        print(mosque.name, mosque.times.prayers, "| Jumua:", mosque.jumua)

    # Nearest mosques to a coordinate
    nearest = client.nearby(48.8566, 2.3522)
    print(nearest[0].name, nearest[0].coordinates)

    # Full-year calendar for a specific mosque (by slug or Mosque object)
    calendar = client.calendar("grande-mosquee-de-paris")
    print("Jul 1:", calendar.day(7, 1).prayers)

    # Announcements
    for notice in client.announcements("grande-mosquee-de-paris"):
        print(notice.title, notice.start_date, "->", notice.end_date)
```

## Prayer times

Each mosque carries today's six clock values in `times`. Index 1 is sunrise/shuruq, not a prayer, so `PrayerTimes` keeps it separate:

```python
times = mosque.times
times.fajr, times.sunrise, times.dhuhr, times.asr, times.maghrib, times.isha
times.prayers          # {'fajr': ..., 'dhuhr': ..., 'asr': ..., 'maghrib': ..., 'isha': ...}
mosque.iqama_offsets   # {'fajr': '+10', 'dhuhr': '+10', ...}  minutes after the adhan
```

## API

`Mawaqit` is the only object you construct. Its public methods:

| Method | Returns | Description |
|--------|---------|-------------|
| `search(word=None, *, lat=None, lon=None, page=1)` | `list[Mosque]` | Search by text, or by coordinate (nearest first). |
| `nearby(lat, lon, *, page=1)` | `list[Mosque]` | Convenience wrapper for a coordinate search. |
| `iter_search(word=None, *, lat=None, lon=None, start_page=1, max_pages=None)` | `Iterator[Mosque]` | Page through results until one comes back empty. |
| `conf_data(mosque, *, lang="en")` | `ConfData` | The full confData blob: calendar, announcements, events. |
| `calendar(mosque, *, lang="en")` | `Calendar` | The full-year prayer-time calendar. |
| `announcements(mosque, *, lang="en")` | `list[Announcement]` | A mosque's current announcements. |

`mosque` arguments accept a `Mosque`, a slug string, or a full `mawaqit.net/{lang}/{slug}` URL.

Every value object has `.to_dict()` (pass `include_raw=True` to keep the original payload), and the untouched response is always on `.raw`.

## How it works

This library uses two public surfaces of mawaqit.net:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `mawaqit.net/api/2.0/mosque/search?word=` | GET | Search mosques by name/city, with today's times embedded. |
| `mawaqit.net/api/2.0/mosque/search?lat=&lon=` | GET | Nearest mosques to a coordinate. |
| `mawaqit.net/{lang}/{slug}` | GET | Mosque web page; embeds a `confData` JSON blob with the whole year's calendar and announcements. |

The per-mosque mobile endpoints (`mosque/{uuid}/times`, `mosque/{uuid}/calendar`, `favorite`, `statistic/mosque`) live behind an `Api-Access-Token` and are not used here.

The request transport, browser-fingerprint impersonation, and retry handling are internal details. Normal users only construct `Mawaqit()` and call the public methods above.

## Disclaimer

This is an unofficial library and is not affiliated with, authorized, maintained, sponsored, or endorsed by MAWAQIT or any of its affiliates. Use at your own risk.

This library only accesses publicly available mosque data through mawaqit.net's web API and pages. The APIs are undocumented and may change or break at any time. Please use it responsibly and avoid excessive requests that could burden MAWAQIT's infrastructure.

## License

AGPL-3.0
