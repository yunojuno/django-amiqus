import pytest

from amiqus.data import get_country


def test_get_country():
    country = get_country("IND")
    assert country.alpha3 == "IND"
    assert country.name == "India"
    assert country.supported_identity_report is True
    assert country.region == "Asia"
    assert country.subregion == "Southern Asia"


def test_get_country_does_not_exist():
    country = get_country("XXX")
    assert country is None


@pytest.mark.parametrize(
    "country,supported",
    [
        ("YEM", False),
        ("ZMB", True),
        ("IND", True),
        ("ERI", False),
    ],
)
def test_country_supports_identity_report(country: str, supported: bool):
    assert get_country(country).supported_identity_report == supported
