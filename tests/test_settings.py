from unittest import mock

from django.test import TestCase

from amiqus import settings


class SettingsTests(TestCase):
    """amiqus.settings module tests."""

    def test_default_check_scrubber(self):
        """Test the check_scrubber default function."""
        data = {"id": "123", "foo": "bar", "email": "test@test.com"}
        clean = settings.DEFAULT_CHECK_SCRUBBER(data)
        self.assertEqual(clean, {"id": "123", "foo": "bar"})

    # mock scrubber that does nothing and returns the data unchanged
    @mock.patch("amiqus.settings.scrub_check_data", lambda d: d)
    def test_override_check_scrubber(self):
        """Test the check_scrubber default function."""
        data = {"foo": "bar", "breakdown": {}, "properties": {}}
        # import here otherwise the mock is ineffective
        from amiqus.settings import scrub_check_data

        # default function should remove breakdown and properties
        scrub_check_data(data)
        self.assertTrue("breakdown" in data)
        self.assertTrue("properties" in data)

    def test_default_applicant_scrubber(self):
        """Test the applicant_scrubber default function."""
        data = {
            "addresses": [],
            "country": "gbr",
            "country_of_birth": None,
            "created_at": "2017-05-03T13:12:17Z",
            "dob": None,
            "email": "foobar@example.com",
            "first_name": "Foo",
            "gender": None,
            "href": "/v3/applicants/1b0f8e99-da6b-4ca5-9580-eed99ff691cd",
            "id": "1b0f8e97-dc6b-4ca5-9580-eed99ff691cd",
            "id_numbers": [],
            "last_name": "Bar",
            "middle_name": None,
            "mobile": None,
            "mothers_maiden_name": None,
            "nationality": None,
            "previous_last_name": None,
            "sandbox": False,
            "telephone": None,
            "title": None,
            "town_of_birth": None,
            "status": "pending",
        }
        clean = settings.DEFAULT_CLIENT_SCRUBBER(data)
        self.assertEqual(
            clean,
            {
                "created_at": "2017-05-03T13:12:17Z",
                "status": "pending",
                "id": "1b0f8e97-dc6b-4ca5-9580-eed99ff691cd",
            },
        )
