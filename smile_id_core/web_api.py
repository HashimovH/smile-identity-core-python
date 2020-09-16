import time
import uuid
from datetime import date
from typing import Union

import requests

from smile_id_core.api_base import ApiBase
from smile_id_core.constants import Servers, JobTypes, StatusCodes
from smile_id_core.exceptions import ServerError, VerificationFailed
from smile_id_core.image_upload import generate_zip_file, validate_images
from smile_id_core.validation import IdValidation

__all__ = ["WebApi", "WebApiLive", "WebApiTest"]


class WebApiTest(ApiBase):
    SERVER_URL = Servers.TEST_SERVER_URL

    class Urls:
        GET_JOB_STATUS = "{server_url}/job_status"
        GET_SERVICES = "{server_url}/services"
        UPLOAD = "{server_url}/upload"
        VERIFY_DOCUMENT = "{server_url}/id_verification"

    def __init__(self, partner_id: str, api_key: str, call_back_url: str = None):
        super().__init__(partner_id, api_key)
        self.call_back_url = call_back_url

    @classmethod
    def get_services(cls):
        """
        This method does not require API keys or partner ID
        """
        return cls._make_request("GET", cls.Urls.GET_SERVICES)

    get_smile_id_services = get_services

    @classmethod
    def validate_id_params(cls, data, service_request=False) -> dict:
        """
        Take the response from get_services() and check that

        :param data: a dict containing fields for a document verification request
        :param service_request: whether to perform an API request to get the latest validation schema
        :return:
        """
        if service_request:
            verification_schema = cls.get_services()
        else:
            verification_schema = None

        return IdValidation.validate(data, verification_schema)

    def verify_document(
        self,
        country: str,
        id_type: str,
        id_number: str,
        first_name: str = None,
        last_name: str = None,
        dob: Union[str, date] = None,
    ):
        """
        Performs a document verification request with an immediate response.

        :param country:
        :param id_type:
        :param id_number:
        :param first_name: Optional; required for some ID types, e.g. DRIVERS_LICENSE, PASSPORT
        :param last_name: Optional; required for some ID types
        :param dob: Optional; required for some ID types. Can be a date

        :return: dict
        """

        try:
            dob = dob.isoformat()
        except AttributeError:
            pass

        signature, timestamp = self._get_signature()

        payload = {
            "sec_key": signature,
            "timestamp": timestamp,
            "partner_id": self.partner_id,
            "partner_params": {
                "job_id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
                "job_type": JobTypes.VERIFY_DOCUMENT,
            },
            "country": country,
            "id_type": id_type,
            "id_number": id_number,
        }

        if dob:
            payload["dob"] = dob
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name

        response = self._make_request("POST", self.Urls.VERIFY_DOCUMENT, payload)

        assert isinstance(response, dict)
        if response.get("ResultCode") != StatusCodes.SUCCESS:
            raise VerificationFailed(response)
        return response

    def get_job_status(
        self, user_id, job_id, return_history=False, return_images=False
    ):
        """

        :param user_id: the `user_id` parameter that was passed to the job
        :param job_id: the `job_id` parameter that was passed to the job
        :param return_history:
        :param return_images:
        :return: dict
        """
        signature, timestamp = self._get_signature()

        data = {
            "sec_key": signature,
            "timestamp": timestamp,
            "partner_id": self.partner_id,
            "job_id": job_id,
            "user_id": user_id,
            "image_links": return_images,
            "history": return_history,
        }
        response = self._make_request("POST", self.Urls.GET_JOB_STATUS, data=data)

        timestamp = response["timestamp"]
        server_signature = response["signature"]
        valid = self.signature.confirm_sec_key(timestamp, server_signature)
        if not valid:
            raise ServerError("Unable to confirm validity of the job_status response")
        return response

    def submit_job(
        self,
        job_type: int,
        images_params,
        id_info_params,
        job_id: str = None,
        user_id: str = None,
    ):
        if job_type == JobTypes.VERIFY_DOCUMENT:
            data = IdValidation.validate(id_info_params)
            return self.verify_document(**data)

        if not id_info_params:
            id_info_params = {field: None for field in IdValidation.FIELDS}

        validate_images(images_params)

        sec_key, timestamp = self._get_signature()

        partner_params = {
            "job_id": job_id or str(uuid.uuid4()),
            "user_id": user_id or str(uuid.uuid4()),
            "job_type": job_type,
        }

        payload = {
            "file_name": "selfie.zip",
            "timestamp": timestamp,
            "sec_key": sec_key,
            "smile_client_id": self.partner_id,
            "partner_params": partner_params,
            "model_parameters": {},
            "callback_url": self.call_back_url,
        }

        prep_upload_json_resp = WebApi._make_request(
            "POST",
            self.Urls.UPLOAD,
            payload,
        )
        upload_url = prep_upload_json_resp["upload_url"]
        smile_job_id = prep_upload_json_resp["smile_job_id"]
        zip_stream = generate_zip_file(
            partner_id=self.partner_id,
            sec_key=sec_key,
            timestamp=timestamp,
            callback_url=self.call_back_url,
            image_params=images_params,
            partner_params=partner_params,
            id_info_params=id_info_params,
            upload_url=upload_url,
        )
        self.upload(upload_url, zip_stream)
        return {
            "success": True,
            "smile_job_id": smile_job_id,
            "user_id": user_id,
            "job_id": job_id,
        }

    def poll_job_status(
        self,
        user_id,
        job_id,
        return_history=False,
        return_images=False,
        max_polls=20,
        delay=2,
        counter=0,
    ):
        if counter > max_polls:
            raise ServerError(
                f"Failed to get job status in {max_polls} attempts: user_id={user_id}, job_id={job_id}"
            )
        if counter > 0:
            time.sleep(delay)

        job_status = self.get_job_status(user_id, job_id, return_history, return_images)
        if job_status["job_complete"]:
            return job_status
        return self.poll_job_status(
            user_id,
            job_id,
            return_history,
            return_images,
            max_polls,
            delay,
            counter + 1,
        )

    @staticmethod
    def upload(url, file):
        """
        Uploads a file to AWS S3 via a URL supplied by a previous API call

        :param url:
        :param file:
        :return:
        """
        resp = requests.put(
            url=url, data=file, headers={"Content-type": "application/zip"}
        )
        if resp.status_code != 200:
            raise ServerError(
                "Failed to upload file to {}, status={}, response={}".format(
                    url, resp.status_code, resp.text
                )
            )
        return resp


class WebApiLive(WebApiTest):
    SERVER_URL = Servers.LIVE_SERVER_URL


WebApi = WebApiTest
