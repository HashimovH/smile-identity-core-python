from smile_id_core.exceptions import InvalidDataFormat


class IdValidation:
    FIELDS = {
        "country": True,  # required
        "id_type": True,  # required
        "id_number": True,  # required
        "first_name": False,  # not required
        "middle_name": False,
        "last_name": False,
        "dob": False,
        "phone_number": False,
    }

    @classmethod
    def validate(cls, data: dict):
        if not isinstance(data, dict):
            raise InvalidDataFormat("ID validation request fields must be a dict")

        result = {}
        for field, required in cls.FIELDS.items():
            try:
                value = data[field]
            except KeyError:
                if required:
                    raise InvalidDataFormat(
                        f"ID validation request field `{field}` is required"
                    )
            else:
                if not value and required:
                    raise InvalidDataFormat(
                        f"ID validation request field `{field}` can not be empty"
                    )
                if not isinstance(value, str):
                    raise InvalidDataFormat(
                        f"ID validation request field `{field}` must be a string"
                    )
                result[field] = value
        return result
