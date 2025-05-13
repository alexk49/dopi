import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import csv
import tempfile
import os

from src.submissions import process_csv_file, process_files, process_queue


class TestProcessCSVFile(unittest.TestCase):
    @patch("src.submissions.read_full_csv_data")
    @patch("src.submissions.fetch_dois_data")
    @patch("src.submissions.write_full_metadata_to_csv")
    @patch("src.submissions.write_resolving_host_summary_to_csv")
    @patch("src.submissions.email_summary_csv")
    def test_process_csv_file_success(
        self, mock_email, mock_write_summary, mock_write_metadata, mock_fetch, mock_read_csv
    ):
        test_file = MagicMock(spec=Path)
        test_file.name = "testfile.csv"

        mock_directories = {
            "QUEUE_DIR": Path("/test/queue"),
            "FAILURES_DIR": Path("/test/failures"),
            "COMPLETE_DIR": Path("/test/complete"),
        }

        mock_read_csv.return_value = ("test@example.com", "test.resolver.org", ["10.1234/test1", "10.1234/test2"])
        mock_fetch.return_value = [
            {"doi": "10.1234/test1", "status": "success"},
            {"doi": "10.1234/test2", "status": "error"},
        ]
        mock_write_summary.return_value = Path("/test/complete/results_summary.csv")

        result = process_csv_file(test_file, mock_directories, email_notification=True, full_metadata=True)

        self.assertTrue(result)
        mock_read_csv.assert_called_once_with(test_file)
        mock_fetch.assert_called_once_with(dois=["10.1234/test1", "10.1234/test2"], resolving_host="test.resolver.org")
        mock_write_metadata.assert_called_once_with(mock_fetch.return_value, directories=mock_directories)
        mock_write_summary.assert_called_once_with(
            "test.resolver.org", mock_fetch.return_value, directories=mock_directories
        )
        mock_email.assert_called_once_with(
            recipient="test@example.com", filepath=Path("/test/complete/results_summary.csv")
        )
        test_file.unlink.assert_called_once()

    @patch("src.submissions.read_full_csv_data")
    def test_process_csv_file_failure(self, mock_read_csv):
        test_file = MagicMock(spec=Path)
        test_file.name = "testfile.csv"
        mock_directories = {"FAILURES_DIR": MagicMock(spec=Path)}

        mock_read_csv.side_effect = Exception("Test error")

        result = process_csv_file(test_file, mock_directories)

        self.assertFalse(result)
        test_file.replace.assert_called_once_with(mock_directories["FAILURES_DIR"] / "testfile.csv")


class TestProcessFiles(unittest.TestCase):
    @patch("src.submissions.process_csv_file")
    def test_process_files_with_csv(self, mock_process_csv):
        mock_csv_file = MagicMock(spec=Path)
        mock_csv_file.is_file.return_value = True
        mock_csv_file.suffix = ".csv"

        mock_text_file = MagicMock(spec=Path)
        mock_text_file.is_file.return_value = True
        mock_text_file.suffix = ".txt"
        mock_text_file.name = "test.txt"

        files = [mock_csv_file, mock_text_file]
        mock_directories = {"FAILURES_DIR": MagicMock(spec=Path)}

        mock_process_csv.return_value = True

        process_files(files, mock_directories)

        mock_process_csv.assert_called_once_with(mock_csv_file, mock_directories)
        mock_text_file.replace.assert_called_once_with(mock_directories["FAILURES_DIR"] / "test.txt")


class TestProcessQueue(unittest.TestCase):
    @patch("src.submissions.create_lockfile")
    @patch("src.submissions.process_files")
    def test_process_queue_no_files(self, mock_process_files, mock_create_lockfile):
        mock_create_lockfile.return_value = True
        mock_lock_file = MagicMock(spec=Path)
        mock_directories = {"QUEUE_DIR": MagicMock(spec=Path)}

        mock_directories["QUEUE_DIR"].iterdir.return_value = []

        process_queue(lock_filepath=mock_lock_file, directories=mock_directories)

        mock_process_files.assert_not_called()
        mock_lock_file.unlink.assert_called_once_with(missing_ok=True)

    @patch("src.submissions.create_lockfile")
    @patch("src.submissions.process_files")
    def test_process_queue_with_files(self, mock_process_files, mock_create_lockfile):
        mock_create_lockfile.return_value = True
        mock_lock_file = MagicMock(spec=Path)

        mock_file1 = MagicMock(spec=Path)
        mock_file2 = MagicMock(spec=Path)

        mock_directories = {"QUEUE_DIR": MagicMock(spec=Path)}

        mock_directories["QUEUE_DIR"].iterdir.side_effect = [
            [mock_file1, mock_file2],  # First call returns files
            [],  # Second call returns empty list to exit loop
        ]

        with patch("src.submissions.sorted", side_effect=lambda x: x):
            process_queue(lock_filepath=mock_lock_file, directories=mock_directories)

        mock_process_files.assert_called_once_with([mock_file1, mock_file2], mock_directories)
        mock_lock_file.unlink.assert_called_once_with(missing_ok=True)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

        self.queue_dir = self.base_path / "queue"
        self.failures_dir = self.base_path / "failures"
        self.complete_dir = self.base_path / "complete"

        os.makedirs(self.queue_dir)
        os.makedirs(self.failures_dir)
        os.makedirs(self.complete_dir)

        self.directories = {
            "QUEUE_DIR": self.queue_dir,
            "FAILURES_DIR": self.failures_dir,
            "COMPLETE_DIR": self.complete_dir,
        }

        self.test_csv_path = self.queue_dir / "test_input.csv"
        with open(self.test_csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["test@example.com"])
            writer.writerow(["test.resolver.org"])
            writer.writerow(["10.1234/test1"])
            writer.writerow(["10.1234/test2"])

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("src.submissions.fetch_dois_data")
    @patch("src.submissions.email_summary_csv")
    def test_integration_process_csv_file(self, mock_email, mock_fetch):
        mock_fetch.return_value = [
            {"doi": "10.1234/test1", "status": "success", "full_metadata": {"message": {"title": "Test1"}}},
            {"doi": "10.1234/test2", "status": "error", "full_metadata": {"message": {"title": "Test2"}}},
        ]

        result = process_csv_file(self.test_csv_path, self.directories, email_notification=False)

        self.assertTrue(result)

        self.assertFalse(self.test_csv_path.exists())

        csv_files = list(self.complete_dir.glob("*.csv"))
        self.assertEqual(len(csv_files), 1)


if __name__ == "__main__":
    unittest.main()
