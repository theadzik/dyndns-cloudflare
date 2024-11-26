import os
import smtplib
from email.message import EmailMessage

from custom_logger import get_logger

logger = get_logger(__name__)


class MailClient:
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
    def generate_mail_body(detected_ip: str) -> str:
        body = (
            f"Your IP address has changed but we failed to update your DNS records.\n\n"
            f"Your new Public IP address is: {detected_ip}."
        )

        return body

    def send_error_mail(self, detected_ip: str):
        mail_body = self.generate_mail_body(detected_ip)

        message = EmailMessage()
        message.set_content(mail_body)
        message['Subject'] = "[DynDNS-Cloudflare] Failed to update IP for DNS"
        message['From'] = self.smtp_username
        message['To'] = self.notification_email

        mailer = smtplib.SMTP_SSL(host=self.smtp_host, port=self.smtp_port)
        mailer.login(user=self.smtp_username, password=self.smtp_password)
        mailer.send_message(msg=message)
        logger.info(f"Sent an error email to {message['To']}")
