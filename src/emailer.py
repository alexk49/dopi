import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from pathlib import Path


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

    def send_email(self, message: MIMEMultipart):
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
