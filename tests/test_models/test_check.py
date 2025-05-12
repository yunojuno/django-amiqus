import copy
from unittest import mock

import pytest
from dateutil.parser import parse as date_parse

from amiqus.models import Check
from amiqus.models.base import BaseModel

from ..conftest import TEST_CHECK_PHOTO_ID


@pytest.mark.django_db
class TestCheckManager:
    @mock.patch.object(BaseModel, "full_clean")
    def test_create_check(self, mock_clean, user, record):
        """Test the create method parses response."""
        data = copy.deepcopy(TEST_CHECK_PHOTO_ID)
        check = Check.objects.create_check(record=record, raw=data)
        assert check.user == user
        assert check.amiqus_record == record
        assert check.amiqus_id == data["id"]
        assert check.check_type == "check.photo_id"  # should add check. prefix
        assert check.status == data["status"]
        assert check.created_at == date_parse(data["created_at"])
        assert check.updated_at == date_parse(data["updated_at"])


@pytest.mark.django_db
class TestCheckModel:
    def test_defaults(self, record):
        """Test default property values."""
        check = Check(
            amiqus_record=record, amiqus_id="foo", check_type="check.document"
        )
        assert check.amiqus_id == "foo"
        assert check.created_at is None
        assert check.status is None
        assert check.check_type == "check.document"
        assert check.updated_at is None

    def test_parse(self):
        """Test the parse method."""
        data = copy.deepcopy(TEST_CHECK_PHOTO_ID)
        check = Check().parse(data)
        assert check.amiqus_id == data["id"]
        assert check.created_at == date_parse(data["created_at"])
        assert check.status == data["status"]
        assert check.check_type == "check.photo_id"  # should add check. prefix
        assert check.updated_at == date_parse(data["updated_at"])

    def test_parse_check_type_with_prefix(self):
        """Test parsing when type already has check. prefix."""
        data = copy.deepcopy(TEST_CHECK_PHOTO_ID)
        data["type"] = "check.photo_id"
        check = Check().parse(data)
        assert check.check_type == "check.photo_id"

    def test_parse_check_type_without_prefix(self):
        """Test parsing when type needs check. prefix added."""
        data = copy.deepcopy(TEST_CHECK_PHOTO_ID)
        data["type"] = "photo_id"
        check = Check().parse(data)
        assert check.check_type == "check.photo_id"

    def test_parse_check_id_from_check_field(self):
        """Test parsing amiqus_id from check field."""
        data = copy.deepcopy(TEST_CHECK_PHOTO_ID)
        data["check"] = "456"
        check = Check().parse(data)
        assert check.amiqus_id == "456"  # should use check field when present

    def test_parse_check_id_from_id_field(self):
        """Test parsing amiqus_id from id field when check field missing."""
        data = copy.deepcopy(TEST_CHECK_PHOTO_ID)
        check = Check().parse(data)
        assert check.amiqus_id == data["id"]  # should fallback to id field
