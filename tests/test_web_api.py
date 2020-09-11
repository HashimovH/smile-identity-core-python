from unittest.mock import patch

import requests

from smile_id_core import WebApiTest


class FakeResponse:
    def __init__(self, text="", data=None, status_code=200):
        self.status_code = status_code
        self.text = text
        self.data = data

    def json(self):
        if self.data is None:
            raise ValueError("No JSON")
        return self.data


def test_make_request():
    with patch.object(requests, "get") as requests_get:
        requests_get.return_value = FakeResponse(data={})

        assert WebApiTest.get_services() == {}
