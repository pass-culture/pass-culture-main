IDENTIFICATION_ID = "862a4c37-7026-4a35-a723-5d81d201d33c"

START_IDENTIFICATION_RESPONSE = {
    "data": {
        "type": "identifications",
        "id": "5033001",
        "attributes": {
            "anonymized-at": None,
            "comment": None,
            "created-at": "2018-01-01T09:20:15.185965Z",
            "ended-at": None,
            "identification-id": IDENTIFICATION_ID,
            "identification-url": f"https://id.ubble.ai/{IDENTIFICATION_ID}",
            "is-live": False,
            "number-of-attempts": 0,
            "redirect-url": "https://passculture.app/verification-identite/fin",
            "started-at": None,
            "status-updated-at": "2018-01-01T09:20:15.185672Z",
            "status": "uninitiated",
            "updated-at": "2018-01-01T09:20:15.246234Z",
            "user-agent": None,
            "user-ip-address": None,
            "webhook": "https://backend.testing.passculture.team/webhooks/ubble/application_status",
        },
        "relationships": {
            "identity": {
                "links": {"related": "https://api.default.svc.cluster.local/api/identifications/5033001/identity"},
                "data": {"type": "identities", "id": "4875620"},
            },
            "reference-data": {
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5033001/reference_data"
                },
                "data": {"type": "reference-data", "id": "674738"},
            },
        },
    },
    "included": [
        {
            "type": "identities",
            "id": "4875620",
            "attributes": {"birth-date": None, "first-name": None, "last-name": None},
        },
        {
            "type": "reference-data",
            "id": "674738",
            "attributes": {"last-name": "DE TOUL", "first-name": "RAOUL", "birth-date": None},
        },
    ],
}

INITIATED_IDENTIFICATION_RESPONSE = {
    "data": {
        "type": "identifications",
        "id": "5033001",
        "attributes": {
            "anonymized-at": None,
            "comment": None,
            "created-at": "2018-01-01T09:20:15.185965Z",
            "ended-at": None,
            "identification-id": IDENTIFICATION_ID,
            "identification-url": f"https://id.ubble.ai/{IDENTIFICATION_ID}",
            "is-live": False,
            "number-of-attempts": 1,
            "redirect-url": "https://passculture.app/verification-identite/fin",
            "started-at": "2018-01-01T09:41:00.868951Z",
            "status-updated-at": "2018-01-01T09:41:01.480892Z",
            "status": "initiated",
            "updated-at": "2018-01-01T09:41:01.481069Z",
            "user-agent": None,
            "user-ip-address": None,
            "webhook": "https://backend.testing.passculture.team/webhooks/ubble/application_status",
        },
        "relationships": {
            "identity": {
                "links": {"related": "https://api.default.svc.cluster.local/api/identifications/5033001/identity"},
                "data": {"type": "identities", "id": "4875620"},
            },
            "reference-data": {
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5033001/reference_data"
                },
                "data": {"type": "reference-data", "id": "674738"},
            },
        },
    },
    "included": [
        {
            "type": "identities",
            "id": "4875620",
            "attributes": {"birth-date": None, "first-name": None, "last-name": None},
        },
        {
            "type": "reference-data",
            "id": "674738",
            "attributes": {"last-name": "DE TOUL", "first-name": "RAOUL", "birth-date": None},
        },
    ],
}

