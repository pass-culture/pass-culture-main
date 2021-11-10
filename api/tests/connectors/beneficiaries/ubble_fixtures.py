UBBLE_IDENTIFICATION_RESPONSE = {
    "type": "identifications",
    "id": "801",
    "attributes": {
        "comment": "Identity Verified",
        "created-at": "2019-02-26T16:29:19.857313Z",
        "ended-at": "2019-02-26T17:05:49.096401Z",
        "identification-id": "70f01f19-6ec5-4b14-9b30-2c493e49df15",
        "identification-url": "https://id.ubble.ai/70f01f19-6ec5-4b14-9b30-2c493e49df15",
        "number-of-attempts": 1,
        "redirect-url": "https://www.ubble.ai/",
        "score": 1.0,
        "started-at": "2019-02-26T16:29:43.075181Z",
        "status": "processed",
        "updated-at": "2019-02-26T17:12:02.226018Z",
        "status-updated-at": "2019-02-26T17:12:02.226018Z",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "user-ip-address": "123.123.123.123",
        "webhook": "https://3eb5c250.ngrok.io",
    },
    "relationships": {
        "doc-face-matches": {
            "data": [{"type": "doc-face-matches", "id": "546"}],
            "links": {"related": "http://api/api/identifications/801/doc_face_matches/"},
            "meta": {"count": 1},
        },
        "doc-doc-matches": {
            "data": [{"type": "doc-doc-matches", "id": "62"}],
            "links": {"related": "http://api/api/identifications/801/doc_doc_matches/"},
            "meta": {"count": 1},
        },
        "document-checks": {
            "data": [{"type": "document-checks", "id": "546"}],
            "links": {"related": "http://api/api/identifications/801/document_checks/"},
            "meta": {"count": 1},
        },
        "face-checks": {
            "data": [{"type": "face-checks", "id": "546"}],
            "links": {"related": "http://api/api/identifications/801/face_checks/"},
            "meta": {"count": 1},
        },
        "identity-form-match": {
            "data": [{"type": "identity-form-matches", "id": "646"}],
            "links": {"related": "http://api/api/identifications/801/identity-form-matches/"},
            "meta": {"count": 1},
        },
        "identity": {
            "data": {"type": "identities", "id": "661"},
            "links": {"related": "http://api/api/identifications/801/identity/"},
        },
    },
}
