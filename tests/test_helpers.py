import csv
import os
import unittest
from unittest.mock import mock_open, patch

from pathlib import Path
import tempfile

from src.helpers import (
    add_csv_to_queue,
    create_log_filename,
    create_lockfile,
    get_list_from_str,
    read_full_csv_data,
    read_dois_from_csv,
    write_resolving_host_summary_to_csv,
)


class TestHelperFunctions(unittest.TestCase):
    def test_get_list_from_str(self):
        test_dois = "doi1\ndoi2\ndoi3"

        expected_result = ["doi1", "doi2", "doi3"]

        self.assertEqual(expected_result, get_list_from_str(test_dois))


class TestCreateLockfile(unittest.TestCase):
    def setUp(self):
        # Set up a test filepath
        self.test_filepath = Path("/test/lockfile.lock")

    @patch("pathlib.Path.is_file")
    @patch("builtins.open", new_callable=mock_open)
    def test_create_lockfile_new_file(self, mock_file_open, mock_is_file):
        mock_is_file.return_value = False

        result = create_lockfile(self.test_filepath)

        self.assertTrue(result)
        mock_is_file.assert_called_once()
        mock_file_open.assert_called_once_with(self.test_filepath, "w")

    @patch("pathlib.Path.is_file")
    @patch("builtins.open", new_callable=mock_open)
    def test_create_lockfile_existing_file(self, mock_file_open, mock_is_file):
        mock_is_file.return_value = True

        result = create_lockfile(self.test_filepath)

        self.assertTrue(result)
        mock_is_file.assert_called_once()
        mock_file_open.assert_not_called()

    @patch("pathlib.Path.is_file")
    @patch("builtins.open")
    @patch("builtins.print")
    def test_create_lockfile_permission_error(self, mock_print, mock_file_open, mock_is_file):
        mock_is_file.return_value = False
        mock_file_open.side_effect = PermissionError("Permission denied")

        result = create_lockfile(self.test_filepath)

        self.assertFalse(result)
        mock_is_file.assert_called_once()
        mock_file_open.assert_called_once_with(self.test_filepath, "w")
        mock_print.assert_called_once()
        error_msg = mock_print.call_args[0][0]
        self.assertIn("error creating", error_msg)
        self.assertIn("Permission denied", error_msg)

    @patch("pathlib.Path.is_file")
    @patch("builtins.open")
    @patch("builtins.print")
    def test_create_lockfile_general_exception(self, mock_print, mock_file_open, mock_is_file):
        mock_is_file.return_value = False
        mock_file_open.side_effect = Exception("Some unexpected error")

        result = create_lockfile(self.test_filepath)

        self.assertFalse(result)
        mock_is_file.assert_called_once()
        mock_file_open.assert_called_once_with(self.test_filepath, "w")
        mock_print.assert_called_once()

        error_msg = mock_print.call_args[0][0]
        self.assertIn("error creating", error_msg)
        self.assertIn("Some unexpected error", error_msg)

    @patch("pathlib.Path.is_file")
    def test_create_lockfile_is_file_exception(self, mock_is_file):
        mock_is_file.side_effect = Exception("Path error")

        with patch("builtins.print") as mock_print:
            result = create_lockfile(self.test_filepath)

        self.assertFalse(result)
        mock_is_file.assert_called_once()

        error_msg = mock_print.call_args[0][0]
        self.assertIn("error creating", error_msg)
        self.assertIn("Path error", error_msg)


