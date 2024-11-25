import os
import smtplib
from email.message import EmailMessage

from custom_logger import get_logger

logger = get_logger(__name__)


class EmailClient:
    def __init__(self):
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", 465))
        self.notification_email = os.getenv("NOTIFICATION_EMAIL", "")

        self.emails_enabled = all([
            self.smtp_username,
            self.smtp_password,
            self.smtp_host,
            self.smtp_port,
            self.notification_email
        ])

    @staticmethod
    def generate_email_body(detected_ip: str, status_code: int, api_response_body: str) -> str:
        body = (
            f"Your new Public IP address is: {detected_ip}.\n"
            f"Failed to update your DNS entries.\n"
            f"A response from the Cloudflare API: [{status_code}] {api_response_body}"
        )

        return body

    def send_error_email(self, body: str):
        message = EmailMessage()
        message.set_content(body)
        message['Subject'] = "[DynDNS-Cloudflare] Failed to update IP for DNS"
        message['From'] = self.smtp_username
        message['To'] = self.notification_email

        mailer = smtplib.SMTP_SSL(host=self.smtp_host, port=self.smtp_port)
        mailer.login(user=self.smtp_username, password=self.smtp_password)
        mailer.send_message(msg=message)
        logger.info(f"Sent an error email to {message['To']}")
