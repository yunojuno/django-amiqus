from copy import deepcopy
from unittest import mock

import pytest
from dateutil.parser import parse as date_parse

from amiqus.helpers import (  # import from helpers to deter possible dependency issues
    Check,
    Client,
    Record,
    create_client,
    create_record,
)

from .conftest import (
    TEST_CHECK,
    TEST_CLIENT,
    TEST_REPORT_DOCUMENT,
    TEST_REPORT_IDENTITY_ENHANCED,
)

# from tests.test_app.models import User
# from amiqus.helpers import create_client, create_record
# reference = "usr_1231asdas212asasda"
# checks = {
#     "document": {
#         "enabled": True,
#         "preferences": {
#             "face": True
#         }
#     },
#     "right_to_work": {
#         "enabled": True,
#         "preferences": {}
#     },
# }
# u = User.objects.create(
#     first_name="Jimmy",
#     last_name="Cricket",
#     username="jimmy.cricket",
#     email="jimmy.cricket@example.com",
# )
# client = create_client(u, reference=reference)
# check = create_record(
#     client,
#     check_names=checks,
#     notification="link",
# )


@pytest.mark.django_db
class TestHelperFunctions:
    @mock.patch("amiqus.helpers.post")
    def test_create_client(self, mock_post, user):
        """Test the create_client function."""
        data = deepcopy(TEST_CLIENT)
        mock_post.return_value = data
        client = create_client(user)
        mock_post.assert_called_once_with(
            "clients",
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            },
        )
        assert client.amiqus_id == data["id"]
        assert client.user == user
        assert client.created_at == date_parse(data["created_at"])

    @mock.patch("amiqus.helpers.post")
    def test_create_client_with_custom_data(self, mock_post, user):
        """Test the create_client function with extra custom POST data."""
        data = deepcopy(TEST_CLIENT)
        mock_post.return_value = data
        create_client(user, country="GBR", dob="2016-01-01", gender="male")
        mock_post.assert_called_once_with(
            "clients",
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "gender": "male",
                "dob": "2016-01-01",
                "country": "GBR",
            },
        )

    @mock.patch("amiqus.helpers.post")
    @mock.patch("amiqus.helpers.get")
    def test_create_record(self, mock_get, mock_post, user):
        """Test the create_record function."""
        client_data = deepcopy(TEST_CLIENT)
        mock_post.return_value = TEST_CHECK
        mock_get.return_value = dict(
            checks=[TEST_REPORT_DOCUMENT, TEST_REPORT_IDENTITY_ENHANCED]
        )
        client = Client.objects.create_client(user, client_data)

        # 1. use the defaults.
        record = create_record(
            client,
            check_names=[
                TEST_REPORT_DOCUMENT["name"],
                TEST_REPORT_IDENTITY_ENHANCED["name"],
            ],
        )
        mock_post.assert_called_once_with(
            "records",
            {
                "client_id": client.amiqus_id,
                "check_names": [
                    Check.CheckType.DOCUMENT.value,
                    Check.CheckType.IDENTITY_ENHANCED.value,
                ],
            },
        )
        assert Record.objects.get() == record
        # record we have two checks, and that the raw field matches the JSON
        # and that the parse method has run
        assert Check.objects.count() == 2
        # confirm that kwargs are merged in correctly
        record.delete()
        mock_post.reset_mock()
        record = create_record(
            client, check_names=[Check.CheckType.IDENTITY_ENHANCED], foo="bar"
        )
        mock_post.assert_called_once_with(
            "records",
            {
                "client_id": client.amiqus_id,
                "check_names": [Check.CheckType.IDENTITY_ENHANCED.value],
                "foo": "bar",
            },
        )
