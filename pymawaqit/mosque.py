"""Typed value objects returned by the public MAWAQIT client."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any

from pymawaqit.constants import IQAMA_NAMES, PRAYER_NAMES, TIME_NAMES
from pymawaqit.models import DictValue, JsonDict


@dataclass(frozen=True, slots=True)
class PrayerTimes(DictValue):
    """The six daily clock values, with sunrise kept separate from the prayers."""

    fajr: str | None = None
    sunrise: str | None = None
    dhuhr: str | None = None
    asr: str | None = None
    maghrib: str | None = None
    isha: str | None = None

    @classmethod
    def from_list(cls, times: Sequence[str] | None) -> "PrayerTimes":
        values = list(times) if isinstance(times, (list, tuple)) else []
        values += [None] * (len(TIME_NAMES) - len(values))
        return cls(**dict(zip(TIME_NAMES, values, strict=False)))

    @property
    def prayers(self) -> dict[str, str | None]:
        """The five obligatory prayers, in order, excluding sunrise."""
        return {name: getattr(self, name) for name in PRAYER_NAMES}

    def __iter__(self) -> Iterator[tuple[str, str | None]]:
        return iter({name: getattr(self, name) for name in TIME_NAMES}.items())

    def __getitem__(self, name: str) -> str | None:
        if name not in TIME_NAMES:
            raise KeyError(name)
        return getattr(self, name)


@dataclass(frozen=True, slots=True)
class Mosque(DictValue):
    """A mosque with today's prayer times embedded, as returned by search."""

    uuid: str | None = None
    slug: str | None = None
    name: str | None = None
    type: str | None = None
    association_name: str | None = None
    label: str | None = None
    localisation: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    email: str | None = None
    site: str | None = None
    payment_website: str | None = None
    image: str | None = None
    times: PrayerTimes = field(default_factory=PrayerTimes)
    iqama: tuple[str, ...] = ()
    iqama_enabled: bool | None = None
    jumua: str | None = None
    jumua2: str | None = None
    jumua3: str | None = None
    jumua_as_duhr: bool | None = None
    closed: bool | None = None
    women_space: bool | None = None
    janaza_prayer: bool | None = None
    aid_prayer: bool | None = None
    children_courses: bool | None = None
    adult_courses: bool | None = None
    ramadan_meal: bool | None = None
    handicap_accessibility: bool | None = None
    ablutions: bool | None = None
    parking: bool | None = None
    raw: JsonDict = field(default_factory=dict, repr=False, compare=False)

    def __repr__(self) -> str:
        return f"Mosque(name={self.name!r}, slug={self.slug!r})"

    @property
    def coordinates(self) -> tuple[float, float] | None:
        if self.latitude is None or self.longitude is None:
            return None
        return self.latitude, self.longitude

    @property
    def iqama_offsets(self) -> dict[str, str]:
        """Map each obligatory prayer to its iqama offset (e.g. ``"+10"``)."""
        return dict(zip(IQAMA_NAMES, self.iqama, strict=False))

    @property
    def url(self) -> str | None:
        if not self.slug:
            return None
        return f"https://mawaqit.net/en/{self.slug}"

    @property
    def facilities(self) -> dict[str, bool]:
        """The facility flags that are explicitly set to True."""
        names = (
            "women_space",
            "janaza_prayer",
            "aid_prayer",
            "children_courses",
            "adult_courses",
            "ramadan_meal",
            "handicap_accessibility",
            "ablutions",
            "parking",
        )
        return {name: True for name in names if getattr(self, name) is True}


@dataclass(frozen=True, slots=True)
class Announcement(DictValue):
    """A notice posted by a mosque (also used for ``events``)."""

    id: int | None = None
    uuid: str | None = None
    title: str | None = None
    content: str | None = None
    image: str | None = None
    video: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    updated: str | None = None
    duration: int | None = None
    is_mobile: bool | None = None
    is_desktop: bool | None = None
    tv_orientation: str | None = None
    raw: JsonDict = field(default_factory=dict, repr=False, compare=False)

    def __repr__(self) -> str:
        return f"Announcement(title={self.title!r})"


@dataclass(frozen=True, slots=True)
class Calendar(DictValue):
    """A mosque's full-year timetable, scraped from its web page.

    ``months`` is indexed 0-11 (January-December). Each entry maps a
    day-of-month to that day's :class:`PrayerTimes`. ``iqama`` mirrors the same
    shape but holds iqama offset strings instead of clock times.
    """

    months: tuple[dict[int, PrayerTimes], ...] = ()
    iqama: tuple[dict[int, tuple[str, ...]], ...] = ()
    raw: JsonDict = field(default_factory=dict, repr=False, compare=False)

    def day(self, month: int, day: int) -> PrayerTimes | None:
        """Return the prayer times for a 1-based month and day-of-month."""
        if not 1 <= month <= len(self.months):
            return None
        return self.months[month - 1].get(day)

    def on(self, when: Any) -> PrayerTimes | None:
        """Return the prayer times for a ``date``/``datetime``-like object."""
        return self.day(when.month, when.day)

    def __iter__(self) -> Iterator[tuple[int, int, PrayerTimes]]:
        for month_index, days in enumerate(self.months, start=1):
            for day in sorted(days):
                yield month_index, day, days[day]


@dataclass(frozen=True, slots=True)
class ConfData(DictValue):
    """The full ``confData`` blob embedded in a mosque's web page."""

    uuid: str | None = None
    name: str | None = None
    slug: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None
    country_code: str | None = None
    times: PrayerTimes = field(default_factory=PrayerTimes)
    jumua: str | None = None
    calendar: Calendar = field(default_factory=Calendar)
    announcements: tuple[Announcement, ...] = ()
    events: tuple[Announcement, ...] = ()
    raw: JsonDict = field(default_factory=dict, repr=False, compare=False)

    def __repr__(self) -> str:
        return f"ConfData(name={self.name!r}, slug={self.slug!r})"
