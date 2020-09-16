from smile_id_core.exceptions import InvalidDataFormat
from smile_id_core.validation_schema import VALIDATION_SCHEMA


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
    def validate(cls, data: dict, validation_schema: dict = None):
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

        if validation_schema is None:
            validation_schema = VALIDATION_SCHEMA

        try:
            id_types_by_country = validation_schema[result["country"]]
        except KeyError as e:
            raise InvalidDataFormat(
                f"Country '{result['country']}' is not supported in the selected schema"
            ) from e

        try:
            id_type_fields = id_types_by_country[result["id_type"]]
        except KeyError as e:
            raise InvalidDataFormat(
                f"Country '{result['country']}' does not support document type '{result['id_type']}'"
            ) from e

        missing_fields = [
            field
            for field in id_type_fields
            if field not in ("user_id", "job_id") and not result.get(field)
        ]

        if missing_fields:
            missing_fields = ",".join(sorted(missing_fields))
            raise InvalidDataFormat(
                f"Some required fields are missing or empty: [{missing_fields}] required for "
                f"Country '{result['country']}' ID type '{result['id_type']}' verification"
            )

        return result
