import hashlib
import time

import pytest
from Crypto.PublicKey import RSA

from smile_id_core.signature import Signature


@pytest.fixture()
def key():
    return RSA.generate(2048)


@pytest.fixture()
def signature(key):
    public_key = key.publickey().export_key()
    return Signature("001", public_key)


def test_generate_sec_key(signature):
    timestamp = int(time.time())
    sig_key, sig_timestamp = signature.generate_sec_key(timestamp=timestamp)
    assert sig_timestamp == timestamp

    hashed = hashlib.sha256(
        "{}:{}".format(signature.partner_id, timestamp).encode("utf-8")
    ).hexdigest()
    encrypted, hashed2 = sig_key.split("|")
    assert hashed == hashed2


@pytest.mark.skip("Method currently not implemented")
def test_confirm_sec_key():
    pass
