import os
import time

from dotenv import load_dotenv

import public_ip
from custom_logger import get_logger
from dns import HandlerDNS
from graceful_shutdown import GracefulKiller

logger = get_logger(__name__)

if __name__ == '__main__':
    load_dotenv()
    logger.info("Starting listening to Public IP changes")
    if check_only_mode := "CHECK_ONLY_MODE" in os.environ:
        logger.info("CHECK_ONLY_MODE is enabled")
    dns_handler = HandlerDNS()
    killer = GracefulKiller()
    while not killer.kill_now:
        current_ip = public_ip.get_public_ip()
        previous_ip = public_ip.get_previous_public_ip()
        resolved_ip = public_ip.resolve_dns(os.environ["HOSTNAME"])

        if current_ip == previous_ip == resolved_ip:
            logger.debug("Nothing to update")
            time.sleep(300)
            continue
        # TODO: Resolved IP != Current IP because of proxy
        elif current_ip == resolved_ip != previous_ip:
            logger.warning(
                "DNS resolves correctly but doesn't match saved Public IP."
            )
            public_ip.save_public_ip(public_ip=current_ip)
            time.sleep(300)
            continue

        if not check_only_mode:
            update_success = dns_handler.update_dns_entry(current_ip)
        else:
            logger.info("CHECK_ONLY_MODE: Skipping update")
            update_success = True

        if update_success:
            public_ip.save_public_ip(public_ip=current_ip)
            time.sleep(600)
        else:
            logger.warning("Something bad happened. Waiting 30 minutes")
            time.sleep(1800)

    logger.info("Shutting down.")
