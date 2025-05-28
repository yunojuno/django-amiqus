from unittest import mock

from django.test import TestCase

from amiqus.api import ApiError, _headers, _respond, _url, get, post, patch
from amiqus.settings import DEFAULT_REQUESTS_TIMEOUT


class ApiTests(TestCase):
    """amiqus.api module tests."""

    def test__headers(self):
        """Test the _headers function return valid dict."""
        self.assertEqual(
            _headers(api_key="foo"),
            {"Authorization": "Bearer foo", "Content-Type": "application/json"},
        )

    def test__respond(self):
        """Test the _respond function handles 2xx."""
        response = mock.Mock()
        response.status_code = 200
        self.assertEqual(_respond(response), response.json.return_value)
        # non-2xx should raise error
        response.status_code = 400
        response.json.return_value = {"error": {"message": "foo", "type": "bar"}}
        self.assertRaises(ApiError, _respond, response)

    @mock.patch("requests.get")
    @mock.patch("amiqus.api._headers")
    def test_get(self, mock_headers, mock_get):
        """Test the get function calls API."""
        response = mock.Mock()
        response.status_code = 200
        headers = mock_headers.return_value
        mock_get.return_value = response
        self.assertEqual(get("/"), response.json.return_value)
        mock_get.assert_called_once_with(
            _url("/"),
            headers=headers,
            timeout=DEFAULT_REQUESTS_TIMEOUT,
        )

    @mock.patch("requests.post")
    @mock.patch("amiqus.api._headers")
    def test_post(self, mock_headers, mock_post):
        """Test the get function calls API."""
        response = mock.Mock()
        response.status_code = 200
        headers = mock_headers.return_value
        data = {"foo": "bar"}
        mock_post.return_value = response
        self.assertEqual(post("/", data=data), response.json.return_value)
        mock_post.assert_called_once_with(
            _url("/"),
            headers=headers,
            json=data,
            timeout=DEFAULT_REQUESTS_TIMEOUT,
        )

    @mock.patch("requests.patch")
    @mock.patch("amiqus.api._headers")
    def test_patch(self, mock_headers, mock_patch):
        """Test the patch function calls API correctly."""
        response = mock.Mock()
        response.status_code = 200
        headers = mock_headers.return_value
        data = {"foo": "bar"}
        mock_patch.return_value = response
        self.assertEqual(patch("/", data=data), response.json.return_value)
        mock_patch.assert_called_once_with(
            _url("/"),
            headers=headers,
            json=data,
            timeout=DEFAULT_REQUESTS_TIMEOUT,
        )