PROCESSING_IDENTIFICATION_RESPONSE = {
    "data": {
        "type": "identifications",
        "id": "5033001",
        "attributes": {
            "anonymized-at": None,
            "comment": "Some additional elements need to be verified. You are using a free API identifier, you will be notified in a few hours by webhook when the final answer is ready. You can use the standard answers in the API documentation to finalize your integration : https://ubbleai.github.io/developer-documentation/#examples",
            "created-at": "2018-01-01T09:20:15.185965Z",
            "ended-at": None,
            "identification-id": IDENTIFICATION_ID,
            "identification-url": f"https://id.ubble.ai/{IDENTIFICATION_ID}",
            "is-live": False,
            "number-of-attempts": 2,
            "redirect-url": "https://passculture.app/verification-identite/fin",
            "started-at": "2018-01-01T09:41:00.868951Z",
            "status-updated-at": "2018-01-01T13:56:20.432326Z",
            "status": "processing",
            "updated-at": "2018-01-01T13:56:42.181742Z",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/99.0.4844.59 Mobile/15E148 Safari/604.1",
            "user-ip-address": "92.184.117.52",
            "webhook": "https://backend.testing.passculture.team/webhooks/ubble/application_status",
        },
        "relationships": {
            "identity": {
                "links": {"related": "https://api.default.svc.cluster.local/api/identifications/5033001/identity"},
                "data": {"type": "identities", "id": "4875620"},
            },
            "reference-data": {
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5033001/reference_data"
                },
                "data": {"type": "reference-data", "id": "674738"},
            },
        },
    },
    "included": [
        {
            "type": "documents",
            "id": "7711344",
            "attributes": {
                "media-type": None,
                "signed-image-back-url": None,
                "signed-image-front-url": None,
                "signed-video-back-url": None,
                "signed-video-front-url": None,
            },
        },
        {"type": "faces", "id": "5856896", "attributes": {"signed-image-url": None, "signed-video-url": None}},
        {
            "type": "identities",
            "id": "4875620",
            "attributes": {"birth-date": None, "first-name": None, "last-name": None},
            "relationships": {
                "document": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/identities/4875620/document"},
                    "data": {"type": "documents", "id": "7711344"},
                },
                "documents": {
                    "meta": {"count": 1},
                    "data": [{"type": "documents", "id": "7711344"}],
                    "links": {"related": "https://api.default.svc.cluster.local/api/identities/4875620/documents/"},
                },
                "face": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/identities/4875620/face"},
                    "data": {"type": "faces", "id": "5856896"},
                },
            },
        },
        {
            "type": "reference-data",
            "id": "674738",
            "attributes": {"last-name": "DE TOUL", "first-name": "RAOUL", "birth-date": None},
        },
    ],
}


