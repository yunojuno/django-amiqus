import copy

import pytest
from dateutil.parser import parse as date_parse

from amiqus.models import Record
from ..conftest import TEST_RECORD, TEST_RECORD_ID


@pytest.mark.django_db
class TestRecordManager:
    """amiqus.models.ClientManager tests."""

    def test_create_record(self, user, client):
        """Test the create method parses response."""
        data = copy.deepcopy(TEST_RECORD)
        record = Record.objects.create_record(client=client, raw=data)
        assert record.user == user
        assert record.client == client
        assert record.amiqus_id == str(data["id"])
        assert record.status == data["status"]
        assert record.created_at == date_parse(data["created_at"])


@pytest.mark.django_db
class TestRecordModel:
    """amiqus.models.Record tests."""

    def test_defaults(self, user, client):
        """Test default property values."""
        record = Record(
            user=user, client=client, amiqus_id=TEST_RECORD_ID, raw=TEST_RECORD
        )
        assert record.amiqus_id == TEST_RECORD_ID
        assert record.raw == TEST_RECORD
        assert record.created_at is None
        assert record.status is None
