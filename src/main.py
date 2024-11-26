import os
import time

from dotenv import load_dotenv

from custom_logger import get_logger
from dns import HandlerDNS
from graceful_shutdown import GracefulKiller
from mail import MailClient
from public_ip import PublicIPHandler

logger = get_logger(__name__)

if __name__ == '__main__':
    load_dotenv()
    dns_handler = HandlerDNS()
    killer = GracefulKiller()
    ip_client = PublicIPHandler()

    logger.info("Starting listening to Public IP changes")
    if check_only_mode := "CHECK_ONLY_MODE" in os.environ:
        logger.info("CHECK_ONLY_MODE is enabled")

    while not killer.kill_now:
        current_ip = ip_client.get_public_ip()
        previous_ip = ip_client.get_previous_public_ip()
        target_ip = dns_handler.get_target_ip()

        if current_ip == previous_ip == target_ip:
            logger.debug("Nothing to update")
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
            time.sleep(600)
        else:
            mail_client = MailClient()
            mail_client.send_error_mail(current_ip)
            logger.warning("Something bad happened. Waiting 30 minutes")
            time.sleep(1800)

    logger.info("Shutting down.")
