"""Shared parser helpers for MAWAQIT response payloads."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def as_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def parse_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    cleaned = str(value).strip()
    try:
        return int(cleaned)
    except ValueError:
        # Tolerate float-like strings ("12.0") the same way we coerce floats.
        try:
            return int(float(cleaned))
        except ValueError:
            return None


def parse_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def str_tuple(value: Any) -> tuple[str, ...]:
    """Coerce a list/tuple payload into a tuple of strings, else empty.

    ``null`` entries are dropped rather than stringified to ``"None"``.
    """
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value if item is not None)


def parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    normalized = str(value).strip().casefold()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    return None


def extract_conf_data(html: str) -> dict[str, Any]:
    """Pull the ``confData`` JSON object out of a mosque web page.

    The page assigns ``var confData = { ... };`` inline. The blob contains
    string literals that may hold ``}`` characters, so we scan for the matching
    closing brace instead of using a non-greedy regex. The scan tracks both
    quote styles when balancing braces, but the blob itself must be valid JSON
    (double-quoted): a single-quoted JS object balances correctly yet fails the
    ``json.loads`` in :func:`_scan_object` and is treated as not found.

    Pages often mention ``confData`` before the real assignment (analytics
    shims, ``window.confData = window.confData || {}`` guards). Such placeholders
    parse to an empty object, so we keep scanning until we find a non-empty one
    rather than latching onto the first ``{}`` we can parse.
    """
    marker = "confData"
    start = html.find(marker)
    while start != -1:
        brace = html.find("{", start)
        equals = html.find("=", start)
        # Guard against matching the word inside another token; the assignment
        # must reach an "=" before the opening brace.
        if brace != -1 and equals != -1 and equals < brace:
            obj = _scan_object(html, brace)
            if obj:
                return obj
        start = html.find(marker, start + len(marker))
    raise ValueError("confData blob not found in page")


def _scan_object(text: str, open_index: int) -> dict[str, Any] | None:
    depth = 0
    in_string = False
    escape = False
    quote = ""
    for index in range(open_index, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                in_string = False
            continue
        if char in ('"', "'"):
            in_string = True
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                blob = text[open_index : index + 1]
                try:
                    return json.loads(blob)
                except json.JSONDecodeError:
                    return None
    return None
