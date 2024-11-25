import logging
import os
import platform
import re
import signal

import requests


class HandlerDNS:
    BASE_URL = "https://api.cloudflare.com/client/v4"
    APP_VERSION = os.environ['APP_VERSION']
    HOSTNAME = os.environ["HOSTNAME"]
    API_TOKEN = os.environ["API_TOKEN"]

    def __init__(self):
        pass

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

    def update_dns_entry(self, zone_id: str, dns_record_id: str, ip_address: str) -> bool:
        update_url = f"{self.BASE_URL}/zones/{zone_id}/dns_records/{dns_record_id}"

        data = {
            "name": f"{self.HOSTNAME}",
            "proxied": True,
            "ttl": 60,
            "content": f"{ip_address}",
            "type": "A"
        }

        update = requests.put(
            url=update_url,
            data=data,
            headers=self.get_headers(),
        )

        result = self.handle_response(update)
        return result

    @staticmethod
    def handle_response(response: requests.Response) -> bool:
        # https://www.noip.com/integrate/response
        if re.match(r"good.*", response.text):
            logging.info(f"Updated DNS. [{response.status_code}] {response.text}")
            return True
        elif re.match(r"nochg.*", response.text):
            logging.warning(f"No changes. [{response.status_code}] {response.text}")
            return True
        elif re.match(r"nohost|badauth|badagent|!donator|abuse", response.text):
            logging.critical(f"Failed to update DNS: [{response.status_code}] {response.text}")
            logging.warning("Waiting indefinitely.")
            signal.pause()
        elif re.match(r"911", response.text):
            logging.warning(f"Failed to update DNS: [{response.status_code}] {response.text}")
        else:
            logging.error(f"Did not understand response: [{response.status_code}] {response.text}")
        return False
