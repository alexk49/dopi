import unittest
from unittest.mock import patch, MagicMock, call
import json

from src.crossref import (
    fetch_dois_data,
    process_single_doi,
    get_resolving_url_for_doi,
    validate_resolving_url,
)


class TestCrossRefFunctions(unittest.TestCase):
    def setUp(self):
        self.sample_doi = "10.1234/test"

        self.sample_response_dict = {"message": {"resource": {"primary": {"URL": "https://example.org/10.1234/test"}}}}

    @patch("src.crossref.Client")
    @patch("src.crossref.process_single_doi")
    def test_fetch_dois_data(self, mock_process_single_doi, mock_client_class):
        mock_client_instance = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client_instance

        dois = ["10.1234/test1", "10.1234/test2"]
        mock_result1 = {"doi": "10.1234/test1", "status": "SUCCESS"}
        mock_result2 = {"doi": "10.1234/test2", "status": "FAILURE"}

        mock_process_single_doi.side_effect = [mock_result1, mock_result2]

        results = fetch_dois_data(dois, "example.org", True)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], mock_result1)
        self.assertEqual(results[1], mock_result2)

        expected_calls = [
            call(mock_client_instance, "10.1234/test1", "example.org", True),
            call(mock_client_instance, "10.1234/test2", "example.org", True),
        ]
        mock_process_single_doi.assert_has_calls(expected_calls)

        mock_client_class.assert_called_once()
        mock_client_class.return_value.__exit__.assert_called_once()

    @patch("builtins.print")
    def test_process_single_doi_success(self, mock_print):
        mock_client = MagicMock()
        mock_response = MagicMock()

        response_data = json.dumps(self.sample_response_dict)

        mock_client.request.return_value = mock_response
        mock_client.get_response_data.return_value = response_data
        mock_client.get_json_dict_from_response.return_value = self.sample_response_dict

        result = process_single_doi(mock_client, self.sample_doi, "example.org", True)

        mock_client.request.assert_called_once_with(f"/works/{self.sample_doi}")
        mock_client.get_response_data.assert_called_once_with(mock_response)
        mock_client.get_json_dict_from_response.assert_called_once_with(response_data)

        self.assertEqual(result["doi"], self.sample_doi)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["resolving_url"], "https://example.org/10.1234/test")
        self.assertEqual(result["ERRORS"], "")
        self.assertEqual(result["full_metadata"], self.sample_response_dict)

        mock_print.assert_any_call(f"Received data for DOI {self.sample_doi}")

    @patch("builtins.print")
    def test_process_single_doi_not_found(self, mock_print):
        mock_client = MagicMock()
        mock_response = MagicMock()

        mock_client.request.return_value = mock_response
        mock_client.get_response_data.return_value = "Resource not found."

        result = process_single_doi(mock_client, self.sample_doi, "example.org", True)

        self.assertEqual(result["doi"], self.sample_doi)
        self.assertEqual(result["status"], "FAILURE")
        self.assertEqual(result["ERRORS"], "Resource not found.")
        self.assertEqual(result["resolving_url"], "not_found")

    @patch("builtins.print")
    def test_process_single_doi_json_error(self, mock_print):
        mock_client = MagicMock()
        mock_response = MagicMock()

        mock_client.request.return_value = mock_response
        mock_client.get_response_data.return_value = "valid response"
        mock_client.get_json_dict_from_response.return_value = "ERROR parsing JSON"

        result = process_single_doi(mock_client, self.sample_doi, "example.org", True)

        self.assertEqual(result["doi"], self.sample_doi)
        self.assertEqual(result["status"], "FAILURE")
        self.assertEqual(result["ERRORS"], "ERROR parsing JSON")

    @patch("builtins.print")
    def test_process_single_doi_no_full_metadata(self, mock_print):
        mock_client = MagicMock()
        mock_response = MagicMock()

        response_data = json.dumps(self.sample_response_dict)

        mock_client.request.return_value = mock_response
        mock_client.get_response_data.return_value = response_data
        mock_client.get_json_dict_from_response.return_value = self.sample_response_dict

        result = process_single_doi(mock_client, self.sample_doi, "example.org", False)

        self.assertEqual(result["full_metadata"], {"message": {}})

    def test_get_resolving_url_for_doi_success(self):
        url = get_resolving_url_for_doi(self.sample_response_dict)

        self.assertEqual(url, "https://example.org/10.1234/test")

    @patch("builtins.print")
    def test_get_resolving_url_for_doi_error(self, mock_print):
        bad_response_dict = {"message": {}}

        url = get_resolving_url_for_doi(bad_response_dict)

        self.assertEqual(url, "")
        mock_print.assert_called_once()

    @patch("builtins.print")
    def test_validate_resolving_url_success(self, mock_print):
        result_dict = {
            "doi": self.sample_doi,
            "status": "FAILURE",
            "resolving_url": "not_found",
            "ERRORS": "",
            "full_metadata": {"message": {}},
        }

        updated_result = validate_resolving_url(self.sample_doi, self.sample_response_dict, "example.org", result_dict)

        self.assertEqual(updated_result["status"], "SUCCESS")
        self.assertEqual(updated_result["resolving_url"], "https://example.org/10.1234/test")
        self.assertEqual(updated_result["ERRORS"], "")

    @patch("builtins.print")
    def test_validate_resolving_url_failure(self, mock_print):
        result_dict = {
            "doi": self.sample_doi,
            "status": "FAILURE",
            "resolving_url": "not_found",
            "ERRORS": "",
            "full_metadata": {"message": {}},
        }

        updated_result = validate_resolving_url(
            self.sample_doi, self.sample_response_dict, "different-host.com", result_dict
        )

        self.assertEqual(updated_result["status"], "FAILURE")
        self.assertEqual(updated_result["resolving_url"], "https://example.org/10.1234/test")
        self.assertTrue("does not resolve correctly" in updated_result["ERRORS"])

    @patch("builtins.print")
    def test_validate_resolving_url_no_url_found(self, mock_print):
        result_dict = {
            "doi": self.sample_doi,
            "status": "FAILURE",
            "resolving_url": "not_found",
            "ERRORS": "",
            "full_metadata": {"message": {}},
        }

        bad_response_dict = {"message": {}}

        with patch("src.crossref.get_resolving_url_for_doi", return_value=""):
            updated_result = validate_resolving_url(self.sample_doi, bad_response_dict, "example.org", result_dict)

        self.assertEqual(updated_result["status"], "FAILURE")
        self.assertEqual(updated_result["ERRORS"], "Unable to find resolving URL in metadata")


if __name__ == "__main__":
    unittest.main()
