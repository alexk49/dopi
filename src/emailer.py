import argparse
import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from pathlib import Path


def set_emailer_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        "-r",
        "-rec",
        "--recipient",
        type=str,
        help="Email to send email to",
        required=True,
    )
    parser.add_argument(
        "-s",
        "-sub",
        "--subject",
        type=str,
        help="Subject of email.",
        required=True,
    )
    parser.add_argument(
        "-b",
        "-body",
        "--body",
        type=str,
        help="Body of email to send",
        required=True,
    )
    parser.add_argument(
        "-a",
        "-att",
        "--attachment",
        type=str,
        help="Filepath of attachment or email.",
    )
    return parser


class Emailer:
    def __init__(self, sender_email: str, email_password: str):
        self.sender_email = sender_email
        self.email_password = email_password

    def connect_to_smtp_server(self) -> smtplib.SMTP:
        """Establishes connection to SMTP server and returns the server object"""
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(self.sender_email, self.email_password)
        return server

    def create_email_message(self, recipient_email: str, message_subject: str, message_body: str) -> MIMEMultipart:
        """Creates main email message"""
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = recipient_email
        message["Subject"] = message_subject
        message.attach(MIMEText(message_body, "plain"))
        return message

    def add_attachment(self, message: MIMEMultipart, filepath: Path) -> MIMEMultipart:
        with open(filepath, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

            # encode attachment
            encoders.encode_base64(part)

            filename = filepath.name

            # add headers
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
        message.attach(part)
        return message

    def send_email(self, message: MIMEMultipart) -> None:
        """Sends email using external SMTP server with authentication"""
        server = None
        try:
            server = self.connect_to_smtp_server()
            server.send_message(message)
            print("Email sent successfully")
        except Exception as e:
            print(f"Error sending email: {e}")
        finally:
            if server is not None:
                server.quit()


def run_emailer_cli(args):
    EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", "")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD environment variables must be set")
        sys.exit(1)

    mailer = Emailer(EMAIL_ADDRESS, EMAIL_PASSWORD)

    message = mailer.create_email_message(
        recipient_email=args.recipient, message_subject=args.subject, message_body=args.body
    )

    attachment = args.attachment

    if attachment and os.path.exists(attachment):
        message = mailer.add_attachment(message=message, filepath=attachment)

    mailer.send_email(message)


if __name__ == "__main__":
    parser = set_emailer_arg_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    run_emailer_cli(args)
