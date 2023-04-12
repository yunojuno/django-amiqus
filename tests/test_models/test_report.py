# import copy
# from unittest import mock

# import pytest
# from dateutil.parser import parse as date_parse

# from amiqus.models import Check
# from amiqus.models.base import BaseModel

# from ..conftest import IDENTITY_REPORT_ID, TEST_REPORT_IDENTITY_ENHANCED


# @pytest.mark.django_db
# class TestCheckManager:
#     @mock.patch.object(BaseModel, "full_clean")
#     def test_create_check(self, mock_clean, user, record):
#         """Test the create method parses response."""
#         data = copy.deepcopy(TEST_REPORT_IDENTITY_ENHANCED)
#         check = Check.objects.create_check(record=record, raw=data)
#         assert check.user == user
#         assert check.amiqus_record == record
#         assert check.amiqus_id == data["id"]
#         assert check.check_type == data["name"]
#         assert check.status == data["status"]
#         assert check.result == data["result"]
#         assert check.created_at == date_parse(data["created_at"])


# @pytest.mark.django_db
# class TestCheckModel:
#     def test_defaults(self, record):
#         """Test default property values."""
#         check = Check(amiqus_record=record, amiqus_id="foo", check_type="document")
#         assert check.amiqus_id == "foo"
#         assert check.created_at is None
#         assert check.status is None
#         assert check.result is None
#         assert check.check_type == "document"

#     def test_parse(self):
#         """Test the parse_raw method."""
#         data = copy.deepcopy(TEST_REPORT_IDENTITY_ENHANCED)
#         assert "breakdown" in data
#         assert "properties" in data
#         check = Check().parse(data)
#         # the default check scrubber should have removed data:
#         assert "breakdown" not in check.raw
#         assert "properties" not in check.raw
#         assert check.amiqus_id == IDENTITY_REPORT_ID
#         assert check.created_at == date_parse(data["created_at"])
#         assert check.status == TEST_REPORT_IDENTITY_ENHANCED["status"]
#         assert check.result == TEST_REPORT_IDENTITY_ENHANCED["result"]
#         assert check.check_type == TEST_REPORT_IDENTITY_ENHANCED["name"]
