VALIDATION_SCHEMA = {
    "GH": {
        "SSNIT": ["country", "id_type", "id_number"],
        "VOTER_ID": ["country", "id_type", "id_number"],
        "DRIVERS_LICENSE": ["country", "id_type", "id_number"],
        "PASSPORT": ["country", "id_type", "id_number"],
    },
    "NG": {
        "NIN": ["country", "id_type", "id_number"],
        "CAC": ["country", "id_type", "id_number", "company"],
        "TIN": ["country", "id_type", "id_number"],
        "VOTER_ID": ["country", "id_type", "id_number"],
        "BVN": ["country", "id_type", "id_number"],
        "PHONE_NUMBER": ["country", "id_type", "id_number", "first_name", "last_name"],
        "DRIVERS_LICENSE": [
            "country",
            "id_type",
            "id_number",
            "first_name",
            "last_name",
            "dob",
        ],
        "PASSPORT": [
            "country",
            "id_type",
            "id_number",
            "first_name",
            "last_name",
            "dob",
        ],
    },
    "KE": {
        "NATIONAL_ID": ["country", "id_type", "id_number"],
        "ALIEN_CARD": ["country", "id_type", "id_number"],
        "PASSPORT": ["country", "id_type", "id_number"],
    },
    "ZA": {
        "NATIONAL_ID": ["country", "id_type", "id_number"],
        "NATIONAL_ID_NO_PHOTO": ["country", "id_type", "id_number"],
    },
}
