# import copy

# import pytest
# from dateutil.parser import parse as date_parse

# from amiqus.models import Record

# from ..conftest import CLIENT_ID, TEST_CHECK


# @pytest.mark.django_db
# class TestRecordManager:
#     """amiqus.models.ClientManager tests."""

#     def test_create_record(self, user, client):
#         """Test the create method parses response."""
#         data = copy.deepcopy(TEST_CHECK)
#         record = Record.objects.create_record(client=client, raw=data)
#         assert record.user == user
#         assert record.client == client
#         assert record.amiqus_id == data["id"]
#         assert record.status == data["status"]
#         assert record.result == data["result"]
#         assert record.created_at == date_parse(data["created_at"])


# @pytest.mark.django_db
# class TestRecordModel:
#     """amiqus.models.Record tests."""

#     def test_defaults(self, user, client):
#         """Test default property values."""
#         record = Record(user=user, client=client, amiqus_id=CLIENT_ID, raw=TEST_CHECK)
#         assert record.amiqus_id == CLIENT_ID
#         assert record.raw == TEST_CHECK
#         assert record.created_at is None
#         assert record.status is None
#         assert record.result is None

#     def test_parse(self):
#         """Test the parse_raw method."""
#         data = copy.deepcopy(TEST_CHECK)
#         record = Record().parse(data)
#         assert record.amiqus_id == TEST_CHECK["id"]
#         assert record.created_at == date_parse(TEST_CHECK["created_at"])
#         assert record.status == "in_progress"
#         assert record.result is None
