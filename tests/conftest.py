"""Shared pytest fixtures and test data."""

from __future__ import annotations

import copy

import pytest
from django.contrib.auth import get_user_model

from amiqus.models import Client, Record

TEST_CLIENT_ID = 123456
TEST_RECORD_ID = 789012
TEST_CHECK_ID = 3456789
TEST_CHECK_ID_2 = 9876543
TEST_DOCUMENT_ID = 9876543

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
def client_status_event():
    return copy.deepcopy(TEST_EVENT_CLIENT_STATUS)


@pytest.fixture
def record_finished_event():
    return copy.deepcopy(TEST_EVENT_RECORD_FINISHED)


# https://developers.amiqus.co/aqid/api-reference.html#tag/Clients
TEST_CLIENT: dict = {
    "object": "client",
    "id": TEST_CLIENT_ID,
    "status": "pending",
    "name": {
        "object": "name",
        "title": "mr",
        "other_title": None,
        "first_name": "Fred",
        "middle_name": "",
        "last_name": "McFly",
        "name": "Martin McFly",
        "full_name": "Marty McFly",
        "complete_name": "Mr Martin McFly",
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
    "id": TEST_RECORD_ID,
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
            "check": TEST_CHECK_ID,
            "cost": 1,
            "completed_at": None,
        },
        {
            "object": "step",
            "id": 3,
            "type": "check.watchlist",
            "preferences": {
                "report_type": "standard",
                "face": True,
                "liveness": True,
                "facial_similarity": False,
                "live_document": False,
                "docs": ["passport", "driving_licence", "national_id"],
                "search_profile": "peps_sanctions_media_extended",
            },
            "check": TEST_CHECK_ID_2,
            "cost": 1,
            "completed_at": None,
        },
        {
            "object": "step",
            "id": 4,
            "type": "check.criminal_record",
            "preferences": {
                "report_type": "standard",
                "country": "gb",
                "check_type": "basic",
            },
            "check": TEST_CHECK_ID_2 + 1,
            "cost": 1,
            "completed_at": None,
        },
    ],
    "client": TEST_CLIENT_ID,
    "created_at": "2022-05-22T08:22:12Z",
    "updated_at": "2022-05-22T08:22:12Z",
    "archived_at": None,
    "expired_at": "2022-06-01T08:22:12Z",
}
# record returned by the v2 API
# WRONG - THIS IS THE V1 RESPONSE
TEST_RECORD_V2 = {
    "object": "record",
    "id": TEST_RECORD_ID,
    "status": "complete",
    "email": "herman.munster@addams.com",
    "client": TEST_CLIENT_ID,
    "checks": {
        "object": "list",
        "data": [
            {
                "object": "check",
                "id": TEST_CHECK_ID,
                "type": "document",
                "record": TEST_RECORD_ID,
                "status": "accepted",
                "allow_replay": False,
                "allow_cancel": False,
                "requires_consent": True,
                "created_at": "2023-04-06T15:09:25Z",
                "updated_at": "2023-04-06T15:17:38Z",
            }
        ],
        "total": 1,
        "count": 1,
        "limit": 15,
        "has_more": False,
    },
    "created_at": "2023-04-06T15:09:25Z",
    "updated_at": "2023-04-06T15:17:50Z",
    "archived_at": None,
    "expired_at": "2022-06-01T08:22:12Z",
}

TEST_CHECK_PHOTO_ID = {
    "allow_cancel": False,
    "allow_replay": False,
    "created_at": "2023-04-06T11:37:14Z",
    "id": 123456,
    "object": "check",
    "record": TEST_RECORD_ID,
    "requires_consent": True,
    "status": "pending",
    "type": "photo_id",
    "updated_at": "2023-04-06T11:37:14Z",
}

