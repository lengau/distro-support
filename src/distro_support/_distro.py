import dataclasses
import datetime
from typing import Self

from distro_support.errors import NoDevelopmentInfoError, NoESMInfoError


@dataclasses.dataclass(kw_only=True, slots=True)
class SupportRange:
    """A date range representing the support of a Linux distribution."""

    distribution: str
    version: str
    begin_support: datetime.date
    end_support: datetime.date
    begin_dev: datetime.date | None = None
    end_extended_support: datetime.date | None = None

    def is_supported_on(
        self, date: datetime.date, *, include_esm: bool = False
    ) -> bool:
        """Determine whether this item is supported on the given date.

        :param date: The date on which to check support.
        :param include_esm: Whether to include ESM support (default: False)
        :returns: Whether the product is supported on this date.
        """
        if self.begin_support <= date <= self.end_support:
            return True
        if not include_esm or self.end_extended_support is None:
            return False
        if self.begin_support <= date <= self.end_extended_support:
            return True
        return False

    def is_in_development_on(self, date: datetime.date) -> bool:
        """Determine whether this item is still in development on the given date."""
        if self.begin_dev is None:
            raise NoDevelopmentInfoError(self)
        return self.begin_dev <= date < self.begin_support

    def is_esm_on(self, date: datetime.date) -> bool:
        if self.end_extended_support is None:
            raise NoESMInfoError(self)
        return self.end_support < date <= self.end_extended_support

    @classmethod
    def from_json(cls, data: dict[str, str]) -> Self:
        return cls(
            distribution=data["distribution"],
            version=data["version"],
            begin_support=datetime.date.fromisoformat(data["begin_support"]),
            end_support=datetime.date.fromisoformat(data["end_support"]),
            begin_dev=None
            if "begin_dev" not in data
            else datetime.date.fromisoformat(data["begin_dev"]),
            end_extended_support=None
            if "end_extended_support" not in data
            else datetime.date.fromisoformat(data["begin_dev"]),
        )
