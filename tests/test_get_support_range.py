from datetime import date

import pytest
import distro_support
from distro_support.errors import NoESMInfoError


@pytest.mark.parametrize(
    ("distribution", "version", "today", "supported", "in_dev", "esm"),
    [
        ("ubuntu", "4.10", date(2004, 10, 1), False, True, None),
        ("ubuntu", "4.10", date(2004, 11, 1), True, False, None),
        ("ubuntu", "4.10", date(2020, 1, 1), False, False, None),
        ("ubuntu", "16.04", date(2020, 1, 1), True, False, False),
        ("ubuntu", "16.04", date(2025, 1, 1), False, False, True),
        ("ubuntu", "25.10", date(2025, 8, 12), False, True, None),
        ("debian", "1.1", date(2000, 1, 1), False, False, None),
        ("debian", "", date(3000, 1, 1), False, True, None),
    ],
)
def test_get_support_range(
    distribution: str,
    version: str,
    today: date,
    supported: bool,
    in_dev: bool,
    esm: bool | None,
):
    """Test that get_support_range returns a valid object."""
    distro = distro_support.get_support_range(distribution, version)

    assert distro.is_supported_on(today) == supported
    assert distro.is_in_development_on(today) == in_dev
    if esm is None:
        with pytest.raises(NoESMInfoError):
            distro.is_esm_on(today)
    else:
        assert distro.is_esm_on(today) == esm
