import os
import platform
import time

import requests

from custom_logger import get_logger

logger = get_logger(__name__)


class HandlerDNS:
    BASE_URL = "https://api.cloudflare.com/client/v4"
    MAX_BACKOFF_TIME = 300

    def __init__(self):
        self.APP_VERSION = os.environ['APP_VERSION']
        self.HOSTNAME = os.environ["HOSTNAME"]
        self.API_TOKEN = os.environ["API_TOKEN"]

        self.zone_id = self.get_zone_id()
        self.record = self.get_record()

        self.record_id = self.get_record_id()
        self.target_ip = self.get_target_ip()

    def get_headers(self) -> dict:
        headers = {
            "User-Agent": f"theadzik/dyndns-cloudflare"
                          f"{platform.system()}{platform.release()}"
                          f"-{self.APP_VERSION}"
                          f" adam@zmuda.pro",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_TOKEN}"
        }
        return headers

    def get_zone_id(self) -> str:
        url = f"{self.BASE_URL}/zones"
        logger.debug("Getting Zone ID.")
        response = requests.get(url, headers=self.get_headers())
        zone_id = [zone["id"] for zone in response.json()["result"] if zone["name"] == self.HOSTNAME][0]
        return zone_id

    def get_record(self) -> dict:
        logger.debug("Getting Record.")
        url = f"{self.BASE_URL}/zones/{self.zone_id}/dns_records"
        response = requests.get(url, headers=self.get_headers())
        return [record for record in response.json()["result"] if record["name"] == self.HOSTNAME][0]

    def get_record_id(self) -> str:
        logger.debug("Getting Record ID.")
        return self.record["id"]

    def get_target_ip(self) -> str:
        logger.debug("Getting target IP.")
        return self.record["content"]

    def update_record(self, ip_address: str) -> bool:
        update_url = f"{self.BASE_URL}/zones/{self.zone_id}/dns_records/{self.record_id}"

        data = {
            "name": f"{self.HOSTNAME}",
            "content": f"{ip_address}",
            "type": "A"
        }

        logger.debug("Updating record.")
        response = requests.patch(
            url=update_url,
            json=data,
            headers=self.get_headers(),
        )

        self.record = response.json()["result"]

        result = self.handle_response(response)
        return result

    def update_record_with_retry(self, ip_address: str, retry_count: int = 3):
        for idx in range(retry_count):
            if self.update_record(ip_address=ip_address):
                return True
            else:
                sleep_time = min(self.MAX_BACKOFF_TIME, 10 ** (idx + 1))  # 10, 100, 300, 300...
                logger.debug(
                    f"Waiting for {sleep_time} seconds."
                )
                time.sleep(sleep_time)
        return False

    @staticmethod
    def handle_response(response: requests.Response) -> bool:
        response_body = response.json()
        try:
            response.raise_for_status()
            logger.info("Updated DNS record.")
            if response_body["messages"]:
                logger.info(f"  Messages: {response_body['messages']}")
            return True
        except requests.HTTPError as e:
            logger.error(
                "Failed to update DNS record:\n"
                f"  Status code: {response.status_code}\n"
                f"  Errors: {response_body['errors']}"
                f"  Messages: {response_body['messages']}"
            )
            logger.exception(e)
            return False
