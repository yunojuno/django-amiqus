import json
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from amiqus.models import Check, Client, Event, Record
from amiqus.views import status_update


class ViewTests(TestCase):
    """amiqus.views module tests."""

    @mock.patch("amiqus.decorators.WEBHOOK_TOKEN")
    def test_status_update(self, *args):
        """Test the status_update view function."""
        data = {
            "payload": {
                "resource_type": "record",
                "action": "record.form_completed",
                "object": {
                    "id": "5345badd-f4bf-4240-9f3b-ffb998bda09e",
                    "status": "in_progress",
                    "completed_at_iso8601": "2019-10-28T15:00:39Z",
                    "href": "https://api.onfido.com/v3/checks/5345badd-f4bf-4240-9f3b-ffb998bda09e",  # noqa
                },
            }
        }
        factory = RequestFactory()

        @mock.patch("amiqus.decorators._match", lambda x, y: True)
        def assert_update(data, message):
            request = factory.post(
                "/",
                data=json.dumps(data),
                content_type="application/json",
                HTTP_X_SHA2_SIGNATURE="bac836ffcc32856bcf70deb77dd63e432ab13e4d940751db927795f616c85352",  # noqa: E501
            )
            response = status_update(request)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode("utf-8"), message)

        # invalid payload
        assert_update({}, "Unexpected event content.")

        # invalid resource type
        data["payload"]["resource_type"] = "foo"
        assert_update(data, "Unknown resource type.")

        # unknown Record
        data["payload"]["resource_type"] = "record"
        with mock.patch.object(Record, "objects") as mock_manager:
            mock_manager.get.side_effect = Record.DoesNotExist()
            assert_update(data, "Record not found.")

        # unknown Check
        data["payload"]["resource_type"] = "check"
        with mock.patch.object(Check, "objects") as mock_manager:
            mock_manager.get.side_effect = Check.DoesNotExist()
            assert_update(data, "Check not found.")

        # unknown exception
        with mock.patch.object(Event, "parse") as mock_parse:
            mock_parse.side_effect = Exception("foobar")
            assert_update(data, "Unknown error.")

        # valid payload / object
        mock_record = mock.Mock(spec=Record)
        with mock.patch(
            "amiqus.models.Event.resource",
            new_callable=mock.PropertyMock(return_value=mock_record),
        ):
            # mock_resource.return_value = mock_record
            assert_update(data, "Update processed.")
            mock_record.update_status.assert_called_once()

        # now record that a good payload passes.
        data["payload"]["resource_type"] = "record"
        user = get_user_model().objects.create_user("fred")
        client = Client(user=user, amiqus_id="foo").save()
        record = Record(user=user, client=client)
        record.amiqus_id = data["payload"]["object"]["id"]
        record.save()

        # validate that the LOG_EVENTS setting is honoured
        with mock.patch.object(Event, "save") as mock_save:
            with mock.patch("amiqus.views.LOG_EVENTS", False):
                assert_update(data, "Update processed.")
                mock_save.assert_not_called()

            # force creation of event
            with mock.patch("amiqus.views.LOG_EVENTS", True):
                assert_update(data, "Update processed.")
                mock_save.assert_called_once_with()
