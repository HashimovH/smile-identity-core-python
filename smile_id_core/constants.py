class Servers:
    TEST_SERVER_URL = "https://3eydmgh10d.execute-api.us-west-2.amazonaws.com/test"
    LIVE_SERVER_URL = "https://la7am6gdm8.execute-api.us-west-2.amazonaws.com/prod"


class JobTypes:
    """
    Job Type Integer
    1 for jobs that compare a selfie to an ID,
    2 for authenticating a selfie against a previously registered user,
    4 for registering a user,
    5
    8 for updating the enrolled photo
    """
    COMPARE_SELFIE_TO_ID = 1
    AUTHENTICATE_SELFIE = 2
    REGISTER_USER = 4
    VERIFY_DOCUMENT = 5
    UPDATE_PHOTO = 8
