import unittest
from unittest.mock import patch, MagicMock
import http.client
import socket

from src.http_client import Client


class TestClient(unittest.TestCase):
    def setUp(self):
        self.test_host = "api.example.com"
        self.test_headers = {"Content-Type": "application/json"}
        self.client = Client(timeout=10, max_retries=2, retry_delay=1, host=self.test_host, headers=self.test_headers)

    @patch("ssl.create_default_context")
    def test_init(self, mock_ssl_context):
        """Test initialization with custom values"""
        client = Client(timeout=10, max_retries=2, retry_delay=1, host=self.test_host, headers=self.test_headers)

        self.assertEqual(client.timeout, 10)
        self.assertEqual(client.max_retries, 2)
        self.assertEqual(client.retry_delay, 1)
        self.assertEqual(client.host, self.test_host)
        self.assertEqual(client.headers, self.test_headers)
        mock_ssl_context.assert_called_once()
        self.assertIsNone(client.conn)

    @patch("http.client.HTTPSConnection")
    def test_enter(self, mock_https_conn):
        """Test __enter__ method"""
        mock_connection = MagicMock()
        mock_https_conn.return_value = mock_connection

        with self.client as client:
            self.assertEqual(client, self.client)
            mock_https_conn.assert_called_once_with(host=self.test_host, timeout=10, context=self.client.context)
            self.assertEqual(client.conn, mock_connection)

    @patch("http.client.HTTPSConnection")
    def test_exit(self, mock_https_conn):
        """Test __exit__ method"""
        mock_connection = MagicMock()
        mock_https_conn.return_value = mock_connection

        with self.client:
            pass

        mock_connection.close.assert_called_once()
        self.assertIsNone(self.client.conn)

    @patch("http.client.HTTPSConnection")
    def test_create_connection(self, mock_https_conn):
        mock_connection = MagicMock()
        mock_https_conn.return_value = mock_connection

        self.client._create_connection()

        mock_https_conn.assert_called_once_with(host=self.test_host, timeout=10, context=self.client.context)
        self.assertEqual(self.client.conn, mock_connection)

    def test_close_connection(self):
        mock_conn = MagicMock()
        self.client.conn = mock_conn

        self.client.close_connection()

        mock_conn.close.assert_called_once()
        self.assertIsNone(self.client.conn)

    @patch("http.client.HTTPSConnection")
    @patch("builtins.print")
    @patch("time.sleep")
    def test_request_success(self, mock_sleep, mock_print, mock_https_conn):
        mock_connection = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 200
        mock_connection.getresponse.return_value = mock_response
        mock_https_conn.return_value = mock_connection

        self.client.conn = mock_connection
        result = self.client.request("/api/endpoint", method="GET", headers={"X-Custom": "Value"})

        mock_connection.request.assert_called_once_with("GET", "/api/endpoint", headers={"X-Custom": "Value"})
        self.assertEqual(result, mock_response)

    @patch("http.client.HTTPSConnection")
    @patch("builtins.print")
    @patch("time.sleep")
    def test_request_404(self, mock_sleep, mock_print, mock_https_conn):
        mock_connection = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 404
        mock_connection.getresponse.return_value = mock_response
        mock_https_conn.return_value = mock_connection

        self.client.conn = mock_connection
        result = self.client.request("/api/nonexistent")

        mock_connection.request.assert_called_once()
        self.assertEqual(result, mock_response)

    @patch("http.client.HTTPSConnection")
    @patch("builtins.print")
    @patch("time.sleep")
    def test_request_retry_success(self, mock_sleep, mock_print, mock_https_conn):
        """Test retry that eventually succeeds"""
        mock_connection = MagicMock()
        mock_https_conn.return_value = mock_connection

        # First attempt fails with connection error
        # Second attempt succeeds
        mock_connection.request.side_effect = [http.client.HTTPException("Connection error"), None]

        # Mock responses for first and second attempts
        mock_failed_response = MagicMock()
        mock_failed_response.status = 500

        mock_success_response = MagicMock()
        mock_success_response.status = 200

        mock_connection.getresponse.side_effect = [mock_success_response]

        result = self.client.request("/api/endpoint")

        mock_sleep.assert_called_once_with(1)

        self.assertEqual(result, mock_success_response)

    @patch("http.client.HTTPSConnection")
    @patch("builtins.print")
    @patch("time.sleep")
    def test_request_max_retries_exhausted(self, mock_sleep, mock_print, mock_https_conn):
        mock_connection = MagicMock()
        mock_https_conn.return_value = mock_connection

        # All requests fail with timeout
        mock_connection.request.side_effect = socket.timeout("Timeout")

        result = self.client.request("/api/endpoint")

        mock_sleep.assert_called_once_with(1)

        self.assertIsNone(result)

        mock_print.assert_any_call("Failed to fetch data after retries.")

    def test_get_response_data(self):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"key": "value"}'

        result = self.client.get_response_data(mock_response)

        self.assertEqual(result, '{"key": "value"}')

    def test_get_json_dict_from_response_success(self):
        json_str = '{"key": "value", "number": 42}'

        result = self.client.get_json_dict_from_response(json_str)

        self.assertEqual(result, {"key": "value", "number": 42})

    def test_get_json_dict_from_response_failure(self):
        invalid_json = '{key: "value"}'

        result = self.client.get_json_dict_from_response(invalid_json)

        self.assertTrue(isinstance(result, str))
        self.assertTrue(result.startswith("ERROR reading json"))


if __name__ == "__main__":
    unittest.main()
