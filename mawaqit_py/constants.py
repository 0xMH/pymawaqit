"""Constants used by the MAWAQIT client."""


API_BASE = "https://mawaqit.net/api/2.0"
API_SEARCH = f"{API_BASE}/mosque/search"

WEB_BASE = "https://mawaqit.net"
WEB_MOSQUE = f"{WEB_BASE}/{{lang}}/{{slug}}"

DEFAULT_LANG = "en"

# times[] carries six clock values per day. Index 1 is sunrise/shuruq, not a
# prayer; the five obligatory prayers are indices 0, 2, 3, 4, 5.
TIME_NAMES = ("fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha")
PRAYER_NAMES = ("fajr", "dhuhr", "asr", "maghrib", "isha")

# iqama[] holds one offset per obligatory prayer, in PRAYER_NAMES order.
IQAMA_NAMES = PRAYER_NAMES

RETRY_STATUS_CODES = {403, 429, 500, 502, 503, 504}
DEFAULT_MAX_RETRIES = 3

# curl_cffi impersonation targets, tried in order on transport errors. The web
# mosque page sits behind a CDN that rejects non-browser clients, so even the
# plain JSON API is fetched with a browser fingerprint.
IMPERSONATE_POOL = ("chrome124", "safari17_0", "chrome120")
