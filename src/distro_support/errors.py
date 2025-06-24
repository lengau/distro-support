from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from distro_support._distro import SupportRange


class DistroSupportError(Exception):
    """Base error for the distro-support package."""


class NoDevelopmentInfoError(DistroSupportError):
    """User made an action that required development information we don't have."""

    def __init__(self, distro: SupportRange) -> None:
        super().__init__(
            f"No development information for {distro.distribution} {distro.version}"
        )
        self.distro = distro


class NoESMInfoError(DistroSupportError):
    """User made an action that required development information we don't have."""

    def __init__(self, distro: SupportRange) -> None:
        super().__init__(
            f"No extended support information for {distro.distribution} {distro.version}"
        )
        self.distro = distro


class UnknownDistributionError(DistroSupportError):
    def __init__(self, distro: str) -> None:
        super().__init__(f"Unknown distribution '{distro}'")


class UnknownVersionError(DistroSupportError):
    def __init__(self, distro: str, series: str) -> None:
        super().__init__(f"Unknown version {distro} {series}")
