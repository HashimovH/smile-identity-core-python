import json
from http import HTTPStatus

import requests

from smile_id_core.exceptions import ServerError
from smile_id_core.Signature import Signature


class ApiBase:
    def __init__(self, partner_id: str, api_key: str, server_url: str):
        """
        Initializes a new API instance.

        :param partner_id: A unique number assigned to your account
        :param api_key: A raw API key
        :param server_url: The chosen server URL (see the ``constants.Servers`` class)
        """
        if not partner_id:
            raise ValueError("Parameter 'partner_id' cannot be empty")
        if not api_key:
            raise ValueError("Parameter 'api_key' cannot be empty")
        if not server_url:
            raise ValueError("Parameter 'server_url' cannot be empty")

        self.partner_id = partner_id
        self.api_key = api_key
        self.server_url = server_url

    def _make_request(self, method: str, url: str, data: dict = None, expected_status=(HTTPStatus.OK,)):
        method = method.lower()
        request = getattr(requests, method)
        if method != "get" and data is not None:
            data = json.dumps(data)

        url = url.format(server_url=self.server_url)

        response: requests.Response = request(url, data, headers={
            "Accept": "application/json",
            "Accept-Language": "en_US",
            "Content-type": "application/json",
        })

        if response.status_code not in expected_status:
            raise ServerError(
                f"Failed to {method.upper()} {url}. Server response: {response.status_code} {response.text}"
            )

        return response

    def _get_signature(self):
        sec_key_gen = Signature(self.partner_id, self.api_key)
        return sec_key_gen.generate_sec_key()
