import pytest

from amiqus.data import get_country


def test_get_country():
    country = get_country("IND")
    assert country
    assert country.alpha3 == "IND"
    assert country.name == "India"
    assert country.supported_identity_report is True
    assert country.region == "Asia"
    assert country.subregion == "Southern Asia"


def test_get_country_does_not_exist():
    assert get_country("XXX") is None


@pytest.mark.parametrize("alpha3,supported", [("YEM", False), ("ZMB", True)])
def test_country_supports_identity_report(alpha3: str, supported: bool):
    country = get_country(alpha3)
    assert country
    assert country.supported_identity_report == supported
