import json

from django.test import RequestFactory

from amiqus.decorators import _hmac
from amiqus.models import Check, Client, Event, Record
from amiqus.views import status_update


class TestViews:
    """amiqus.views module tests."""

    # @mock.patch("amiqus.decorators._match", lambda x, y: True)
    def assert_update(self, rf, data, message):
        request = rf.post(
            "/", data=json.dumps(data), content_type="application/json"
        )
        response = status_update(request)
        assert response.status_code == 200, response.status_code
        assert response.content.decode("utf-8") == message, response.content

    def test_empty_content(self, rf: RequestFactory, event_data: dict):
        """Test the status_update view function."""
        self.assert_update(rf, {}, "Empty event content.")

    def test_missing_trigger(self, rf: RequestFactory):
        self.assert_update(rf, {"foo": "bar"}, "Missing trigger.")

    def test_invalid_resource(self, rf: RequestFactory, event_data: dict)->None:
        event_data["trigger"]["alias"] = "foo"
        self.assert_update(rf, event_data, "Unknown resource type.")

    def test_unknown_record(self, rf: RequestFactory, event_data: dict)->None:
        event_data["trigger"]["alias"] = "record"
        with mock.patch.object(Record, "objects") as mock_manager:
            mock_manager.get.side_effect = Record.DoesNotExist()
            self.assert_update(rf, event_data, "Record not found.")

    def test_unknown_check(self, rf: RequestFactory, event_data: dict)->None:
        event_data["trigger"]["alias"] = "check"
        with mock.patch.object(Check, "objects") as mock_manager:
            mock_manager.get.side_effect = Check.DoesNotExist()
            self.assert_update(rf, event_data, "Check not found.")

    def test_unknown_exception(self, rf: RequestFactory, event_data: dict)->None:
        with mock.patch.object(Event, "parse") as mock_parse:
            mock_parse.side_effect = Exception("foobar")
            self.assert_update(rf, event_data, "Unknown error.")

        # # valid payload / object
        # mock_record = mock.Mock(spec=Record)
        # with mock.patch(
        #     "amiqus.models.Event.resource",
        #     new_callable=mock.PropertyMock(return_value=mock_record),
        # ):
        #     # mock_resource.return_value = mock_record
        #     assert_update(event_data, "Update processed.")
        #     mock_record.update_status.assert_called_once()

        # # now record that a good payload passes.
        # event_data["trigger"]["alias"] = "record"
        # user = get_user_model().objects.create_user("fred")
        # client = Client(user=user, amiqus_id="foo").save()
        # record = Record(user=user, client=client)
        # record.amiqus_id = event_data["data"]["record"]["id"]
        # record.save()

        # # validate that the LOG_EVENTS setting is honoured
        # with mock.patch.object(Event, "save") as mock_save:
        #     with mock.patch("amiqus.views.LOG_EVENTS", False):
        #         assert_update(event_data, "Update processed.")
        #         mock_save.assert_not_called()

        #     # force creation of event
        #     with mock.patch("amiqus.views.LOG_EVENTS", True):
        #         assert_update(event_data, "Update processed.")
        #         mock_save.assert_called_once_with()
        #         mock_save.assert_called_once_with()
