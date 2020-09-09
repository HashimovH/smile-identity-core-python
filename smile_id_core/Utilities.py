import json
import zipfile
import io
import os

import requests

from smile_id_core.Signature import Signature
from smile_id_core.exceptions import ServerError

__all__ = ["Utilities"]


class Utilities:

    @staticmethod
    def validate_partner_params(partner_params):
        if not partner_params:
            raise ValueError("Please ensure that you send through partner params")

        if (
            not partner_params["user_id"]
            or not partner_params["job_id"]
            or not partner_params["job_type"]
        ):
            raise ValueError("Partner Parameter Arguments may not be null or empty")

        if not isinstance(partner_params["user_id"], str):
            raise ValueError("Please ensure user_id is a string")

        if not isinstance(partner_params["job_id"], str):
            raise ValueError("Please ensure job_id is a string")

        if not isinstance(partner_params["job_id"], str):
            raise ValueError("Please ensure job_id is a string")

        if not isinstance(partner_params["job_type"], int):
            raise ValueError("Please ensure job_id is a number")

    @staticmethod
    def validate_id_params(
        sid_server, id_info_params, partner_params, use_validation_api=True
    ):
        if not id_info_params["entered"]:
            return

        for field in ["country", "id_type", "id_number"]:
            if field in id_info_params:
                if id_info_params[field]:
                    continue
                else:
                    raise ValueError("key " + field + " cannot be empty")
            else:
                raise ValueError("key " + field + " cannot be empty")
        if not use_validation_api:
            return

        response = Utilities.get_smile_id_services(sid_server)
        if response.status_code != 200:
            raise ServerError(
                "Failed to get to {}, status={}, response={}".format(
                    url + "/services", response.status_code, response.json()
                )
            )
        response_json = response.json()
        if response_json["id_types"]:
            if not id_info_params["country"] in response_json["id_types"]:
                raise ValueError("country " + id_info_params["country"] + " is invalid")
            selected_country = response_json["id_types"][id_info_params["country"]]
            if not id_info_params["id_type"] in selected_country:
                raise ValueError("id_type " + id_info_params["id_type"] + " is invalid")
            id_params = selected_country[id_info_params["id_type"]]
            for key in id_params:
                if key not in id_info_params and key not in partner_params:
                    raise ValueError("key " + key + " is required")
                if key in id_info_params and not id_info_params[key]:
                    raise ValueError("key " + key + " cannot be empty")
                if key in partner_params and not partner_params[key]:
                    raise ValueError("key " + key + " cannot be empty")

    @staticmethod
    def get_smile_id_services(sid_server):
        if sid_server in [0, 1]:
            sid_server_map = {
                0: "https://3eydmgh10d.execute-api.us-west-2.amazonaws.com/test",
                1: "https://la7am6gdm8.execute-api.us-west-2.amazonaws.com/prod",
            }
            url = sid_server_map[sid_server]
        else:
            url = sid_server
        response = Utilities.execute_get(url + "/services")
        if response.status_code != 200:
            raise ServerError(
                "Failed to get to {}, status={}, response={}".format(
                    url + "/services", response.status_code, response.json()
                )
            )
        return response

    @staticmethod
    def execute_get(url):
        resp = requests.get(
            url=url,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
            },
        )
        return resp

    @staticmethod
    def execute_post(url, payload):
        data = json.dumps(payload)
        resp = requests.post(
            url=url,
            data=data,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
                "Content-type": "application/json",
            },
        )
        return resp
