# """Full integration test - do not run in CI."""
# from copy import deepcopy
# from unittest import mock

# import pytest
# from django.contrib.auth import get_user_model
# from django.test import Client
# from django.urls import reverse

# from amiqus.helpers import create_client, create_record
# from amiqus.models import Check, Event
# from amiqus.models.base import BaseStatusModel

# from .conftest import TEST_CHECK, TEST_CLIENT, TEST_EVENT, TEST_REPORT_IDENTITY_ENHANCED

# User = get_user_model()


# @mock.patch("amiqus.helpers.post")
# @mock.patch("amiqus.helpers.get")
# @mock.patch("amiqus.models.base.get")
# @pytest.mark.django_db
# def test_end_to_end(mock_fetch, mock_get, mock_post, user, check_data, client_data, client: Client):
#     # Create a new client from the default user -
#     # the API POST returns the TEST_CLIENT JSON
#     mock_post.return_value = client_data
#     client = create_client(user)

#     # Create a new record for the client just created
#     # the API POST returns the new record (TEST_CHECK)
#     # the API GET retrievs the checks for the record (TEST_REPORT_IDENTITY_ENHANCED)
#     mock_post.return_value = check_data
#     mock_get.return_value = dict(checks=[TEST_REPORT_IDENTITY_ENHANCED])
#     record = create_record(client, check_names=[Check.CheckType.IDENTITY_ENHANCED])
#     assert not record.is_clear
#     assert record.status == "in_progress"

#     # this simulates a record.fetch() using the default JSON updated
#     # with the contents from the event - we are forcing the result here
#     # so that the record comes back from the fetch() as "complete" and "clear"
#     record.refresh_from_db()
#     mock_fetch.return_value = record.raw
#     mock_fetch.return_value["status"] = BaseStatusModel.Status.COMPLETE
#     mock_fetch.return_value["result"] = BaseStatusModel.Result.CLEAR

#     # Call the status_update webhook with the TEST_EVENT payload
#     url = reverse("amiqus:status_update")
#     with mock.patch("amiqus.decorators.TEST_MODE", True):
#         client.post(url, data=TEST_EVENT, content_type="application/json")
#     assert mock_fetch.call_count == 1
#     assert Event.objects.count() == 1
#     record.refresh_from_db()
#     assert record.is_clear
#     assert record.status == BaseStatusModel.Status.COMPLETE
