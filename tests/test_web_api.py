from unittest.mock import patch, Mock

import pytest
import requests

from smile_id_core import WebApiTest, signature
from smile_id_core.constants import StatusCodes
from smile_id_core.exceptions import InvalidDataFormat, VerificationFailed


class FakeResponse:
    def __init__(self, text="", data=None, status_code=200):
        self.status_code = status_code
        self.text = text
        self.data = data

    def json(self):
        if self.data is None:
            raise ValueError("No JSON")
        return self.data


@pytest.fixture()
def api():
    with patch.object(signature, "RSA") as patched_rsa:
        with patch.object(signature, "PKCS1_v1_5") as patched_crypto:
            patched_rsa.importKey.return_value = "key"
            patched_crypto.new().encrypt = Mock(return_value=b"encrypted")

            yield WebApiTest("001", "key")


def test_make_request():
    with patch.object(requests, "get") as requests_get:
        requests_get.return_value = FakeResponse(data={})

        assert WebApiTest.get_services() == {}


def test_verify_document_failure_raises(api):
    with patch.object(requests, "post") as requests_post:
        requests_post.return_value = FakeResponse(data={"ResultText": "error"})

        with pytest.raises(VerificationFailed) as e:
            api.verify_document("country", "id_type", "id_number")

        assert e.value.message == "error"


def test_verify_document_success(api):
    with patch.object(requests, "post") as requests_post:
        requests_post.return_value = FakeResponse(
            data={"ResultText": "success", "ResultCode": StatusCodes.SUCCESS}
        )

        response = api.verify_document("country", "id_type", "id_number")

        assert response["ResultText"] == "success"


def test_validation_success():
    data = {"country": "GH", "id_type": "DRIVERS_LICENSE", "id_number": "test"}
    assert WebApiTest.validate_id_params(data) == data

    data = {
        "country": "NG",
        "id_type": "DRIVERS_LICENSE",
        "id_number": "test",
        "first_name": "test",
        "last_name": "test",
        "dob": "2020-01-02",
    }
    assert WebApiTest.validate_id_params(data) == data


def test_validation_failure():
    data = {}
    with pytest.raises(InvalidDataFormat) as e:
        WebApiTest.validate_id_params(data)
        assert e.match("field `country` is required")

    data = {"country": "XX", "id_type": "DRIVERS_LICENSE", "id_number": "test"}
    with pytest.raises(InvalidDataFormat) as e:
        WebApiTest.validate_id_params(data)
        assert e.match("Country 'XX' is not supported")

    data = {"country": "NG", "id_type": "UNKNOWN", "id_number": "test"}
    with pytest.raises(InvalidDataFormat) as e:
        WebApiTest.validate_id_params(data)
        assert e.match(f"Country 'NG' does not support document type 'UNKNOWN'")

    data = {
        "country": "NG",
        "id_type": "DRIVERS_LICENSE",
        "id_number": "test",
    }
    with pytest.raises(InvalidDataFormat) as e:
        WebApiTest.validate_id_params(data)
        assert e.match("fields are missing or empty: [dob,first_name,last_name]")
