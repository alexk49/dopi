import json
import unittest
from unittest.mock import MagicMock, patch
from src.app import app
from webtest import TestApp


class BottleAppTestCase(unittest.TestCase):
    def setUp(self):
        self.test_app = TestApp(app)

    def test_home(self):
        res = self.test_app.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "text/html")
        assert "<h1>dopi</h1>" in res.text

    def test_script_js(self):
        res = self.test_app.get("/static/scripts.js")
        self.assertEqual(res.status_code, 200)

    def test_styles_css(self):
        res = self.test_app.get("/static/styles.css")
        self.assertEqual(res.status_code, 200)

    @patch("src.app.Config.directories")
    @patch("src.app.static_file")
    def test_download_complete_file_route(self, mock_static_file, mock_directories):
        mock_complete_dir = "/fake/complete/dir"
        mock_directories.__getitem__.return_value = mock_complete_dir

        mock_static_file.return_value = "fake file response"

        res = self.test_app.get("/complete/somefile.csv")

        self.assertEqual(res.status_code, 200)
        self.assertIn("fake file response", res.text)

        mock_static_file.assert_called_once_with(
            "somefile.csv",
            root=mock_complete_dir,
            download="somefile.csv",
        )

    """ API routes """

    @patch("src.app.Config.directories")
    def test_queue_count_res(self, mock_directories):
        mock_queue_dir = MagicMock()
        mock_queue_dir.glob.return_value = ["fake.csv", "fake2.csv"]
        mock_directories.__getitem__.return_value = mock_queue_dir
        res = self.test_app.get("/queue")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "application/json")
        assert "queue_count" in res.text

        res_dict = json.loads(res.text)
        self.assertEqual(res_dict["queue_count"], "2")

    @patch("src.app.Config.directories")
    def test_completed_files_route(self, mock_directories):
        mock_complete_dir = MagicMock()

        mock_file1 = MagicMock()
        mock_file1.name = "complete.csv"

        mock_file2 = MagicMock()
        mock_file2.name = "complete2.csv"

        mock_complete_dir.glob.return_value = [mock_file1, mock_file2]
        mock_directories.__getitem__.return_value = mock_complete_dir
        res = self.test_app.get("/completed")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "application/json")

        assert "completed" in res.text
        res_dict = json.loads(res.text)
        self.assertEqual(res_dict["completed"], ["complete.csv", "complete2.csv"])


class SubmitFormTestCase(unittest.TestCase):
    def setUp(self):
        self.test_app = TestApp(app)

    @patch("src.app.start_queue")
    @patch("src.app.Config")
    @patch("src.app.add_csv_to_queue")
    @patch("src.app.get_errors")
    @patch("src.app.validate_form")
    def test_submit_successful(
        self, mock_validate_form, mock_get_errors, mock_add_csv_to_queue, mock_config, mock_start_queue
    ):
        mock_validate_form.return_value = {
            "resolver": {"value": "resolver_host"},
            "email": {"value": "test@example.com"},
            "dois": {"value": "10.1000/xyz123"},
        }
        mock_get_errors.return_value = {}
        mock_add_csv_to_queue.return_value = "/fake/path/to/queued_file.csv"
        mock_config.directories = {"QUEUE_DIR": "/fake/queue/dir"}

        mock_lock_path = MagicMock()
        mock_lock_path.is_file.return_value = False
        mock_config.LOCK_FILEPATH = mock_lock_path

        res = self.test_app.post(
            "/submit", params={"resolver": "resolver_host", "email": "test@example.com", "dois": "10.1000/xyz123"}
        )

        self.assertEqual(res.status_code, 200)
        res_dict = res.json

        self.assertTrue(res_dict["success"])
        self.assertIn("Thank you", res_dict["message"])
        self.assertEqual(res_dict["errors"], {})

        mock_validate_form.assert_called_once()
        mock_get_errors.assert_called_once()
        mock_add_csv_to_queue.assert_called_once()
        mock_start_queue.assert_called_once()

    @patch("src.app.start_queue")
    @patch("src.app.Config")
    @patch("src.app.add_csv_to_queue")
    @patch("src.app.get_errors")
    @patch("src.app.validate_form")
    def test_submit_with_errors(
        self, mock_validate_form, mock_get_errors, mock_add_csv_to_queue, mock_config, mock_start_queue
    ):
        mock_validate_form.return_value = {}
        mock_get_errors.return_value = {"email": "Email is required"}

        res = self.test_app.post("/submit", params={"resolver": "", "email": "", "dois": ""}, expect_errors=True)

        self.assertEqual(res.status_code, 400)
        res_dict = res.json

        self.assertFalse(res_dict["success"])
        self.assertIn("Invalid form", res_dict["message"])
        self.assertIn("email", res_dict["errors"])

        mock_validate_form.assert_called_once()
        mock_get_errors.assert_called_once()
        mock_add_csv_to_queue.assert_not_called()
        mock_start_queue.assert_not_called()


if __name__ == "__main__":
    unittest.main()
