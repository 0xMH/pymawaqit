"""Public MAWAQIT client."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from mawaqit_py._transport import _MawaqitTransport
from mawaqit_py.constants import (
    API_SEARCH,
    DEFAULT_LANG,
    DEFAULT_MAX_RETRIES,
    WEB_MOSQUE,
)
from mawaqit_py.exceptions import ConfDataError, MawaqitRequestError, MosqueNotFound
from mawaqit_py.mosque import Announcement, Calendar, ConfData, Mosque
from mawaqit_py.parsing import parse_conf_data, parse_search_results


_MosqueInput = Mosque | str


@dataclass(slots=True)
class Mawaqit:
    """Client for the public MAWAQIT mosque API and confData web scrape.

    The search endpoint needs no authentication and embeds today's prayer
    times in every result. The per-mosque year calendar and announcements are
    not exposed by the public API, so they are read from the ``confData`` blob
    on each mosque's web page.
    """

    timeout: int = 15
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_backoff: float = 0.2

    _transport: _MawaqitTransport = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._transport = _MawaqitTransport(
            timeout=self.timeout,
            max_retries=self.max_retries,
            retry_backoff=self.retry_backoff,
        )

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> "Mawaqit":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def search(
        self,
        word: str | None = None,
        *,
        lat: float | None = None,
        lon: float | None = None,
        page: int = 1,
    ) -> list[Mosque]:
        """Search mosques by name/city, or by coordinate (nearest first).

        Pass ``word`` for a text search, or both ``lat`` and ``lon`` for a
        proximity search. Each result already carries today's prayer times.
        """
        params = self._search_params(word=word, lat=lat, lon=lon, page=page)
        return parse_search_results(self._get_json(API_SEARCH, params=params))

    def nearby(self, lat: float, lon: float, *, page: int = 1) -> list[Mosque]:
        """Return mosques nearest to a coordinate, sorted by proximity."""
        return self.search(lat=lat, lon=lon, page=page)

    def iter_search(
        self,
        word: str | None = None,
        *,
        lat: float | None = None,
        lon: float | None = None,
        start_page: int = 1,
        max_pages: int | None = None,
    ) -> Iterator[Mosque]:
        """Yield mosques across pages until a page comes back empty.

        ``max_pages`` caps the number of pages that contribute *new* mosques, not
        the number of requests issued; a page that adds only duplicates stops the
        iteration early (the server is clamping or looping ``page``).
        """
        if start_page < 1:
            raise ValueError("start_page must be >= 1")
        if max_pages is not None and max_pages < 0:
            raise ValueError("max_pages must be >= 0")

        page = start_page
        fetched = 0
        seen: set[str] = set()
        while max_pages is None or fetched < max_pages:
            mosques = self.search(word, lat=lat, lon=lon, page=page)
            if not mosques:
                break
            fresh = []
            for mosque in mosques:
                key = mosque.uuid or mosque.slug
                if key and key not in seen:
                    seen.add(key)
                    fresh.append(mosque)
            # A page that adds nothing new means the server is ignoring `page`
            # (clamping or looping); stop instead of yielding duplicates forever.
            if not fresh:
                break
            yield from fresh
            fetched += 1
            page += 1

    def conf_data(self, mosque: _MosqueInput, *, lang: str = DEFAULT_LANG) -> ConfData:
        """Fetch and parse the full confData blob for a mosque's web page."""
        slug = self._slug(mosque)
        html = self._get_text(WEB_MOSQUE.format(lang=lang, slug=slug))
        try:
            return parse_conf_data(html)
        except ValueError as exc:
            raise ConfDataError(
                f"Could not extract confData for mosque {slug!r}"
            ) from exc

    def calendar(self, mosque: _MosqueInput, *, lang: str = DEFAULT_LANG) -> Calendar:
        """Fetch a mosque's full-year prayer-time calendar."""
        return self.conf_data(mosque, lang=lang).calendar

    def announcements(
        self,
        mosque: _MosqueInput,
        *,
        lang: str = DEFAULT_LANG,
    ) -> list[Announcement]:
        """Fetch a mosque's current announcements."""
        return list(self.conf_data(mosque, lang=lang).announcements)

    def _get_json(self, url: str, *, params: dict[str, Any] | None = None) -> Any:
        response = self._transport.get(url, profile="api", params=params)
        if response.status_code == 200:
            return response.json()
        raise MawaqitRequestError(
            f"Request to {url} failed (status {response.status_code})"
        )

    def _get_text(self, url: str) -> str:
        response = self._transport.get(url, profile="web")
        if response.status_code == 200:
            return response.text
        if response.status_code == 404:
            raise MosqueNotFound(f"Mosque page not found: {url}")
        raise MawaqitRequestError(
            f"Request to {url} failed (status {response.status_code})"
        )

    @staticmethod
    def _search_params(
        *,
        word: str | None,
        lat: float | None,
        lon: float | None,
        page: int,
    ) -> dict[str, Any]:
        if page < 1:
            raise ValueError("page must be >= 1")
        has_coords = lat is not None and lon is not None
        if not word and not has_coords:
            raise ValueError("provide word, or both lat and lon")
        if (lat is None) != (lon is None):
            raise ValueError("lat and lon must be given together")

        params: dict[str, Any] = {"page": page}
        if word:
            params["word"] = word
        if has_coords:
            params["lat"] = lat
            params["lon"] = lon
        return params

    @staticmethod
    def _slug(mosque: _MosqueInput) -> str:
        if isinstance(mosque, Mosque):
            if not mosque.slug:
                raise ValueError("Mosque has no slug")
            return mosque.slug
        slug = str(mosque).strip()
        if not slug:
            raise ValueError("slug must not be empty")
        if "mawaqit.net" in slug:
            slug = slug.split("?", 1)[0].split("#", 1)[0].rstrip("/").rsplit("/", 1)[-1]
        return slug
