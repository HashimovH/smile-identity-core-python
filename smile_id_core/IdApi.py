import json
from smile_id_core.Signature import Signature
from smile_id_core.Utilities import Utilities
from smile_id_core.exceptions import ServerError
import requests

__all__ = ["IdApi"]


class IdApi:
    def submit_job(self, partner_params, id_params, use_validation_api=True):
        Utilities.validate_partner_params(partner_params)

        if not id_params:
            raise ValueError("Please ensure that you send through ID Information")

        Utilities.validate_id_params(
            self.url, id_params, partner_params, use_validation_api
        )

        if partner_params.get("job_type") != 5:
            raise ValueError(
                "Please ensure that you are setting your job_type to 5 to query ID Api"
            )

        sec_key_object = self.__get_sec_key()
        payload = self.__configure_json(
            partner_params,
            id_params,
            sec_key_object["sec_key"],
            sec_key_object["timestamp"],
        )
        response = self.__execute_http(payload)
        if response.status_code != 200:
            raise ServerError(
                "Failed to post entity to {}, status={}, response={}".format(
                    self.url + "/id_verification", response.status_code, response.json()
                )
            )
        return response

    def __configure_json(self, partner_params, id_params, sec_key, timestamp):
        payload = {
            "sec_key": sec_key,
            "timestamp": timestamp,
            "partner_id": self.partner_id,
            "partner_params": partner_params,
        }
        payload.update(id_params)
        return payload

    def __execute_http(self, payload):
        data = json.dumps(payload)
        resp = requests.post(
            url=self.url + "/id_verification",
            data=data,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
                "Content-type": "application/json",
            },
        )
        return resp
