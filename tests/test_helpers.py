from unittest import mock

import pytest
from dateutil.parser import parse as date_parse

from amiqus.helpers import create_client


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
