"""Shared pytest fixtures and test data."""
import copy
import uuid

import pytest
from django.contrib.auth import get_user_model

from amiqus.models import Check, Client, Event, Record

CLIENT_ID = str(uuid.uuid4())
CHECK_ID = str(uuid.uuid4())
IDENTITY_REPORT_ID = str(uuid.uuid4())
DOCUMENT_REPORT_ID = str(uuid.uuid4())
DOCUMENT_ID = str(uuid.uuid4())

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        "fred", first_name="Fred", last_name="Flinstone", email="fred@example.com"
    )


@pytest.fixture
def client(user):
    data = copy.deepcopy(TEST_CLIENT)
    return Client.objects.create_client(user=user, raw=data)


@pytest.fixture
def record(client):
    data = copy.deepcopy(TEST_CHECK)
    return Record.objects.create_record(client, raw=data)


@pytest.fixture
def identity_check(record):
    data = copy.deepcopy(TEST_REPORT_IDENTITY_ENHANCED)
    return Check.objects.create_check(record, raw=data)


# @pytest.fixture
# def document_check(record):
#     data = copy.deepcopy(TEST_REPORT_DOCUMENT)
#     return Check.objects.create_check(record, raw=data)


@pytest.fixture
def check(identity_check):
    return identity_check


@pytest.fixture
def event(record):
    data = copy.deepcopy(TEST_EVENT)
    return Event().parse(data)


# Test data taken from Onfido v3 API docs.

# https://documentation.onfido.com/#client-object
TEST_CLIENT = {
    "id": CLIENT_ID,
    "created_at": "2019-10-09T16:52:42Z",
    "sandbox": True,
    "first_name": "Jane",
    "last_name": "Doe",
    "email": None,
    "dob": "1990-01-01",
    "delete_at": None,
    "href": f"/v2/clients/{CLIENT_ID}",
    "id_numbers": [],
    "address": {
        "flat_number": None,
        "building_number": None,
        "building_name": None,
        "street": "Second Street",
        "sub_street": None,
        "town": "London",
        "state": None,
        "postcode": "S2 2DF",
        "country": "GBR",
        "line1": None,
        "line2": None,
        "line3": None,
    },
}

# https://documentation.onfido.com/#record-object

TEST_CHECK = {
    "object": "record",
    "id": 705972,
    "status": "reviewed",
    "email": "marty.mcfly@example.com",
    "client": 571374,
    "checks": {
        "object": "list",
        "data": [
            {
                "object": "check",
                "id": 1539425,
                "type": "document",
                "record": 705972,
                "status": "refer",
                "allow_replay": False,
                "allow_cancel": False,
                "requires_consent": True,
                "created_at": "2023-03-29T19:39:58Z",
                "updated_at": "2023-03-29T22:50:58Z",
            }
        ],
        "total": 1,
        "count": 1,
        "limit": 15,
        "has_more": False,
    },
    "created_at": "2023-03-29T19:39:57Z",
    "updated_at": "2023-03-30T11:46:13Z",
    "archived_at": None,
}

# https://documentation.onfido.com/#identity-enhanced-check
TEST_REPORT_IDENTITY_ENHANCED = {
    "created_at": "2019-10-03T15:54:20Z",
    "href": f"/v3/checks/{IDENTITY_REPORT_ID}",
    "id": IDENTITY_REPORT_ID,
    "name": "identity_enhanced",
    "properties": {
        "matched_address": 19099121,
        "matched_addresses": [
            {"id": 19099121, "match_types": ["credit_agencies", "voting_register"]}
        ],
    },
    "result": "clear",
    "status": "complete",
    "sub_result": None,
    "breakdown": {
        "sources": {
            "result": "clear",
            "breakdown": {
                "total_sources": {
                    "result": "clear",
                    "properties": {"total_number_of_sources": "3"},
                }
            },
        },
        "address": {
            "result": "clear",
            "breakdown": {
                "credit_agencies": {
                    "result": "clear",
                    "properties": {"number_of_matches": "1"},
                },
                "telephone_database": {"result": "clear", "properties": {}},
                "voting_register": {"result": "clear", "properties": {}},
            },
        },
        "date_of_birth": {
            "result": "clear",
            "breakdown": {
                "credit_agencies": {"result": "clear", "properties": {}},
                "voting_register": {"result": "clear", "properties": {}},
            },
        },
        "mortality": {"result": "clear"},
    },
    "record_id": CHECK_ID,
    "documents": [],
}


TEST_EVENT = {
    "payload": {
        "resource_type": "record",
        "action": "record.form_opened",
        "object": {
            "id": CHECK_ID,
            "status": "complete",
            "completed_at_iso8601": "2019-10-28T15:00:39Z",
            "href": f"https://api.onfido.com/v3/checks/{CHECK_ID}",
        },
    }
}
