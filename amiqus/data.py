from __future__ import annotations

import json


def get_countries() -> list:
    with open("amiqus/data/supported_applicant_countries.json") as f:
        countries = json.load(f)
    return countries


def record_supported_country(alpha3: str) -> bool:
    with open("amiqus/data/supported_applicant_countries.json") as f:
        countries = json.load(f)

    if alpha3:
        pick_country = next(
            (country for country in countries if country["alpha3"] == alpha3), None
        )
        if pick_country:
            return pick_country["supported_identity_check"]

    return False
