from datetime import date

import pytest
import distro_support


@pytest.mark.parametrize(
    ("distribution", "version"),
    [
        ("ubuntu", "4.10"),
        ("ubuntu", "16.04"),
        ("ubuntu", "25.10"),
        ("debian", "1.1"),
    ],
)
def test_get_support_range(distribution: str, version: str):
    """Test that get_support_range returns a valid object."""
    distro = distro_support.get_support_range(distribution, version)

    distro.is_supported_on(date.today())
    distro.is_in_development_on(date.today())
    distro.is_esm_on(date.today())
