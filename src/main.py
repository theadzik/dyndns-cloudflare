import os
import time

from dotenv import load_dotenv

from custom_logger import get_logger
from dns import HandlerDNS
from mail import MailClient
from public_ip import PublicIPHandler

load_dotenv()
logger = get_logger(__name__)

if __name__ == '__main__':
    dns_handler = HandlerDNS()
    ip_client = PublicIPHandler()

    logger.info("Starting listening to Public IP changes")
    if check_only_mode := "CHECK_ONLY_MODE" in os.environ:
        logger.info("CHECK_ONLY_MODE is enabled")

    while True:
        current_ip = ip_client.get_public_ip()
        previous_ip = ip_client.get_previous_public_ip()
        target_ip = dns_handler.get_target_ip()

        if current_ip == previous_ip == target_ip:
            logger.debug("Nothing to update")
            time.sleep(60)
            continue
        elif (current_ip == previous_ip) and check_only_mode:
            logger.debug("Check only mode. Your Public IP was already saved.")
            time.sleep(60)
            continue
        elif current_ip == target_ip != previous_ip:
            logger.info(
                "DNS Record is set correctly. Saving public IP."
            )
            ip_client.save_public_ip(ip_address=current_ip)
            time.sleep(60)
            continue

        if not check_only_mode:
            update_success = dns_handler.update_record_with_retry(ip_address=current_ip)
        else:
            logger.info("CHECK_ONLY_MODE: Skipping update")
            update_success = True

        if update_success:
            ip_client.save_public_ip(ip_address=current_ip)

        if not check_only_mode:
            mail_client = MailClient(hostname=os.environ["HOSTNAME"], detected_ip=current_ip, success=update_success)
            mail_client.send_email()

        time.sleep(60)

    logger.info("Shutting down.")
