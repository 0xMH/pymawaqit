"""Small value objects and shared type aliases for pymawaqit."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Literal


JsonDict = dict[str, Any]
RequestProfile = Literal["api", "web"]


class DictValue:
    """Small mixin for exporting nested dataclasses to plain dicts."""

    def to_dict(self, *, include_raw: bool = False) -> JsonDict:
        data = asdict(self)
        if not include_raw:
            self._drop_raw(data)
        return data

    @staticmethod
    def _drop_raw(value: Any) -> None:
        if isinstance(value, dict):
            value.pop("raw", None)
            for child in value.values():
                DictValue._drop_raw(child)
        elif isinstance(value, list | tuple):
            for child in value:
                DictValue._drop_raw(child)
