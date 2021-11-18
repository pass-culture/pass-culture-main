UBBLE_IDENTIFICATION_RESPONSE = {
    "data": {
        "type": "identifications",
        "id": "3191295",
        "attributes": {
            "anonymized-at": None,
            "comment": None,
            "created-at": "2021-11-18T18:59:59.273402Z",
            "ended-at": None,
            "identification-id": "29d9eca4-dce6-49ed-b1b5-8bb0179493a8",
            "identification-url": "https://id.ubble.ai/29d9eca4-dce6-49ed-b1b5-8bb0179493a8",
            "is-live": False,
            "number-of-attempts": 0,
            "redirect-url": "https://example.com/redirect-url",
            "started-at": None,
            "status-updated-at": "2021-11-18T18:59:59.273171Z",
            "status": "uninitiated",
            "updated-at": "2021-11-18T18:59:59.329011Z",
            "user-agent": None,
            "user-ip-address": None,
            "webhook": "https://example.com/webhook",
        },
        "relationships": {
            "identity": {
                "data": {"type": "identities", "id": "3187041"},
                "links": {"related": "https://api.example.com/api/identifications/3191295/identity"},
            },
            "reference-data": {
                "data": {"type": "reference-data", "id": "119617"},
                "links": {"related": "https://api.example.com/api/identifications/3191295/reference_data"},
            },
        },
    },
    "included": [
        {
            "type": "identities",
            "id": "3187041",
            "attributes": {"birth-date": None, "first-name": None, "last-name": None},
        },
        {
            "type": "reference-data",
            "id": "119617",
            "attributes": {"last-name": "LastName", "first-name": "FirstName", "birth-date": "2003-10-18"},
        },
    ],
}
