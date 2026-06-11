"""Parsers that turn MAWAQIT payloads into typed value objects."""

from __future__ import annotations

from typing import Any

from pymawaqit._parse_helpers import (
    as_str,
    extract_conf_data,
    mapping,
    parse_bool,
    parse_float,
    parse_int,
    str_tuple,
)
from pymawaqit.mosque import Announcement, Calendar, ConfData, Mosque, PrayerTimes


# Keys under which the search endpoint has been seen to wrap its result list.
_SEARCH_LIST_KEYS = ("data", "results", "mosques", "items")


def parse_search_results(data: Any) -> list[Mosque]:
    items = _as_result_list(data)
    return [parse_mosque(item) for item in items if isinstance(item, dict)]


def _as_result_list(data: Any) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in _SEARCH_LIST_KEYS:
            value = data.get(key)
            if isinstance(value, list):
                return value
    return []


def parse_mosque(data: Any) -> Mosque:
    item = mapping(data)
    return Mosque(
        uuid=as_str(item.get("uuid")),
        slug=as_str(item.get("slug")),
        name=as_str(item.get("name")),
        type=as_str(item.get("type")),
        association_name=as_str(item.get("associationName")),
        label=as_str(item.get("label")),
        localisation=as_str(item.get("localisation")),
        latitude=parse_float(item.get("latitude")),
        longitude=parse_float(item.get("longitude")),
        phone=as_str(item.get("phone")),
        email=as_str(item.get("email")),
        site=as_str(item.get("site")),
        payment_website=as_str(item.get("paymentWebsite")),
        image=as_str(item.get("image")),
        times=PrayerTimes.from_list(item.get("times")),
        iqama=str_tuple(item.get("iqama")),
        iqama_enabled=parse_bool(item.get("iqamaEnabled")),
        jumua=as_str(item.get("jumua")),
        jumua2=as_str(item.get("jumua2")),
        jumua3=as_str(item.get("jumua3")),
        jumua_as_duhr=parse_bool(item.get("jumuaAsDuhr")),
        closed=parse_bool(item.get("closed")),
        women_space=parse_bool(item.get("womenSpace")),
        janaza_prayer=parse_bool(item.get("janazaPrayer")),
        aid_prayer=parse_bool(item.get("aidPrayer")),
        children_courses=parse_bool(item.get("childrenCourses")),
        adult_courses=parse_bool(item.get("adultCourses")),
        ramadan_meal=parse_bool(item.get("ramadanMeal")),
        handicap_accessibility=parse_bool(item.get("handicapAccessibility")),
        ablutions=parse_bool(item.get("ablutions")),
        parking=parse_bool(item.get("parking")),
        raw=dict(item),
    )


def parse_announcement(data: Any) -> Announcement:
    item = mapping(data)
    return Announcement(
        id=parse_int(item.get("id")),
        uuid=as_str(item.get("uuid")),
        title=as_str(item.get("title")),
        content=as_str(item.get("content")),
        image=as_str(item.get("image")),
        video=as_str(item.get("video")),
        start_date=as_str(item.get("startDate")),
        end_date=as_str(item.get("endDate")),
        updated=as_str(item.get("updated")),
        duration=parse_int(item.get("duration")),
        is_mobile=parse_bool(item.get("isMobile")),
        is_desktop=parse_bool(item.get("isDesktop")),
        tv_orientation=as_str(item.get("tvOrientation")),
        raw=dict(item),
    )


def parse_announcements(items: Any) -> tuple[Announcement, ...]:
    if not isinstance(items, list):
        return ()
    return tuple(parse_announcement(item) for item in items if isinstance(item, dict))


def parse_calendar(months: Any, iqama_months: Any = None) -> Calendar:
    return Calendar(
        months=_parse_calendar_months(months, PrayerTimes.from_list),
        iqama=_parse_calendar_months(iqama_months, str_tuple),
        raw={"calendar": months, "iqamaCalendar": iqama_months},
    )


def _parse_calendar_months(months: Any, convert: Any) -> tuple[dict, ...]:
    if not isinstance(months, list):
        return ()
    parsed: list[dict] = []
    for month in months:
        days: dict[int, Any] = {}
        for key, values in mapping(month).items():
            day = parse_int(key)
            if day is not None:
                days[day] = convert(values)
        parsed.append(days)
    return tuple(parsed)


def parse_conf_data(html: str) -> ConfData:
    blob = extract_conf_data(html)
    return conf_data_from_dict(blob)


def conf_data_from_dict(blob: dict[str, Any]) -> ConfData:
    item = mapping(blob)
    # A real mosque blob always carries at least one identifying field; an empty
    # or placeholder object means extraction degraded, so signal rather than
    # hand back an all-None ConfData that looks like a mosque with no data.
    if not any(as_str(item.get(key)) for key in ("uuid", "slug", "name")):
        raise ValueError("confData blob is missing uuid/slug/name")
    return ConfData(
        uuid=as_str(item.get("uuid")),
        name=as_str(item.get("name")),
        slug=as_str(item.get("slug")),
        latitude=parse_float(item.get("latitude")),
        longitude=parse_float(item.get("longitude")),
        timezone=as_str(item.get("timezone")),
        country_code=as_str(item.get("countryCode")),
        times=PrayerTimes.from_list(item.get("times")),
        jumua=as_str(item.get("jumua")),
        calendar=parse_calendar(item.get("calendar"), item.get("iqamaCalendar")),
        announcements=parse_announcements(item.get("announcements")),
        events=parse_announcements(item.get("events")),
        raw=dict(item),
    )
