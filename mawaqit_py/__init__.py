"""
MAWAQIT - Python API for mawaqit.net mosque prayer times.

Example usage:
    >>> from mawaqit_py import Mawaqit
    >>> with Mawaqit() as client:
    ...     mosques = client.search("amsterdam")
    ...     mosque = mosques[0]
    ...     print(mosque.name, mosque.times.prayers)

    >>> # Nearest mosques to a coordinate
    >>> client.nearby(48.8566, 2.3522)

    >>> # Full-year calendar for a specific mosque
    >>> calendar = client.calendar("grande-mosquee-de-paris")
    >>> calendar.day(7, 1)  # July 1st
"""

from importlib.metadata import PackageNotFoundError, version

from mawaqit_py.exceptions import (
    ConfDataError,
    MawaqitError,
    MawaqitRequestError,
    MosqueNotFound,
)
from mawaqit_py.mawaqit import Mawaqit
from mawaqit_py.mosque import (
    Announcement,
    Calendar,
    ConfData,
    Mosque,
    PrayerTimes,
)

try:
    __version__ = version("mawaqit-py")
except PackageNotFoundError:  # running from a source checkout without install
    __version__ = "0.0.0+unknown"
__all__ = [
    "Announcement",
    "Calendar",
    "ConfData",
    "ConfDataError",
    "Mawaqit",
    "MawaqitError",
    "MawaqitRequestError",
    "Mosque",
    "MosqueNotFound",
    "PrayerTimes",
    "__version__",
]
