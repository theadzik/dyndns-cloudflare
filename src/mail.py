import os
import smtplib
from email.message import EmailMessage

from jinja2 import Template

from custom_logger import get_logger

logger = get_logger(__name__)


class MailClient:
    PRODUCT_NAME = "DynDNS-Cloudflare"

    def __init__(self, hostname: str, detected_ip: str, success: bool):
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", 465))
        self.notification_email = os.getenv("NOTIFICATION_EMAIL", "")
        self.notification_on_success = os.getenv("NOTIFICATION_ON_SUCCESS", "False")

        self.hostname = hostname
        self.detected_ip = detected_ip
        self.success = success

        self.emails_enabled = all([
            self.smtp_username,
            self.smtp_password,
            self.smtp_host,
            self.smtp_port,
            self.notification_email
        ])

    def check_should_send(self) -> bool:
        truthy_strings = ["true", "yes", "enabled"]
        should_send = (
                self.emails_enabled and
                ((self.notification_on_success.lower() in truthy_strings) or not self.success)
        )

        return should_send

    def _get_email_message(self) -> EmailMessage:
        message = self._get_email_base()
        message['Subject'] = self._get_email_subject()
        email_body = self._get_email_body()
        message.set_content(email_body, subtype="html")

        return message

    def _get_email_body(self) -> str:
        email_vars = {
            "detected_ip": self.detected_ip,
            "success": self.success,
            "host_name": self.hostname,
            "product_name": self.PRODUCT_NAME
        }
        script_dir = os.path.dirname(__file__)
        rel_path = "templates/email_template.html"
        abs_file_path = os.path.join(script_dir, rel_path)
        with open(abs_file_path, mode="r") as template_file:
            email_template = template_file.read()

        body = Template(email_template).render(email_vars)
        return body

    def _get_email_subject(self):
        if self.success:
            return f"[{self.PRODUCT_NAME}] Your new public IP is {self.detected_ip}"
        else:
            return f"[{self.PRODUCT_NAME}] Could not update your DNS records {self.detected_ip}"

    def _get_email_base(self) -> EmailMessage:
        message = EmailMessage()
        message['From'] = self.smtp_username
        message['To'] = self.notification_email

        return message

    def send_email(self) -> None:
        if not self.check_should_send():
            logger.debug("Skipping send.")
            return None

        message = self._get_email_message()

        mailer = smtplib.SMTP_SSL(host=self.smtp_host, port=self.smtp_port)
        mailer.login(user=self.smtp_username, password=self.smtp_password)
        mailer.send_message(msg=message)

        logger.info(f"Sent an email to {message['To']}")
