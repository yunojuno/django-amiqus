from amiqus.data import get_countries, record_supported_country


def test_record_supported_country_matches_json():
    test_params = (
        (
            "YEM",
            False,
        ),
        (
            "ZMB",
            True,
        ),
        (
            "IND",
            True,
        ),
        (
            "ERI",
            False,
        ),
    )

    data = get_countries()
    assert len(data) == 249

    for test in test_params:
        assert record_supported_country(test[0]) == test[1]
