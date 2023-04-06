from decimal import Decimal
from unittest import mock

import pytest
from dateutil.parser import parse as date_parse
from django.contrib.auth import get_user_model

from amiqus.admin import Client, EventsMixin, RawMixin, Record, ResultMixin, UserMixin


class TestResultMixin:
    @mock.patch.object(Record, "mark_as_clear")
    def test__events(self, mock_clear):
        def request():
            request = mock.Mock()
            request.user = get_user_model()()
            return request

        record = Record()
        request = request()
        mixin = ResultMixin()
        mixin.mark_as_clear(request, [record])
        mock_clear.assert_called_once_with(request.user)


@pytest.mark.django_db
class TestEventsMixin:
    """amiqus.admin.EventsMixin tests."""

    @mock.patch.object(Record, "events")
    def test__events(self, mock_events, event_data, event):
        payload = event_data["payload"]
        action = payload["action"]
        completed_at = date_parse(payload["object"]["completed_at_iso8601"])
        mock_events.return_value = [event]
        mixin = EventsMixin()
        record = Record()
        html = mixin._events(record)
        assert html == (f"<ul><li>{completed_at.date()}: {action}</li></ul>")


class TestRawMixin:
    def test__raw(self):
        mixin = RawMixin()
        obj = Client(raw={"foo": "bar"})
        html = mixin._raw(obj)
        assert (
            html == '<code>{<br>&nbsp;&nbsp;&nbsp;&nbsp;"foo":&nbsp;"bar"<br>}</code>'
        )

        # test with Decimal (stdlib json won't work) and unicode
        obj = Client(raw={"foo": Decimal(1.0), "bar": "åß∂ƒ©˙∆"})
        html = mixin._raw(obj)


class TestUserMixin:
    def test__user(self):
        def assertUser(first_name, last_name, expected):
            mixin = UserMixin()
            user = get_user_model()(first_name=first_name, last_name=last_name)
            obj = mock.Mock(user=user)
            assert mixin._user(obj) == expected

        assertUser("fred", "flintstone", "Fred Flintstone")
        assertUser("", "", "")
        assertUser("fredå", "flintstone", "Fredå Flintstone")
