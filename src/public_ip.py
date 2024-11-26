import os
import queue
import socket
import time

import requests

from custom_logger import get_logger

logger = get_logger(__name__)


class PublicIPHandler:
    def __init__(self):
        self.log_path = os.getenv("LOG_PATH", "/history/public_ip_history")
        self.MAX_BACKOFF_TIME = 300
        self.resolvers_queue = queue.SimpleQueue()
        remote_ip_detection_hosts = [
            "https://ifconfig.me",
            "https://ipinfo.io/ip",
            "https://ipecho.net/plain",
            "http://ip1.dynupdate.no-ip.com",
        ]
        for resolver in remote_ip_detection_hosts:
            self.resolvers_queue.put_nowait(resolver)

    def get_public_ip(self, max_retries: int = 4) -> str:
        for idx in range(max_retries):
            ip_url = self.resolvers_queue.get()
            logger.debug(f"Requesting IP from {ip_url}")
            try:
                public_ip = requests.request("GET", ip_url)
                public_ip.raise_for_status()
                logger.debug(f"Current Public IP: {public_ip.text}")
                return public_ip.text
            except requests.HTTPError:
                logger.warning(
                    f"Failed do get IP from {ip_url}.\n"
                    f"  Status code: {public_ip.status_code}\n"
                    f"  Response: {public_ip.text}"
                )
            except requests.exceptions.ConnectionError:
                logger.warning(
                    f"Failed do get IP from {ip_url}.\n"
                    f"  No internet connection?"
                )
                if idx < max_retries - 1:
                    sleep_time = min(self.MAX_BACKOFF_TIME, 10 ** (idx + 1))  # 10, 100, 300, 300...
                    logger.debug(
                        f"Waiting for {sleep_time} seconds."
                    )
                    time.sleep(sleep_time)
            except Exception as e:
                logger.error(
                    f"Failed do get IP from {ip_url}.\n"
                    f"{e}"
                )
            finally:
                self.resolvers_queue.put_nowait(ip_url)
        else:
            raise Exception(f"Failed to get public IP after {max_retries} retries.")

    def save_public_ip(self, ip_address: str) -> None:
        with open(self.log_path, "a") as ip_log:
            ip_log.write(ip_address + "\n")
        logger.info(f"Saved {ip_address} IP to the history file")

    def get_previous_public_ip(self) -> str:
        try:
            with open(self.log_path, "r") as ip_log:
                previous_ip = list(ip_log)[-1].strip()
                logger.debug(f"Previous IP: {previous_ip}")
                return previous_ip
        except FileNotFoundError:
            logger.info("No previous IP found.")
            return ""

    @staticmethod
    def resolve_dns(hostname: str) -> str:
        resolved_ip = socket.gethostbyname(hostname)
        logger.debug(f"{hostname} resolved to {resolved_ip}.")
        return resolved_ip