WRONG_REFERENCE_DATA_RESPONSE = {
    "data": {
        "type": "identifications",
        "id": "5033001",
        "attributes": {
            "anonymized-at": None,
            "comment": "Extracted identity and reference data do not match.",
            "created-at": "2018-01-01T09:20:15.185965Z",
            "ended-at": "2018-01-01T14:00:14.863359Z",
            "identification-id": IDENTIFICATION_ID,
            "identification-url": f"https://id.ubble.ai/{IDENTIFICATION_ID}",
            "is-live": False,
            "number-of-attempts": 2,
            "redirect-url": "https://passculture.app/verification-identite/fin",
            "score": 0.0,
            "started-at": "2018-01-01T09:41:00.868951Z",
            "status-updated-at": "2018-01-01T14:00:14.863385Z",
            "status": "processed",
            "updated-at": "2018-01-01T14:00:16.916021Z",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/99.0.4844.59 Mobile/15E148 Safari/604.1",
            "user-ip-address": "92.184.117.52",
            "webhook": "https://backend.testing.passculture.team/webhooks/ubble/application_status",
        },
        "relationships": {
            "doc-doc-matches": {
                "meta": {"count": 0},
                "data": [],
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5033001/doc_doc_matches/"
                },
            },
            "doc-face-matches": {
                "meta": {"count": 1},
                "data": [{"type": "doc-face-matches", "id": "6995259"}],
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5033001/doc_face_matches/"
                },
            },
            "face-face-matches": {
                "meta": {"count": 0},
                "data": [],
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5033001/face_face_matches/"
                },
            },
            "document-checks": {
                "meta": {"count": 1},
                "data": [{"type": "document-checks", "id": "7710765"}],
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5033001/document_checks/"
                },
            },
            "face-checks": {
                "meta": {"count": 1},
                "data": [{"type": "face-checks", "id": "5856499"}],
                "links": {"related": "https://api.default.svc.cluster.local/api/identifications/5033001/face_checks/"},
            },
            "identity": {
                "links": {"related": "https://api.default.svc.cluster.local/api/identifications/5033001/identity"},
                "data": {"type": "identities", "id": "4875620"},
            },
            "reference-data": {
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5033001/reference_data"
                },
                "data": {"type": "reference-data", "id": "674738"},
            },
            "reference-data-check": {
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5033001/reference_data_check"
                },
                "data": {"type": "reference-data-checks", "id": "674736"},
            },
        },
    },
    "included": [
        {
            "type": "doc-face-matches",
            "id": "6995259",
            "attributes": {"score": 1.0},
            "relationships": {
                "document": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/doc_face_matches/6995259/document"},
                    "data": {"type": "documents", "id": "7711344"},
                },
                "face": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/doc_face_matches/6995259/face"},
                    "data": {"type": "faces", "id": "5856896"},
                },
            },
        },
        {
            "type": "document-checks",
            "id": "7710765",
            "attributes": {
                "data-extracted-score": 1.0,
                "expiry-date-score": 1.0,
                "issue-date-score": None,
                "live-video-capture-score": None,
                "mrz-validity-score": 1.0,
                "mrz-viz-score": 1.0,
                "ove-back-score": 1.0,
                "ove-front-score": 1.0,
                "ove-score": 1.0,
                "quality-score": 1.0,
                "score": 1.0,
                "supported": 1.0,
                "visual-back-score": 1.0,
                "visual-front-score": 1.0,
            },
            "relationships": {
                "document": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/document_checks/7710765/document"},
                    "data": {"type": "documents", "id": "7711344"},
                }
            },
        },
        {
            "type": "documents",
            "id": "7711344",
            "attributes": {
                "birth-date": "2000-01-01",
                "birth-place": None,
                "document-number": "123456P00123",
                "document-type": "ID",
                "document-type-detailed": None,
                "expiry-date": "2029-02-17",
                "first-name": "RAOUL",
                "gender": "M",
                "issue-date": None,
                "issue-place": None,
                "issuing-state-code": "FRA",
                "last-name": "DE TOUL",
                "married-name": None,
                "media-type": "video",
                "mrz": "IDFRADETOUL<<<<<<<<<<<<<<<<<<<75P001123456P001233RAOUL<<JEAN<<0001010M8",
                "nationality": None,
                "obtaining-date": None,
                "personal-number": None,
                "remarks": None,
                "signed-image-back-url": f"https://storage.ubble.ai/production-ubble-ai/HIDDEN_CODE/{IDENTIFICATION_ID}/hidden_signature",
                "signed-image-front-url": f"https://storage.ubble.ai/production-ubble-ai/HIDDEN_CODE/{IDENTIFICATION_ID}/hidden_signature",
                "signed-video-back-url": f"https://storage.ubble.ai/production-ubble-ai/HIDDEN_CODE/{IDENTIFICATION_ID}/hidden_signature",
                "signed-video-front-url": f"https://storage.ubble.ai/production-ubble-ai/HIDDEN_CODE/{IDENTIFICATION_ID}/hidden_signature",
            },
            "relationships": {
                "identity": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/documents/7711344/identity"},
                    "data": {"type": "identities", "id": "4875620"},
                }
            },
        },
        {
            "type": "face-checks",
            "id": "5856499",
            "attributes": {
                "active-liveness-score": 1.0,
                "live-video-capture-score": None,
                "quality-score": 1.0,
                "score": 1.0,
            },
            "relationships": {
                "face": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/face_checks/5856499/face"},
                    "data": {"type": "faces", "id": "5856896"},
                }
            },
        },
        {
            "type": "faces",
            "id": "5856896",
            "attributes": {
                "signed-image-url": f"https://storage.ubble.ai/production-ubble-ai/HIDDEN_CODE/{IDENTIFICATION_ID}/hidden_signature",
                "signed-video-url": f"https://storage.ubble.ai/production-ubble-ai/HIDDEN_CODE/{IDENTIFICATION_ID}/hidden_signature",
            },
            "relationships": {
                "identity": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/faces/5856896/identity"},
                    "data": {"type": "identities", "id": "4875620"},
                }
            },
        },
        {
            "type": "identities",
            "id": "4875620",
            "attributes": {"birth-date": "2000-01-01", "first-name": "RAOUL", "last-name": "DE TOUL"},
            "relationships": {
                "document": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/identities/4875620/document"},
                    "data": {"type": "documents", "id": "7711344"},
                },
                "documents": {
                    "meta": {"count": 1},
                    "data": [{"type": "documents", "id": "7711344"}],
                    "links": {"related": "https://api.default.svc.cluster.local/api/identities/4875620/documents/"},
                },
                "face": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/identities/4875620/face"},
                    "data": {"type": "faces", "id": "5856896"},
                },
            },
        },
        {
            "type": "reference-data",
            "id": "674738",
            "attributes": {"last-name": "DE TOUL", "first-name": "RAOUL", "birth-date": None},
        },
        {
            "type": "reference-data-checks",
            "id": "674736",
            "attributes": {"score": 0.0},
            "relationships": {
                "reference-data": {
                    "links": {
                        "related": "https://api.default.svc.cluster.local/api/reference_data_checks/674736/reference_data"
                    },
                    "data": {"type": "reference-data", "id": "674738"},
                }
            },
        },
    ],
}

