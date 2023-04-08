"""Shared pytest fixtures and test data."""
from __future__ import annotations

import copy

import pytest
from django.contrib.auth import get_user_model

from amiqus.models import Client, Record

# import uuid


# CLIENT_ID = str(uuid.uuid4())
# CHECK_ID = str(uuid.uuid4())
# IDENTITY_REPORT_ID = str(uuid.uuid4())
# DOCUMENT_REPORT_ID = str(uuid.uuid4())
# DOCUMENT_ID = str(uuid.uuid4())

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        "fred", first_name="Fred", last_name="Flinstone", email="fred@example.com"
    )


@pytest.fixture
def client_data():
    return copy.deepcopy(TEST_CLIENT)


@pytest.fixture
def client(user, client_data):
    return Client.objects.create_client(user=user, raw=client_data)


@pytest.fixture
def record_data():
    return copy.deepcopy(TEST_RECORD)


@pytest.fixture
def record(client, record_data):
    return Record.objects.create_record(client, raw=record_data)


@pytest.fixture
def event_data():
    return copy.deepcopy(TEST_EVENT_FORM_SUBMITTED)


# https://amiqus.github.io/developers/api#tag/Clients
TEST_CLIENT: dict = {
    "object": "client",
    "id": 73845,
    "status": None,
    "name": {
        "object": "name",
        "title": "mr",
        "other_title": None,
        "first_name": "Martin",
        "middle_name": "Seamus",
        "last_name": "McFly",
        "name": "Martin McFly",
        "full_name": "Martin Seamus McFly",
        "complete_name": "Mr Martin Seamus McFly",
    },
    "email": "marty@example.com",
    "landline": None,
    "mobile": None,
    "dob": None,
    "reference": None,
    "is_deletable": True,
    "created_at": "2022-05-21T14:15:22Z",
    "updated_at": "2022-05-21T14:15:22Z",
    "archived_at": None,
}

# https://amiqus.github.io/developers/api#tag/Records
TEST_RECORD = {
    "object": "record",
    "id": 983434,
    "status": "pending",
    "email": "marty@example.com",
    "steps": [
        {
            "object": "step",
            "id": 2,
            "type": "check.photo_id",
            "preferences": {
                "report_type": "standard",
                "face": True,
                "liveness": True,
                "facial_similarity": False,
                "live_document": False,
                "docs": ["passport", "driving_licence", "national_id"],
            },
            "check": 82342,
            "cost": 1,
            "completed_at": None,
        },
        {
            "object": "step",
            "id": 3,
            "type": "document.request",
            "preferences": {
                "title": "Utility bill",
                "instructions": "A utility bill dated within the last three months.",
            },
            "document": 23123,
            "cost": 0,
            "completed_at": None,
        },
    ],
    "client": 73845,
    "created_at": "2022-05-22T08:22:12Z",
    "updated_at": "2022-05-22T08:22:12Z",
    "archived_at": None,
}


# Webhook event data (anonymised) taken from
# https://id.amiqus.co/team/workflow/webhooks
TEST_EVENT_RECORD_FINISHED: dict = {
    "webhook": {
        "uuid": "93554561-d946-4c0d-8858-28f038801b47",
        "created_at": "2023-03-31T22:54:32+00:00",
        "events": ["*"],
    },
    "trigger": {
        "triggered_at": "2023-04-06T15:17:50+00:00",
        "alias": "record.finished",
    },
    "data": {
        "record": {
            "id": 999999,
            "show": "https://id.amiqus.co/api/records/999999",
            "download": "https://id.amiqus.co/api/records/999999/download",
        },
        "client": {"id": 999999, "show": "https://id.amiqus.co/api/clients/999999"},
    },
}


TEST_EVENT_FORM_SUBMITTED: dict = {
    "webhook": {
        "uuid": "2d37061a-65e8-4aac-844b-f51dd41d3e6c",
        "created_at": "2023-03-31T23:49:44+00:00",
        "events": ["*"],
    },
    "trigger": {"triggered_at": "2023-04-06T15:17:50+00:00", "alias": "form.submitted"},
    "data": {
        "form": {
            "reference": "d2edcfae-8778-4323-ac3e-b847b56728b7",
            "show": "https://id.amiqus.co/api/clients/999999/forms/d2edcfae-8778-4323-ac3e-b847b56728b7",
        },
        "client": {"id": 999999, "show": "https://id.amiqus.co/api/clients/999999"},
        "record": {
            "id": 999999,
            "show": "https://id.amiqus.co/api/records/999999",
            "download": "https://id.amiqus.co/api/records/999999/download",
        },
    },
}
