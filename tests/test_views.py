import json

from django.test import RequestFactory

from amiqus.views import status_update


class TestViews:
    # @mock.patch("amiqus.decorators._match", lambda x, y: True)
    def assert_update(self, rf: RequestFactory, data: dict, message: str) -> None:
        request = rf.post(
            "/",
            data=json.dumps(data),
            content_type="application/json",
        )
        response = status_update(request)
        assert response.status_code == 200, response.status_code
        assert response.content.decode("utf-8") == message, response.content

    def test_status_update__empty(self, rf: RequestFactory, event_data: dict) -> None:
        self.assert_update(rf, {}, "Empty webhook.")

    def test_status_update__invalid_resource(
        self, rf: RequestFactory, event_data: dict
    ) -> None:
        event_data["trigger"] = {"foo": "bar"}
        self.assert_update(rf, event_data, "Invalid webhook body.")

        # unknown Record
        # with mock.patch.object(Record, "objects") as mock_manager:
        #     mock_manager.get.side_effect = Record.DoesNotExist()
        #     assert_update(data, "Record not found.")

        # # unknown Check
        # data["payload"]["resource_type"] = "check"
        # with mock.patch.object(Check, "objects") as mock_manager:
        #     mock_manager.get.side_effect = Check.DoesNotExist()
        #     assert_update(data, "Check not found.")

        # # unknown exception
        # with mock.patch.object(Event, "parse") as mock_parse:
        #     mock_parse.side_effect = Exception("foobar")
        #     assert_update(data, "Unknown error.")

        # # valid payload / object
        # mock_record = mock.Mock(spec=Record)
        # with mock.patch(
        #     "amiqus.models.Event.resource",
        #     new_callable=mock.PropertyMock(return_value=mock_record),
        # ):
        #     # mock_resource.return_value = mock_record
        #     assert_update(data, "Update processed.")
        #     mock_record.update_status.assert_called_once()

        # # now record that a good payload passes.
        # data["payload"]["resource_type"] = "record"
        # user = get_user_model().objects.create_user("fred")
        # client = Client(user=user, amiqus_id="foo").save()
        # record = Record(user=user, client=client)
        # record.amiqus_id = data["payload"]["object"]["id"]
        # record.save()

        # # validate that the LOG_EVENTS setting is honoured
        # with mock.patch.object(Event, "save") as mock_save:
        #     with mock.patch("amiqus.views.LOG_EVENTS", False):
        #         assert_update(data, "Update processed.")
        #         mock_save.assert_not_called()

        #     # force creation of event
        #     with mock.patch("amiqus.views.LOG_EVENTS", True):
        #         assert_update(data, "Update processed.")
        #         mock_save.assert_called_once_with()
