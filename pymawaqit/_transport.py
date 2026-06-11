"""HTTP transport and impersonation rotation for MAWAQIT."""

import time
from dataclasses import dataclass, field
from typing import Any

from curl_cffi import requests

from pymawaqit.constants import (
    DEFAULT_MAX_RETRIES,
    IMPERSONATE_POOL,
    RETRY_STATUS_CODES,
)
from pymawaqit.exceptions import MawaqitRequestError
from pymawaqit.headers import make_headers
from pymawaqit.models import RequestProfile


@dataclass(slots=True)
class _MawaqitTransport:
    """Thin curl_cffi wrapper with retry and browser-fingerprint rotation.

    MAWAQIT's public API needs no auth, but its CDN drops requests that do not
    look like a browser. We impersonate one, and on transport errors or
    rate-limit/5xx responses we rotate to the next fingerprint and back off.

    Not thread-safe: the session and fingerprint index are mutated in place, so
    a single instance (and the ``Mawaqit`` client wrapping it) must not be
    shared across threads.
    """

    timeout: int = 15
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_backoff: float = 0.2
    retry_statuses: set[int] | None = None

    _session: requests.Session | None = field(default=None, init=False, repr=False)
    _impersonate_index: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.retry_backoff < 0:
            raise ValueError("retry_backoff must be >= 0")
        if self.retry_statuses is None:
            self.retry_statuses = set(RETRY_STATUS_CODES)
        else:
            self.retry_statuses = set(self.retry_statuses)

    def close(self) -> None:
        if self._session is not None:
            self._session.close()
            self._session = None

    def __enter__(self) -> "_MawaqitTransport":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def _ensure_session(self) -> requests.Session:
        if self._session is None:
            target = IMPERSONATE_POOL[self._impersonate_index % len(IMPERSONATE_POOL)]
            self._session = requests.Session(impersonate=target)
        return self._session

    def _rotate(self) -> None:
        self._impersonate_index = (self._impersonate_index + 1) % len(IMPERSONATE_POOL)
        self.close()

    def _sleep_backoff(self, attempt: int) -> None:
        if self.retry_backoff > 0:
            time.sleep(self.retry_backoff * (attempt + 1))

    def get(
        self,
        url: str,
        *,
        profile: RequestProfile = "api",
        params: dict[str, Any] | None = None,
    ) -> requests.Response:
        for attempt in range(self.max_retries + 1):
            session = self._ensure_session()
            try:
                response = session.get(
                    url,
                    params=params,
                    headers=make_headers(profile),
                    timeout=self.timeout,
                )
            except requests.errors.RequestsError as exc:
                if attempt >= self.max_retries:
                    raise MawaqitRequestError(
                        f"GET {url} failed after {attempt + 1} attempts: {exc}"
                    ) from exc
                self._rotate()
                self._sleep_backoff(attempt)
                continue

            if response.status_code not in self.retry_statuses:
                return response
            if attempt >= self.max_retries:
                raise MawaqitRequestError(
                    f"MAWAQIT rejected GET {url} after {attempt + 1} attempts "
                    f"(status {response.status_code})"
                )
            self._rotate()
            self._sleep_backoff(attempt)

        raise AssertionError("unreachable: retry loop must return or raise")
