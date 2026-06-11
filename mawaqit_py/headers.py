"""Request headers for MAWAQIT calls."""

from mawaqit_py.models import RequestProfile


def make_headers(profile: RequestProfile = "api") -> dict[str, str]:
    """Generate the headers required by an internal request profile.

    curl_cffi sets a matching User-Agent from the impersonation target, so we
    only add the content-negotiation headers each endpoint expects.
    """
    if profile == "api":
        return {
            "Accept": "application/json",
            "Referer": "https://mawaqit.net/",
        }
    if profile == "web":
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en;q=0.9",
        }
    raise ValueError(f"unknown request profile: {profile!r}")
