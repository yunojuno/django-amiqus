# from copy import deepcopy
from unittest import mock

import pytest
from dateutil.parser import parse as date_parse

from amiqus.helpers import (  # import from helpers to deter possible dependency issues; Check,; Client,; Record,; create_record,
    create_client,
)

# from .conftest import TEST_CLIENT, TEST_RECORD


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

    # @mock.patch("amiqus.helpers.post")
    # @mock.patch("amiqus.helpers.get")
    # def test_create_record(self, client_data, record_data, mock_get, mock_post, user):
    #     """Test the create_record function."""
    #     mock_post.return_value = record_data
    #     mock_get.return_value = dict(
    #         checks=[TEST_REPORT_DOCUMENT, TEST_REPORT_IDENTITY_ENHANCED]
    #     )
    #     client = Client.objects.create_client(user, client_data)

    #     # 1. use the defaults.
    #     record = create_record(
    #         client,
    #         check_names=[
    #             TEST_REPORT_DOCUMENT["name"],
    #             TEST_REPORT_IDENTITY_ENHANCED["name"],
    #         ],
    #     )
    #     mock_post.assert_called_once_with(
    #         "records",
    #         {
    #             "client_id": client.amiqus_id,
    #             "check_names": [
    #                 Check.CheckType.DOCUMENT.value,
    #                 Check.CheckType.IDENTITY_ENHANCED.value,
    #             ],
    #         },
    #     )
    #     assert Record.objects.get() == record
    #     # record we have two checks, and that the raw field matches the JSON
    #     # and that the parse method has run
    #     assert Check.objects.count() == 2
    #     # confirm that kwargs are merged in correctly
    #     record.delete()
    #     mock_post.reset_mock()
    #     record = create_record(
    #         client, check_names=[Check.CheckType.IDENTITY_ENHANCED], foo="bar"
    #     )
    #     mock_post.assert_called_once_with(
    #         "records",
    #         {
    #             "client_id": client.amiqus_id,
    #             "check_names": [Check.CheckType.IDENTITY_ENHANCED.value],
    #             "foo": "bar",
    #         },
    #     )
