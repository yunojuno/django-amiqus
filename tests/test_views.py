import json
from unittest import mock

import pytest
from django.test import RequestFactory

from amiqus.models import Check, Event, Record
from amiqus.views import status_update


class TestStatusUpdateView:
    """amiqus.views module tests."""

    def assert_update(self, rf, data, message):
        request = rf.post("/", data=json.dumps(data), content_type="application/json")
        response = status_update(request)
        assert response.status_code == 200, response.status_code
        assert response.content.decode("utf-8") == message, response.content

    def test_empty_content(self, rf: RequestFactory):
        """Test the status_update view function."""
        self.assert_update(rf, {}, "Empty webhook.")

    def test_missing_trigger(self, rf: RequestFactory):
        self.assert_update(rf, {"foo": "bar"}, "Invalid webhook body.")

    def test_invalid_resource(
        self, rf: RequestFactory, client_status_event: dict
    ) -> None:
        client_status_event["trigger"]["alias"] = "foo"
        self.assert_update(rf, client_status_event, "Invalid event trigger.")

    @pytest.mark.django_db
    def test_unknown_record(
        self, rf: RequestFactory, record_finished_event: dict
    ) -> None:
        with mock.patch.object(Record, "objects") as mock_manager:
            mock_manager.get.side_effect = Record.DoesNotExist()
            self.assert_update(rf, record_finished_event, "Record not found.")

    @pytest.mark.django_db
    def test_unknown_client(
        self, rf: RequestFactory, client_status_event: dict
    ) -> None:
        with mock.patch.object(Check, "objects") as mock_manager:
            mock_manager.get.side_effect = Check.DoesNotExist()
            self.assert_update(rf, client_status_event, "Client not found.")

    def test_error(self, rf: RequestFactory, client_status_event: dict) -> None:
        with mock.patch.object(Event, "parse") as mock_parse:
            mock_parse.side_effect = Exception("foobar")
            self.assert_update(rf, client_status_event, "Unknown error.")
