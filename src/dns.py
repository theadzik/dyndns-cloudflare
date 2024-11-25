import logging
import os
import platform
import re
import signal
import smtplib
from base64 import b64encode
from email.message import EmailMessage

import requests


class HandlerDNS:
    def __init__(self, public_ip: str):
        self.username = os.environ["NOIP_USERNAME"]
        self.password = os.environ["NOIP_PASSWORD"]
        self.hostname = os.environ["HOSTNAME"]
        self.public_ip = public_ip
        self.update_url = (
            "https://dynupdate.no-ip.com/nic/update"
            f"?hostname={self.hostname}"
            f"&myip={self.public_ip}"
        )

    def get_headers(self) -> dict:
        # encode -> encode -> decode to get string -> bytes -> base64 bytes -> base64 string
        basic_auth = b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers = {
            "Authorization": f"Basic {basic_auth}",
            "User-Agent": f"theadzik/dyndns-noip"
                          f"{platform.system()}{platform.release()}"
                          f"-{os.environ['APP_VERSION']}"
                          f" adam@zmuda.pro"
        }
        return headers

    def update_dns_entry(self) -> bool:
        update = requests.request(
            method="GET",
            url=self.update_url,
            headers=self.get_headers()
        )

        result = self.handle_response(update)
        return result

    def handle_response(self, response: requests.Response) -> bool:
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