class TestCSVReaderFunctions(unittest.TestCase):
    def setUp(self):
        self.sample_email = "test@example.com"
        self.sample_host = "example.org"
        self.sample_dois = ["10.1234/test1", "10.1234/test2", "10.1234/test3"]

        self.full_csv_content = f"{self.sample_email}\n{self.sample_host}\n" + "\n".join(self.sample_dois)
        self.dois_only_content = "\n".join(self.sample_dois)

    def test_read_full_csv_data_with_mock(self):
        mock_csv_data = self.full_csv_content

        with patch("builtins.open", mock_open(read_data=mock_csv_data)):
            email, host, dois = read_full_csv_data("dummy_path.csv")

            self.assertEqual(email, self.sample_email)
            self.assertEqual(host, self.sample_host)
            self.assertEqual(dois, self.sample_dois)

    def test_read_dois_from_csv_with_mock(self):
        mock_csv_data = self.dois_only_content

        with patch("builtins.open", mock_open(read_data=mock_csv_data)):
            dois = read_dois_from_csv("dummy_path.csv")

            self.assertEqual(dois, self.sample_dois)

    def test_read_full_csv_data_with_temp_file(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(self.full_csv_content)
            temp_path = temp_file.name

        try:
            email, host, dois = read_full_csv_data(temp_path)

            self.assertEqual(email, self.sample_email)
            self.assertEqual(host, self.sample_host)
            self.assertEqual(dois, self.sample_dois)
        finally:
            os.unlink(temp_path)

    def test_read_dois_from_csv_with_temp_file(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(self.dois_only_content)
            temp_path = temp_file.name

        try:
            dois = read_dois_from_csv(temp_path)

            self.assertEqual(dois, self.sample_dois)
        finally:
            os.unlink(temp_path)

    def test_read_full_csv_data_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            read_full_csv_data("non_existent_file.csv")

    def test_read_dois_from_csv_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            read_dois_from_csv("non_existent_file.csv")

    def test_read_full_csv_data_malformed(self):
        malformed_csv = f"{self.sample_email}"

        with patch("builtins.open", mock_open(read_data=malformed_csv)):
            with self.assertRaises(StopIteration):
                read_full_csv_data("malformed.csv")


class TestCSVWriterFunctions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_log_filename(self):
        with patch("src.helpers.datetime") as mock_datetime, patch("src.helpers.uuid.uuid4") as mock_uuid:
            mock_datetime.now.return_value.strftime.return_value = "2023_01_01_1200"
            mock_uuid.return_value = "test-uuid"

            filename = create_log_filename("test_file")
            expected = "test_file_2023_01_01_1200-test-uuid.csv"
            self.assertEqual(filename, expected)

            filename = create_log_filename("test_file", ext=".txt")
            expected = "test_file_2023_01_01_1200-test-uuid.txt"
            self.assertEqual(filename, expected)

    def test_add_csv_to_queue(self):
        resolver_host = "test.resolver.com"
        email = "test@example.com"
        dois = ["10.1234/test1", "10.1234/test2"]

        with patch("src.helpers.create_log_filename") as mock_create_filename:
            mock_create_filename.return_value = "test_queue_file.csv"

            output_path = add_csv_to_queue(self.temp_path, resolver_host, email, dois)

            self.assertEqual(output_path, self.temp_path / "test_queue_file.csv")

            with open(output_path, mode="r", newline="") as file:
                reader = csv.reader(file)
                rows = list(reader)

                self.assertEqual(rows[0], [email])
                self.assertEqual(rows[1], [resolver_host])
                self.assertEqual(rows[2], [dois[0]])
                self.assertEqual(rows[3], [dois[1]])

    def test_write_resolving_host_summary_to_csv(self):
        resolving_host = "test.resolver.com"
        results = [
            {"doi": "10.1234/test1", "status": "success", "full_metadata": {"message": {"title": "Test1"}}},
            {"doi": "10.1234/test2", "status": "error", "full_metadata": {"message": {"title": "Test2"}}},
        ]

        expected_results = [{"doi": "10.1234/test1", "status": "success"}, {"doi": "10.1234/test2", "status": "error"}]

        with patch("src.helpers.create_log_filename") as mock_create_filename:
            mock_create_filename.return_value = "test_summary.csv"

            output_path = write_resolving_host_summary_to_csv(resolving_host, results, self.temp_path)

            self.assertEqual(output_path, self.temp_path / "test_summary.csv")

            with open(output_path, mode="r", newline="") as file:
                reader = csv.DictReader(file)
                saved_rows = list(reader)

                self.assertEqual(set(reader.fieldnames), set(expected_results[0].keys()))
                self.assertEqual(len(saved_rows), 2)
                self.assertEqual(saved_rows[0]["doi"], expected_results[0]["doi"])
                self.assertEqual(saved_rows[0]["status"], expected_results[0]["status"])
                self.assertEqual(saved_rows[1]["doi"], expected_results[1]["doi"])
                self.assertEqual(saved_rows[1]["status"], expected_results[1]["status"])

    def test_write_with_custom_directories(self):
        directories = {"COMPLETE_DIR": self.temp_path / "complete"}
        os.makedirs(directories["COMPLETE_DIR"], exist_ok=True)

        resolving_host = "test.resolver.com"
        results = [{"doi": "10.1234/test", "status": "success", "full_metadata": {"message": {}}}]

        with patch("src.helpers.create_log_filename") as mock_create_filename:
            mock_create_filename.return_value = "test_custom_dir.csv"

            # Test write_resolving_host_summary_to_csv with custom directories
            output_path = write_resolving_host_summary_to_csv(resolving_host, results, directories=directories)
            expected_path = directories["COMPLETE_DIR"] / "test_custom_dir.csv"
            self.assertEqual(output_path, expected_path)
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
