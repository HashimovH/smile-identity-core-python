import json
from http import HTTPStatus

import requests

from smile_id_core.exceptions import ServerError
from smile_id_core.signature import Signature


class ApiBase:
    SERVER_URL: str
    """This can be one of `constants.Servers` entries"""

    def __init__(self, partner_id: str, api_key: str):
        """
        Initializes a new API instance.

        :param partner_id: A unique number assigned to your account, as a 3-digit string, eg. "123"
        :param api_key: A raw API key
        """
        if not partner_id:
            raise ValueError("Parameter 'partner_id' cannot be empty")
        if not api_key:
            raise ValueError("Parameter 'api_key' cannot be empty")
        try:
            int(partner_id)
        except (TypeError, ValueError) as e:
            raise ValueError("Parameter 'partner_id' must be a numeric string") from e

        self.partner_id = partner_id
        self.signature = Signature(partner_id=partner_id, api_key=api_key)

    @classmethod
    def _make_request(
        cls, method: str, url: str, data: dict = None, expected_status=(HTTPStatus.OK,)
    ):
        method = method.lower()
        request = getattr(requests, method)
        if method != "get" and data is not None:
            data = json.dumps(data)

        url = url.format(server_url=cls.SERVER_URL, api_version=1)

        response: requests.Response = request(
            url,
            data,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
                "Content-type": "application/json",
            },
        )

        if response.status_code not in expected_status:
            raise ServerError(
                f"Failed to {method.upper()} {url}. Server response: {response.status_code} {response.text}"
            )

        try:
            data = response.json()
        except ValueError:
            raise ServerError(
                f"Failed to parse server response from {method.upper()} {url}: {response.status_code} {response.text}"
            )

        return data

    @classmethod
    def _make_request_async(
            cls, method: str, url: str, data: dict = None, expected_status=(HTTPStatus.OK,)
    ):
        method = method.lower()
        request = getattr(requests, method)
        if method != "get" and data is not None:
            data = json.dumps(data)

        url = url.format(server_url=cls.SERVER_URL, api_version=2)

        response: requests.Response = request(
            url,
            data,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
                "Content-type": "application/json",
            },
        )

        if response.status_code not in expected_status:
            raise ServerError(
                f"Failed to {method.upper()} {url}. Server response: {response.status_code} {response.text}"
            )

        try:
            data = response.json()
        except ValueError:
            raise ServerError(
                f"Failed to parse server response from {method.upper()} {url}: {response.status_code} {response.text}"
            )

        return data

    def _get_signature(self):
        return self.signature.generate_sec_key()
