import os
import platform

import requests

from custom_logger import get_logger

logger = get_logger(__name__)


class HandlerDNS:
    BASE_URL = "https://api.cloudflare.com/client/v4"

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
        response = requests.get(url, headers=self.get_headers())
        zone_id = [zone["id"] for zone in response.json()["result"] if zone["name"] == self.HOSTNAME][0]
        return zone_id

    def get_record(self) -> dict:
        url = f"{self.BASE_URL}/zones/{self.zone_id}/dns_records"
        response = requests.get(url, headers=self.get_headers())
        return [record for record in response.json()["result"] if record["name"] == self.HOSTNAME][0]

    def get_record_id(self) -> str:
        return self.record["id"]

    def get_target_ip(self) -> str:
        return self.record["content"]

    def update_record(self, ip_address: str) -> bool:
        update_url = f"{self.BASE_URL}/zones/{self.zone_id}/dns_records/{self.record_id}"

        data = {
            "name": f"{self.HOSTNAME}",
            "content": f"{ip_address}",
            "type": "A"
        }

        response = requests.patch(
            url=update_url,
            json=data,
            headers=self.get_headers(),
        )

        self.record = response.json()["result"]

        result = self.handle_response(response)
        return result

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