PROCESSED_IDENTIFICATION_RESPONSE = {
    "data": {
        "type": "identifications",
        "id": "5045236",
        "attributes": {
            "anonymized-at": None,
            "comment": "",
            "created-at": "2018-01-01T08:25:51.492743Z",
            "ended-at": "2018-01-01T08:41:02.504663Z",
            "identification-id": "1f44355f-2d66-4ba8-850d-79bb287c953d",
            "identification-url": "https://id.ubble.ai/1f44355f-2d66-4ba8-850d-79bb287c953d",
            "is-live": False,
            "number-of-attempts": 1,
            "redirect-url": "https://passculture.app/verification-identite/fin",
            "score": 1.0,
            "started-at": "2018-01-01T08:31:52.358229Z",
            "status-updated-at": "2018-01-01T08:41:02.504682Z",
            "status": "processed",
            "updated-at": "2018-01-01T08:41:03.799660Z",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/99.0.4844.59 Mobile/15E148 Safari/604.1",
            "user-ip-address": "92.184.117.51",
            "webhook": "https://backend.testing.passculture.team/webhooks/ubble/application_status",
        },
        "relationships": {
            "doc-doc-matches": {
                "meta": {"count": 0},
                "data": [],
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5045236/doc_doc_matches/"
                },
            },
            "doc-face-matches": {
                "meta": {"count": 1},
                "data": [{"type": "doc-face-matches", "id": "7007083"}],
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5045236/doc_face_matches/"
                },
            },
            "face-face-matches": {
                "meta": {"count": 0},
                "data": [],
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5045236/face_face_matches/"
                },
            },
            "document-checks": {
                "meta": {"count": 1},
                "data": [{"type": "document-checks", "id": "7723584"}],
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5045236/document_checks/"
                },
            },
            "face-checks": {
                "meta": {"count": 1},
                "data": [{"type": "face-checks", "id": "5867766"}],
                "links": {"related": "https://api.default.svc.cluster.local/api/identifications/5045236/face_checks/"},
            },
            "identity": {
                "links": {"related": "https://api.default.svc.cluster.local/api/identifications/5045236/identity"},
                "data": {"type": "identities", "id": "4887091"},
            },
            "reference-data": {
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5045236/reference_data"
                },
                "data": {"type": "reference-data", "id": "678671"},
            },
            "reference-data-check": {
                "links": {
                    "related": "https://api.default.svc.cluster.local/api/identifications/5045236/reference_data_check"
                },
                "data": {"type": "reference-data-checks", "id": "678669"},
            },
        },
    },
    "included": [
        {
            "type": "doc-face-matches",
            "id": "7007083",
            "attributes": {"score": 1.0},
            "relationships": {
                "document": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/doc_face_matches/7007083/document"},
                    "data": {"type": "documents", "id": "7724163"},
                },
                "face": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/doc_face_matches/7007083/face"},
                    "data": {"type": "faces", "id": "5868163"},
                },
            },
        },
        {
            "type": "document-checks",
            "id": "7723584",
            "attributes": {
                "data-extracted-score": 1.0,
                "expiry-date-score": 1.0,
                "issue-date-score": None,
                "live-video-capture-score": None,
                "mrz-validity-score": 1.0,
                "mrz-viz-score": 1.0,
                "ove-back-score": 1.0,
                "ove-front-score": 1.0,
                "ove-score": 1.0,
                "quality-score": 1.0,
                "score": 1.0,
                "supported": 1.0,
                "visual-back-score": 1.0,
                "visual-front-score": 1.0,
            },
            "relationships": {
                "document": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/document_checks/7723584/document"},
                    "data": {"type": "documents", "id": "7724163"},
                }
            },
        },
        {
            "type": "documents",
            "id": "7724163",
            "attributes": {
                "birth-date": "2000-01-01",
                "birth-place": None,
                "document-number": "123456P00123",
                "document-type": "ID",
                "document-type-detailed": None,
                "expiry-date": "2029-02-17",
                "first-name": "RAOUL",
                "gender": "M",
                "issue-date": None,
                "issue-place": None,
                "issuing-state-code": "FRA",
                "last-name": "DE TOULON",
                "married-name": None,
                "media-type": "video",
                "mrz": "IDFRADETOUL<<<<<<<<<<<<<<<<<<<75P001123456P001233RAOUL<<JEAN<<0001010M8",
                "nationality": None,
                "obtaining-date": None,
                "personal-number": None,
                "remarks": None,
                "signed-image-back-url": "https://storage.ubble.ai/production-ubble-ai/HIDDEN_CODE/hidden_signature",
                "signed-image-front-url": "https://storage.ubble.ai/production-ubble-ai/HIDDEN_CODE/hidden_signature",
                "signed-video-back-url": "https://storage.ubble.ai/production-ubble-ai/HIDDEN_CODE/hidden_signature",
                "signed-video-front-url": "https://storage.ubble.ai/production-ubble-ai/HIDDEN_CODE/hidden_signature",
            },
            "relationships": {
                "identity": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/documents/7724163/identity"},
                    "data": {"type": "identities", "id": "4887091"},
                }
            },
        },
        {
            "type": "face-checks",
            "id": "5867766",
            "attributes": {
                "active-liveness-score": 1.0,
                "live-video-capture-score": None,
                "quality-score": 1.0,
                "score": 1.0,
            },
            "relationships": {
                "face": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/face_checks/5867766/face"},
                    "data": {"type": "faces", "id": "5868163"},
                }
            },
        },
        {
            "type": "faces",
            "id": "5868163",
            "attributes": {
                "signed-image-url": "https://storage.ubble.ai/production-ubble-ai/HIDDEN_CODE/hidden_signature",
                "signed-video-url": "https://storage.ubble.ai/production-ubble-ai/HIDDEN_CODE/hidden_signature",
            },
            "relationships": {
                "identity": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/faces/5868163/identity"},
                    "data": {"type": "identities", "id": "4887091"},
                }
            },
        },
        {
            "type": "identities",
            "id": "4887091",
            "attributes": {"birth-date": "2000-01-01", "first-name": "RAOUL", "last-name": "DE TOUL"},
            "relationships": {
                "document": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/identities/4887091/document"},
                    "data": {"type": "documents", "id": "7724163"},
                },
                "documents": {
                    "meta": {"count": 1},
                    "data": [{"type": "documents", "id": "7724163"}],
                    "links": {"related": "https://api.default.svc.cluster.local/api/identities/4887091/documents/"},
                },
                "face": {
                    "links": {"related": "https://api.default.svc.cluster.local/api/identities/4887091/face"},
                    "data": {"type": "faces", "id": "5868163"},
                },
            },
        },
        {
            "type": "reference-data",
            "id": "678671",
            "attributes": {"last-name": "DE TOUL", "first-name": "RAOUL", "birth-date": None},
        },
        {
            "type": "reference-data-checks",
            "id": "678669",
            "attributes": {"score": 1.0},
            "relationships": {
                "reference-data": {
                    "links": {
                        "related": "https://api.default.svc.cluster.local/api/reference_data_checks/678669/reference_data"
                    },
                    "data": {"type": "reference-data", "id": "678671"},
                }
            },
        },
    ],
}
