import copy

import pytest

from amiqus.models import Client, Event, Record

from ..conftest import TEST_EVENT_RECORD_REVIEWED


@pytest.mark.django_db
class TestEventModel:
    def test__resource_manager(self):
        """Test the _resource_manager method."""
        event = Event()
        with pytest.raises(ValueError):
            event._resource_manager()

        event.action = "foo"
        with pytest.raises(ValueError):
            event._resource_manager()

        event.action = "record.reviewed"
        assert event._resource_manager() == Record.objects
        event.action = "client.created"
        assert event._resource_manager() == Client.objects

    def test_defaults(self):
        """Test default property values."""
        event = Event()
        # real data taken from record.json
        assert event.action == ""
        assert event.amiqus_id == ""
        assert event.action == ""
        assert event.status == ""
        assert event.completed_at is None
        assert event.raw is None

    def test_parse(self):
        """Test the parse_raw method."""
        data = copy.deepcopy(TEST_EVENT_RECORD_REVIEWED)
        event = Event().parse(data, entity_type="record")
        # real data taken from record.json
        assert event.resource_type == "record"
        assert event.amiqus_id == data["data"]["record"]["id"]
        assert event.action == data["trigger"]["alias"]
        # assert event.status == data["data"]["record"]["status"]
        # assert event.completed_at == (
        #     date_parse(data["payload"]["object"]["completed_at_iso8601"])
        # )
