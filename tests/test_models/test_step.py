import copy
import pytest
from amiqus.models import Record, Step, Check, Form
from ..conftest import TEST_RECORD, TEST_RECORD_ID, TEST_CHECK_ID, TEST_CHECK_ID_2


@pytest.mark.django_db
class TestStepCreation:
    """Tests for Step creation from Record responses."""

    def test_create_record_creates_steps(self, user, client):
        """Test steps are created automatically when creating a record."""
        data = copy.deepcopy(TEST_RECORD)
        Record.objects.create_record(client=client, raw=data)

        # We should have two steps from TEST_RECORD
        steps = Step.objects.all()
        assert steps.count() == 2

        # Check first step (photo_id)
        photo_step = Step.objects.get(amiqus_check__check_type="check.photo_id")
        assert photo_step.amiqus_id == str(TEST_CHECK_ID)
        assert photo_step.amiqus_check.user == user
        assert photo_step.form is None
        assert photo_step.review is None

        # Check second step (watchlist)
        watchlist_step = Step.objects.get(amiqus_check__check_type="check.watchlist")
        assert watchlist_step.amiqus_id == str(TEST_CHECK_ID_2)
        assert watchlist_step.amiqus_check.user == user
        assert watchlist_step.form is None
        assert watchlist_step.review is None

    def test_create_record_with_form_step(self, user, client):
        """Test creating a record with a form step."""
        data = copy.deepcopy(TEST_RECORD)
        # Add a form step to the test data matching API format
        data["steps"].append(
            {
                "completed_at": None,
                "cost": 0,
                "form": "a66185ca-144c-43fe-9048-1ab74add82b4",
                "id": 3,
                "object": "step",
                "review": None,
                "type": "form",
            }
        )

        record = Record.objects.create_record(client=client, raw=data)

        # Check the form was created
        form = Form.objects.get(amiqus_id="a66185ca-144c-43fe-9048-1ab74add82b4")
        assert form.user == user
        assert form.record == record

        # Check the step was created and linked to the form
        step = Step.objects.get(form=form)
        assert step.amiqus_id == "3"
        assert step.amiqus_check is None
        assert step.review is None
        assert step.raw["type"] == "form"
        assert step.raw["form"] == "a66185ca-144c-43fe-9048-1ab74add82b4"

    def test_create_record_no_steps(self, user, client):
        """Test record creation with no steps."""
        data = {
            "id": TEST_RECORD_ID,
            "status": "pending",
            "created_at": "2025-04-15T10:00:00Z",
            "steps": [],
        }
        Record.objects.create_record(client=client, raw=data)
        assert Step.objects.count() == 0
        assert Check.objects.count() == 0
        assert Form.objects.count() == 0


@pytest.mark.django_db
class TestFormModel:
    """Tests for Form model."""

    def test_form_creation_from_step(self, user, client):
        """Test form creation from step data."""
        data = copy.deepcopy(TEST_RECORD)
        form_id = "a66185ca-144c-43fe-9048-1ab74add82b4"
        data["steps"].append(
            {
                "completed_at": None,
                "cost": 0,
                "form": form_id,
                "id": 3,
                "object": "step",
                "review": None,
                "type": "form",
            }
        )
        record = Record.objects.create_record(client=client, raw=data)

        # Verify form was created with correct ID
        form = Form.objects.get(amiqus_id=form_id)
        assert form.record == record
        assert form.user == user
