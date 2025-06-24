import datetime
import pytest
from distro_support._distro import SupportRange
from distro_support.errors import NoDevelopmentInfoError, NoESMInfoError


EMPTY_DISTRO = SupportRange(
    distribution="empty",
    version="0",
    begin_support=None,
    end_support=None,
    begin_dev=datetime.date(1, 1, 1),
)
BASIC_DISTRO = SupportRange(
    distribution="basic",
    version="1",
    begin_support=datetime.date(2000, 1, 1),
    end_support=datetime.date(2000, 12, 31),
)
FULL_DISTRO = SupportRange(
    distribution="full",
    version="2",
    begin_support=datetime.date(2000, 1, 1),
    end_support=datetime.date(2000, 12, 31),
    begin_dev=datetime.date(1999, 1, 1),
    end_extended_support=datetime.date(2001, 12, 31),
)
SUPPORT_DATES = [
    (
        datetime.date(1958, 7, 2),
        False,
        False,
        False,
    ),
    (datetime.date(1999, 12, 31), False, False, True),
    (
        datetime.date(2000, 1, 1),
        True,
        False,
        False,
    ),
    (
        datetime.date(2000, 2, 21),
        True,
        False,
        False,
    ),
    (datetime.date(2000, 12, 31), True, False, False),
    (datetime.date(2001, 1, 1), False, True, False),
    (datetime.date(2038, 1, 19), False, False, False),
]


@pytest.mark.parametrize(("date", "supported", "esm", "in_dev"), SUPPORT_DATES)
def test_is_supported_on(date, supported, esm, in_dev):
    assert not EMPTY_DISTRO.is_supported_on(date)
    assert BASIC_DISTRO.is_supported_on(date) == supported
    if not supported:
        assert not BASIC_DISTRO.is_supported_on(date)

    assert FULL_DISTRO.is_supported_on(date) == supported
    assert FULL_DISTRO.is_supported_on(date, include_esm=True) == supported or esm


@pytest.mark.parametrize(("date", "supported", "esm", "in_dev"), SUPPORT_DATES)
def test_is_esm_on(date, supported, esm, in_dev):
    with pytest.raises(NoESMInfoError):
        BASIC_DISTRO.is_esm_on(date)
    assert FULL_DISTRO.is_esm_on(date) == esm


@pytest.mark.parametrize(("date", "supported", "esm", "in_dev"), SUPPORT_DATES)
def test_is_dev_on(date, supported, esm, in_dev):
    assert EMPTY_DISTRO.is_in_development_on(date)
    with pytest.raises(NoDevelopmentInfoError):
        BASIC_DISTRO.is_in_development_on(date)
    assert FULL_DISTRO.is_in_development_on(date) == in_dev
