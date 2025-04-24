import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from email.mime.multipart import MIMEMultipart

from src.emailer import Emailer


class TestEmailer(unittest.TestCase):
    def setUp(self):
        self.emailer = Emailer("test@example.com", "password123")
        self.recipient = "recipient@example.com"
        self.subject = "Test Subject"
        self.body = "Test Body"

    @patch("smtplib.SMTP")
    def test_connect_to_smtp_server(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        server = self.emailer.connect_to_smtp_server()

        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "password123")
        self.assertEqual(server, mock_server)

    def test_create_email_message(self):
        message = self.emailer.create_email_message(self.recipient, self.subject, self.body)

        self.assertIsInstance(message, MIMEMultipart)
        self.assertEqual(message["From"], "test@example.com")
        self.assertEqual(message["To"], self.recipient)
        self.assertEqual(message["Subject"], self.subject)

        self.assertEqual(len(message.get_payload()), 1)

    @patch("builtins.open", new_callable=mock_open, read_data=b"test file content")
    @patch("email.encoders.encode_base64")
    def test_add_attachment(self, mock_encode_base64, mock_file):
        message = MIMEMultipart()
        filepath = Path("test_file.txt")

        result = self.emailer.add_attachment(message, filepath)

        mock_file.assert_called_once_with(filepath, "rb")
        mock_encode_base64.assert_called_once()
        self.assertEqual(len(result.get_payload()), 1)
        attachment = result.get_payload()[0]
        self.assertIn("filename= test_file.txt", attachment["Content-Disposition"])

    @patch("src.emailer.Emailer.connect_to_smtp_server")
    def test_send_email_success(self, mock_connect):
        mock_server = MagicMock()
        mock_connect.return_value = mock_server
        message = MIMEMultipart()

        with patch("builtins.print") as mock_print:
            self.emailer.send_email(message)

        mock_connect.assert_called_once()
        mock_server.send_message.assert_called_once_with(message)
        mock_server.quit.assert_called_once()
        mock_print.assert_called_once_with("Email sent successfully")

    @patch("src.emailer.Emailer.connect_to_smtp_server")
    def test_send_email_exception(self, mock_connect):
        mock_server = MagicMock()
        mock_connect.return_value = mock_server
        mock_server.send_message.side_effect = Exception("Test error")
        message = MIMEMultipart()

        with patch("builtins.print") as mock_print:
            self.emailer.send_email(message)

        mock_connect.assert_called_once()
        mock_server.send_message.assert_called_once_with(message)
        mock_server.quit.assert_called_once()
        mock_print.assert_called_once_with("Error sending email: Test error")


if __name__ == "__main__":
    unittest.main()
