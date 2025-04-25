import unittest
from unittest.mock import patch

from src.validators import is_required, must_be_empty, is_email, is_host, is_doi, get_invalid_dois, validate_dois


class TestValidators(unittest.TestCase):
    def test_is_required_succeeds_with_value(self):
        expected_output = {"ok": True, "value": "value"}

        self.assertEqual(expected_output, is_required("value"))

    def test_is_required_fails_with_no_value(self):
        expected_output = {"ok": False, "error": "This field is required."}

        self.assertEqual(expected_output, is_required(""))
        self.assertEqual(expected_output, is_required(None))

    def test_must_be_empty_with_value(self):
        expected_output = {"ok": False, "error": "This field must be empty."}

        self.assertEqual(expected_output, must_be_empty("value"))

    def test_must_be_empty_with_no_value(self):
        expected_output = {"ok": True, "value": ""}

        self.assertEqual(expected_output, must_be_empty(""))

    def test_is_email_with_email(self):
        test_email = "someone@somewhere.com"

        result = is_email(test_email)

        assert result["ok"]

    def test_is_email_with_fake_email(self):
        test_email = "someonesomewhere.com"

        result = is_email(test_email)

        assert not result["ok"]

    def test_is_host_with_correct_format(self):
        host = "somewhere.com"

        result = is_host(host)

        assert result["ok"]

    def test_is_host_with_incorrect_format(self):
        host = "https://somewhere.com"

        result = is_host(host)

        assert not result["ok"]


class TestDOIValidators(unittest.TestCase):
    def test_is_doi_valid_inputs(self):
        """Test is_doi with valid DOI formats"""
        valid_dois = [
            "10.1234/abc123",
            "10.12345/abc-123",
            "10.123456/ABC_123",
            "10.1234/ab.c_1-2:3",
            "10.9999/abc;123(45)def",
            "10.12345678/abcdefghijklmnopqrstuvwxyz",
            "10.1234/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "10.5555/0123456789",
            "10.1234/a/b/c",
        ]

        for doi in valid_dois:
            with self.subTest(doi=doi):
                self.assertTrue(is_doi(doi), f"Expected '{doi}' to be recognized as valid")

    def test_is_doi_invalid_inputs(self):
        """Test is_doi with invalid DOI formats"""
        invalid_dois = [
            "",
            "abc123",  # Missing prefix
            "10.123/abc",  # Prefix too short
            "11.1234/abc",  # Wrong prefix number
            "10.1234.abc",  # Missing slash
            "10./abc123",  # Missing number after period
            "10.1234/",  # Missing suffix
            "10.1234/ abc123",  # Space in DOI
            "10,1234/abc123",  # Invalid character in prefix
            "10.1234/abc!@#",  # Invalid special characters
        ]

        for doi in invalid_dois:
            with self.subTest(doi=doi):
                self.assertFalse(is_doi(doi), f"Expected '{doi}' to be recognized as invalid")

    def test_is_doi_whitespace_handling(self):
        """Test that is_doi handles whitespace properly"""
        # Whitespace should be stripped
        self.assertTrue(is_doi("  10.1234/abc123  "))
        self.assertTrue(is_doi("\t10.1234/abc123\n"))

    def test_get_invalid_dois(self):
        """Test get_invalid_dois function"""
        # Mix of valid and invalid DOIs
        mixed_dois = [
            "10.1234/abc",  # Valid
            "invalid-doi",  # Invalid
            "10.5678/xyz",  # Valid
            "10.123/short",  # Invalid (prefix too short)
            "",
        ]

        expected_invalid = ["invalid-doi", "10.123/short", ""]
        result = get_invalid_dois(mixed_dois)

        self.assertEqual(result, expected_invalid)
        self.assertEqual(len(result), 3)

    def test_get_invalid_dois_all_valid(self):
        """Test get_invalid_dois when all DOIs are valid"""
        valid_dois = ["10.1234/abc", "10.5678/xyz"]
        result = get_invalid_dois(valid_dois)

        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)

    def test_get_invalid_dois_all_invalid(self):
        """Test get_invalid_dois when all DOIs are invalid"""
        invalid_dois = ["invalid1", "invalid2", ""]
        result = get_invalid_dois(invalid_dois)

        self.assertEqual(result, invalid_dois)
        self.assertEqual(len(result), 3)

    @patch("src.helpers.get_list_from_str")
    def test_validate_dois_valid(self, mock_get_list):
        """Test validate_dois with valid DOIs"""
        mock_get_list.return_value = ["10.1234/abc", "10.5678/xyz"]

        result = validate_dois("10.1234/abc\n10.5678/xyz")

        self.assertTrue(result["ok"])
        self.assertEqual(result["value"], ["10.1234/abc", "10.5678/xyz"])

    def test_validate_dois_invalid(self):
        """Test validate_dois with invalid DOIs"""
        result = validate_dois("some\ninput\nstring")

        self.assertFalse(result["ok"])
        self.assertIn("Invalid DOIs given:", result["error"])
