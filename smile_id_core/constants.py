class Servers:
    TEST_SERVER_URL = "https://testapi.smileidentity.com"
    LIVE_SERVER_URL = "https://api.smileidentity.com"


class JobTypes:
    """
    Job Types

    1 for jobs that compare a selfie to an ID,
    2 for authenticating a selfie against a previously registered user,
    4 for registering a user,
    5 for ID validation,
    8 for updating the enrolled photo

    Source: https://docs.smileidentity.com/results/result-and-error-codes
    """

    REGISTER_WITH_ID = 1
    AUTHENTICATE = 2
    REGISTER_WITHOUT_ID = 4
    VERIFY_DOCUMENT = 5
    UPDATE_PHOTO = 8


class ImageTypes:
    """
    Images can be in png or jpg format
    """

    SELFIE = 0
    ID_CARD = 1
    SELFIE_BASE64 = 2
    ID_CARD_BASE64 = 3

    ALL = (SELFIE, SELFIE_BASE64, ID_CARD, ID_CARD_BASE64)


class StatusCodes:
    """
    Source: https://docs.smileidentity.com/results/result-and-error-codes
    """

    SUCCESS = "1012"
    INVALID_ID = "1013"
    UNSUPPORTED_ARGUMENT = "1014"  # Unsupported ID Type, Country, or ID Number Format
    DATABASE_UNAVAILABLE = "1015"  # ID Authority Database query error (e.g. downtime)
    ACTIVATION_REQUIRED = "1016"
