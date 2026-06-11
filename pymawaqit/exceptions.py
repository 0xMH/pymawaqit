"""Exception types raised by pymawaqit."""


class MawaqitError(Exception):
    """Base exception for pymawaqit errors."""


class MawaqitRequestError(MawaqitError, RuntimeError):
    """Raised when MAWAQIT rejects or fails an HTTP request."""


class MosqueNotFound(MawaqitError, LookupError):
    """Raised when a mosque page or slug cannot be found."""


class ConfDataError(MawaqitError, LookupError):
    """Raised when the confData blob cannot be extracted from a mosque page."""
