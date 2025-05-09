"""Tests for webhook functionality."""
import json
from unittest import mock
from django.utils.timezone import now

import pytest

from amiqus.models import Review, Record, Event
from amiqus.views import status_update
from amiqus.signals import record_reviewed
from amiqus.helpers import create_or_update_reviews


@pytest.mark.django_db
class TestRecordReviewedWebhook:
    """Test handling of record.reviewed webhook events."""

    @mock.patch("amiqus.models.Record.update_status")
    @mock.patch("amiqus.models.Event.parse")
    def test_record_reviewed_signal(
        self, mock_parse, mock_update, rf, record_reviewed_event, record
    ):
        """Test that record.reviewed events trigger the signal."""
        # Mock the event parse to return an event with our record
        mock_event = Event(
            amiqus_id=record.amiqus_id,
            resource_type="record",
            action="record.reviewed",
            received_at=now(),
        )
        # Mock the _resource_manager to return a manager that will return our record
        mock_manager = mock.Mock()
        mock_manager.get.return_value = record
        mock_event._resource_manager = mock.Mock(return_value=mock_manager)
        mock_parse.return_value = mock_event

        signal_handler = mock.Mock()
        record_reviewed.connect(signal_handler)

        # Mock create_reviews to prevent API calls
        with mock.patch("amiqus.views.create_or_update_reviews"):
            request = rf.post(
                "/",
                data=json.dumps(record_reviewed_event),
                content_type="application/json",
            )
            response = status_update(request)

            assert response.status_code == 200
            assert response.content.decode("utf-8") == "Update processed."

            # Verify signal was called with correct args
            signal_handler.assert_called_once()
            args, kwargs = signal_handler.call_args
            assert kwargs["sender"] == Record
            assert kwargs["record"] == record
            assert isinstance(kwargs["event"], Event)
            assert kwargs["data"] == record_reviewed_event

    @mock.patch("amiqus.helpers.get")
    def test_create_reviews(self, mock_get, record):
        """Test create_reviews helper creates Review objects from API data."""
        # Get the steps that were automatically created with the record
        steps = record.steps.all()
        assert len(steps) == 3

        # Mock the API response to return different review IDs for each step
        def get_mock_response(url):
            step_id = url.split("/")[
                -2
            ]  # URL format: records/{record_id}/steps/{step_id}/reviews
            return {
                "data": [
                    {
                        "id": f"review-{step_id}",
                        "status": "approved",
                        "created_at": "2023-04-06T15:17:50+00:00",
                    }
                ]
            }

        mock_get.side_effect = get_mock_response

        # Create an event with required received_at
        event = Event.objects.create(
            amiqus_id="event-123",
            action="record.reviewed",
            resource_type="record",
            received_at=now(),
            raw={"data": {"record": {"id": record.amiqus_id}}},
        )

        # Call create_reviews
        create_or_update_reviews(event)

        # Verify API was called for each step
        assert mock_get.call_count == len(steps)
        for step in steps:
            expected_url = f"records/{record.amiqus_id}/steps/{step.amiqus_id}/reviews"
            mock_get.assert_any_call(expected_url)

        # Verify Reviews were created with unique IDs
        for step in steps:
            review = Review.objects.get(amiqus_id=f"review-{step.amiqus_id}")
            assert review.step == step
            assert review.status == "approved"
