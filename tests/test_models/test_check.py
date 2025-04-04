import copy

import pytest
from dateutil.parser import parse as date_parse
from django.core.exceptions import ValidationError
from amiqus.models import Record
from ..conftest import TEST_RECORD, TEST_RECORD_ID, TEST_CHECK_ID, TEST_CHECK_ID_2


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

    def test_create_record_with_checks(self, user, client):
        """Test checks are created correctly from record creation."""
        data = copy.deepcopy(TEST_RECORD)

        record = Record.objects.create_record(client=client, raw=data)

        # Verify checks were created
        checks = record.checks.all()
        assert checks.count() == 2

        # Verify first check
        photo_check = checks.get(check_type="check.photo_id")
        assert photo_check.amiqus_id == str(TEST_CHECK_ID)
        assert photo_check.user == user
        assert photo_check.amiqus_record == record

        # Verify second check
        doc_check = checks.get(
            check_type="check.watchlist.peps_sanctions_media_extended"
        )
        assert doc_check.amiqus_id == str(TEST_CHECK_ID_2)
        assert doc_check.user == user
        assert doc_check.amiqus_record == record

    def test_create_record_duplicate_checks(self, user, client):
        """Test checks aren't duplicated if record is created multiple times."""
        data = {
            "id": TEST_RECORD_ID,
            "status": "pending",
            "created_at": "2022-05-22T08:22:12Z",
            "steps": [
                {
                    "type": "check.photo_id",
                    "check": "12345",
                    "preferences": {"report_type": "standard"},
                }
            ],
        }

        record1 = Record.objects.create_record(client=client, raw=data)

        # Attempt to create record twice with the same data
        with pytest.raises(ValidationError) as excinfo:
            Record.objects.create_record(client=client, raw=data)
        assert "Record with this Amiqus ID already exists." in str(excinfo.value)

        # Verify only one check exists
        assert record1.checks.count() == 1

    def test_create_record_no_checks(self, user, client):
        """Test record creation works when no checks are present."""
        data = {
            "id": TEST_RECORD_ID,
            "status": "pending",
            "created_at": "2022-05-22T08:22:12Z",
            "steps": [],
        }
        record = Record.objects.create_record(client=client, raw=data)
        assert record.checks.count() == 0


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