# Webhook event data (anonymised) taken from
# https://id.amiqus.co/team/workflow/webhooks


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
            "show": (
                f"https://id.amiqus.co/api/clients/{TEST_CLIENT_ID}"
                "/forms/d2edcfae-8778-4323-ac3e-b847b56728b7"
            ),
        },
        "client": {
            "id": 999999,
            "show": f"https://id.amiqus.co/api/clients/{TEST_CLIENT_ID}",
        },
        "record": {
            "id": TEST_RECORD_ID,
            "show": f"https://id.amiqus.co/api/records/{TEST_RECORD_ID}",
            "download": f"https://id.amiqus.co/api/records/{TEST_RECORD_ID}/download",
        },
    },
}

TEST_EVENT_CLIENT_RECORD = {
    "data": {
        "client": {
            "id": TEST_CLIENT_ID,
            "show": f"https://id.amiqus.co/api/clients/{TEST_CLIENT_ID}",
        },
        "record": {
            "id": TEST_RECORD_ID,
            "show": f"https://id.amiqus.co/api/records/{TEST_RECORD_ID}",
            "download": f"https://id.amiqus.co/api/records/{TEST_RECORD_ID}/download",
        },
    },
    "trigger": {"alias": "client.record", "triggered_at": "2023-04-06T11:37:16+00:00"},
    "webhook": {
        "created_at": "2023-03-31T23:49:44+00:00",
        "events": ["*"],
        "uuid": "2d37061a-65e8-4aac-844b-f51dd41d3e6c",
    },
}

TEST_EVENT_CLIENT_STATUS = {
    "data": {
        "client": {
            "id": TEST_CLIENT_ID,
            "show": f"https://id.amiqus.co/api/clients/{TEST_CLIENT_ID}",
        }
    },
    "trigger": {"alias": "client.status", "triggered_at": "2023-04-06T11:37:16+00:00"},
    "webhook": {
        "created_at": "2023-03-31T23:49:44+00:00",
        "events": ["*"],
        "uuid": "2d37061a-65e8-4aac-844b-f51dd41d3e6c",
    },
}

TEST_EVENT_RECORD_CREATED = {
    "data": {
        "client": {
            "id": TEST_CLIENT_ID,
            "show": f"https://id.amiqus.co/api/clients/{TEST_CLIENT_ID}",
        },
        "record": {
            "id": TEST_RECORD_ID,
            "show": f"https://id.amiqus.co/api/records/{TEST_RECORD_ID}",
            "download": f"https://id.amiqus.co/api/records/{TEST_RECORD_ID}/download",
        },
    },
    "trigger": {"alias": "record.created", "triggered_at": "2023-04-06T11:37:16+00:00"},
    "webhook": {
        "created_at": "2023-03-31T23:49:44+00:00",
        "events": ["*"],
        "uuid": "2d37061a-65e8-4aac-844b-f51dd41d3e6c",
    },
}

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
            "id": TEST_RECORD_ID,
            "show": f"https://id.amiqus.co/api/records/{TEST_RECORD_ID}",
            "download": f"https://id.amiqus.co/api/records/{TEST_RECORD_ID}/download",
        },
        "client": {
            "id": TEST_CLIENT_ID,
            "show": f"https://id.amiqus.co/api/clients/{TEST_CLIENT_ID}",
        },
    },
}

TEST_EVENT_RECORD_REVIEWED: dict = {
    "webhook": {
        "uuid": "93554561-d946-4c0d-8858-28f038801b47",
        "created_at": "2023-03-31T22:54:32+00:00",
        "events": ["*"],
    },
    "trigger": {
        "triggered_at": "2023-04-06T15:17:50+00:00",
        "alias": "record.reviewed",
    },
    "data": {
        "record": {
            "id": TEST_RECORD_ID,
            "show": f"https://id.amiqus.co/api/records/{TEST_RECORD_ID}",
            "download": f"https://id.amiqus.co/api/records/{TEST_RECORD_ID}/download",
        },
        "client": {
            "id": TEST_CLIENT_ID,
            "show": f"https://id.amiqus.co/api/clients/{TEST_CLIENT_ID}",
        },
    },
}


@pytest.fixture
def record_reviewed_event():
    """Return a record.reviewed event fixture."""
    return copy.deepcopy(TEST_EVENT_RECORD_REVIEWED)
