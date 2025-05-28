import copy

import pytest
from dateutil.parser import parse as date_parse
from django.contrib.auth import get_user_model

from amiqus.models import Client
from amiqus.settings import scrub_client_data

from ..conftest import TEST_CLIENT_ID, TEST_CLIENT

User = get_user_model()


@pytest.mark.django_db
class TestClientManager:
    def test_create_client(self, user):
        """Test the create method parses response."""
        data = copy.deepcopy(TEST_CLIENT)
        client = Client.objects.create_client(user=user, raw=data)
        assert client.user == user
        assert client.raw == scrub_client_data(data)
        assert int(client.amiqus_id) == data["id"]
        assert client.created_at == date_parse(data["created_at"])


@pytest.mark.django_db
class TestClientModel:
    def test_defaults(self, user):
        """Test default property values."""
        client = Client(user=user, amiqus_id=TEST_CLIENT_ID, raw=TEST_CLIENT)
        assert client.href == f"clients/{TEST_CLIENT_ID}"
        assert int(client.amiqus_id) == TEST_CLIENT_ID
        assert client.user == user
        assert client.created_at is None

    def test_save(self, user):
        """Test the save method."""
        client = Client(user=user, amiqus_id=TEST_CLIENT_ID, raw=TEST_CLIENT)
        client.save()
        assert client.href == f"clients/{TEST_CLIENT_ID}"
        assert int(client.amiqus_id) == TEST_CLIENT_ID
        assert client.user == user
        assert client.created_at is None
        # test the related_name
        assert user.amiqus_clients.last() == client

    def test_parse(self, client):
        """Test default scrubbing of data."""
        data = copy.deepcopy(TEST_CLIENT)
        client.parse(data)
        assert client.raw == {
            "id": TEST_CLIENT["id"],
            "created_at": TEST_CLIENT["created_at"],
            "status": TEST_CLIENT["status"],
        }
