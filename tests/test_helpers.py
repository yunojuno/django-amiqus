from datetime import datetime
from unittest import mock

import pytest
from dateutil.parser import parse as date_parse

from amiqus.helpers import (
    create_client,
    update_client_status,
    update_record_expired_at_date,
)
from amiqus.models import Client


class TestCreateRecord:
    pass


@pytest.mark.django_db
class TestCreateClient:
    @mock.patch("amiqus.helpers.post")
    def test_create_client(self, mock_post, client_data, user):
        """Test the create_client function."""
        mock_post.return_value = client_data
        client = create_client(user)
        mock_post.assert_called_once_with(
            "clients",
            data={
                "name": {"first_name": user.first_name, "last_name": user.last_name},
                "email": user.email,
            },
        )
        assert client.amiqus_id == str(client_data["id"])
        assert client.user == user
        assert client.created_at == date_parse(client_data["created_at"])

    @mock.patch("amiqus.helpers.post")
    def test_create_client_with_custom_data(self, mock_post, client_data, user):
        """Test the create_client function with extra custom POST data."""
        mock_post.return_value = client_data
        create_client(user, country="GBR", dob="2016-01-01", gender="male")
        mock_post.assert_called_once_with(
            "clients",
            data={
                "name": {"first_name": user.first_name, "last_name": user.last_name},
                "email": user.email,
                "gender": "male",
                "dob": "2016-01-01",
                "country": "GBR",
            },
        )

    @mock.patch("amiqus.helpers.post")
    def test_create_client_with_name_override(self, mock_post, client_data, user):
        """Test the create_client function with a name override."""
        mock_post.return_value = client_data
        create_client(user, name={"first_name": "Foo", "last_name": "Bar"})
        mock_post.assert_called_once_with(
            "clients",
            data={
                "name": {"first_name": "Foo", "last_name": "Bar"},
                "email": user.email,
            },
        )


@pytest.mark.django_db
class TestUpdateClientStatus:
    @mock.patch("amiqus.helpers.patch")
    def test_update_client_status(self, mock_patch, client_data, client):
        """Test the update_client_status function."""
        mock_patch.return_value = client_data
        update_client_status(client, Client.ClientStatus.FOR_REVIEW)
        mock_patch.assert_called_once_with(
            f"clients/{client.amiqus_id}",
            data={"status": Client.ClientStatus.FOR_REVIEW.value},
        )
        assert client.amiqus_id == str(client_data["id"])
        assert client.created_at == date_parse(client_data["created_at"])


@pytest.mark.django_db
class TestUpdateRecordExpiredAtDate:
    @mock.patch("amiqus.helpers.patch")
    def test_update_record_expired_at_date(self, mock_patch, record_data, record):
        """Test the update_record_expired_at_date function."""
        mock_patch.return_value = record_data
        update_record_expired_at_date(record, datetime(2022, 6, 10))
        mock_patch.assert_called_once_with(
            f"records/{record.amiqus_id}",
            data={"expired_at": "2022-06-10T00:00:00Z"},
        )
