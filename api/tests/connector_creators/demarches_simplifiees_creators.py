from pcapi.connectors.dms.models import GraphQLApplicationStates


def get_bank_info_response_procedure_v4(
    dms_token: str = "1234567890abcdef",
    etablissement: dict | None = None,
    state: str = GraphQLApplicationStates.accepted.value,
    annotations: list | None = None,
    dossier_id: str = "Q2zzbXAtNzgyODAw",
    application_id: int = 9,
    last_pending_correction_date: str | None = None,
) -> dict:
    etablissement = etablissement or {
        "etablissement": {
            "entreprise": None,
            "siret": None,
        },
        "id": "Q2hhbXAtNzgyODAw",
        "label": "SIRET",
        "stringValue": None,
    }
    annotations = annotations or [
        {"label": "Nouvelle annotation Texte", "id": "OTHERID"},
        {
            "id": "Q2hhbXAtOTE1NDg5",
            "label": "Erreur traitement pass Culture",
            "stringValue": "",
            "value": None,
        },
    ]
    result = {
        "id": dossier_id,
        "number": application_id,
        "champs": [
            {
                "id": "Q2hhbXAtMjY3NDMyMQ==",
                "label": "N° d'identifiant du lieu",
                "stringValue": dms_token,
                "value": dms_token,
            },
            etablissement,
            {"id": "Q2hhbXAtNzAwNTA5", "label": "Vos coordonnées bancaires", "stringValue": "", "value": None},
            {
                "id": "Q2hhbXAtMzUyNzIy",
                "label": "IBAN",
                "stringValue": "FR7630007000111234567890144",
                "value": "FR7630007000111234567890144",
            },
            {"id": "Q2hhbXAtMzUyNzI3", "label": "BIC", "stringValue": "SOGEFRPP", "value": "SOGEFRPP"},
            {
                "id": "Q2hhbXAtNDA3ODk1",
                "label": "N° d'identifiant du lieu",
                "stringValue": "60a7536a21c8",
                "value": "60a7536a21c8",
            },
        ],
        "dateDerniereModification": "2020-01-03T01:00:00+01:00",
        "dateDerniereCorrectionEnAttente": last_pending_correction_date,
        "state": state,
        "annotations": annotations,
    }
    return result


def get_bank_info_response_procedure_v4_as_batch(
    dms_token: str = "1234567890abcdef",
    etablissement: dict | None = None,
    state: str = GraphQLApplicationStates.accepted.value,
    annotations: list | None = None,
    dossier_id: str = "Q2zzbXAtNzgyODAw",
    application_id: int = 9,
    last_modification_date: str = "2020-01-03T01:00:00+01:00",
    last_pending_correction_date: str | None = None,
) -> dict:
    etablissement = etablissement or {
        "etablissement": {
            "entreprise": None,
            "siret": None,
        },
        "id": "Q2hhbXAtNzgyODAw",
        "label": "SIRET",
        "stringValue": None,
    }
    if annotations is None:
        annotations = [
            {
                "id": "Q2hhbXAtOTE1NDg5",
                "label": "Erreur traitement pass Culture",
                "stringValue": "",
                "value": None,
            },
            {"id": "Q2hhbXAtMjc1NzMyOQ==", "label": "URL du lieu", "stringValue": "", "value": None},
        ]
    result = {
        "demarche": {
            "dossiers": {
                "pageInfo": {
                    "hasPreviousPage": False,
                    "hasNextPage": False,
                    "endCursor": "MjAyMy0xMC0yNlQxMjoxODowMC4xNjA2OTUwMDBaOzE0NzQyNjU0",
                },
                "nodes": [
                    {
                        "id": dossier_id,
                        "number": application_id,
                        "champs": [
                            {
                                "id": "Q2hhbXAtMjY3NDMyMQ==",
                                "label": "N° d'identifiant du lieu",
                                "stringValue": dms_token,
                                "value": dms_token,
                            },
                            etablissement,
                            {
                                "id": "Q2hhbXAtNzAwNTA5",
                                "label": "Vos coordonnées bancaires",
                                "stringValue": "",
                                "value": None,
                            },
                            {
                                "id": "Q2hhbXAtMzUyNzIy",
                                "label": "IBAN",
                                "stringValue": "FR7630007000111234567890144",
                                "value": "FR7630007000111234567890144",
                            },
                            {"id": "Q2hhbXAtMzUyNzI3", "label": "BIC", "stringValue": "SOGEFRPP", "value": "SOGEFRPP"},
                            {
                                "id": "Q2hhbXAtNDA3ODk1",
                                "label": "N° d'identifiant du lieu",
                                "stringValue": "60a7536a21c8",
                                "value": "60a7536a21c8",
                            },
                        ],
                        "dateDerniereModification": last_modification_date,
                        "dateDerniereCorrectionEnAttente": last_pending_correction_date,
                        "state": state,
                        "annotations": annotations,
                    }
                ],
            }
        }
    }
    return result


def get_bank_info_response_procedure_v5(
    state: str = GraphQLApplicationStates.accepted.value,
    annotations: list[dict] | None = None,
    messages: list[dict] | None = None,
    b64_encoded_application_id: str = "RG9zc2llci0xNDc0MjY1NA==",
    application_id: int = 14742654,
    bic: str = "BICAGRIFRPP",
    iban: str = "FR76 3000 6000 0112 3456 7890 189",
    last_modification_date: str = "2023-10-26T14:51:09+02:00",
    last_fields_modification: str = "2023-10-26T14:51:09+02:00",
    last_pending_correction_date: str | None = None,
    siret: str = "85331845900049",
    label: str | None = "Intitulé du compte bancaire",
) -> dict:
    iban = "".join(iban.split())

    return {
        "demarche": {
            "dossiers": {
                "pageInfo": {
                    "hasPreviousPage": False,
                    "hasNextPage": False,
                    "endCursor": "MjAyMy0xMC0yNlQxMjoxODowMC4xNjA2OTUwMDBaOzE0NzQyNjU0",
                },
                "nodes": [
                    {
                        "id": b64_encoded_application_id,
                        "number": application_id,
                        "state": state,
                        "dateDerniereModification": last_modification_date,
                        "dateDerniereModificationChamps": last_fields_modification,
                        "dateDerniereCorrectionEnAttente": last_pending_correction_date,
                        "usager": {"email": "usager@example.com"},
                        "demandeur": {"siret": siret},
                        "champs": [
                            {
                                "id": "Q2hhbXAtNzAwNTA5",
                                "label": "Vos informations bancaires",
                                "stringValue": "",
                                "value": None,
                            },
                            {
                                "id": "Q2hhbXAtMzU3MzQ1Mw==",
                                "label": "Intitulé du compte bancaire",
                                "stringValue": "Intitulé du compte bancaire",
                                "value": label,
                            },
                            {
                                "id": "Q2hhbXAtMzUyNzI3",
                                "label": "BIC",
                                "stringValue": bic,
                                "value": bic,
                            },
                            {
                                "id": "Q2hhbXAtMzUyNzIy",
                                "label": "IBAN",
                                "stringValue": iban,
                                "value": iban,
                            },
                            {
                                "id": "Q2hhbXAtODU2ODE4",
                                "label": "RIB",
                                "stringValue": "",
                                "file": {
                                    "url": "https://static.demarches-simplifiees.fr:443/v1/AUTH_db3cbfc79c914f87b192ff7c6bb176f0/ds_activestorage_backup/2023/10/26/Ws/WscW3LjQ2zJd824mF7FDhw95wKwC?temp_url_sig=62e7ef36caebbc88292bed98ce4438c2bad29e2b&temp_url_expires=1699356787&filename=Mon%20RIB.png&inline",
                                    "checksum": "vtbp0+ODQtL3qzbeYx6s3g==",
                                    "contentType": "image/png",
                                    "filename": "Mon RIB.png",
                                },
                            },
                            {
                                "id": "Q2hhbXAtODU2NzEz",
                                "label": "Identité du responsable légal",
                                "stringValue": "",
                                "value": None,
                            },
                            {
                                "id": "Q2hhbXAtMzYzMDA4Ng==",
                                "label": "Carte d'identité (recto) ou passeport du responsable légal de la structure",
                                "stringValue": "",
                            },
                            {"id": "Q2hhbXAtMzYxMzExMA==", "label": "Structure", "stringValue": "", "value": None},
                            {
                                "id": "Q2hhbXAtMzQ4NTEwOA==",
                                "label": "Nature juridique de votre structure",
                                "stringValue": "Entreprise individuelle",
                                "value": "Entreprise individuelle",
                            },
                            {
                                "id": "Q2hhbXAtMzQ4NTE2Mg==",
                                "label": "Déclaration sur l'honneur",
                                "stringValue": "",
                                "value": None,
                            },
                            {
                                "id": "Q2hhbXAtMzQ4NTE1Nw==",
                                "label": "Je déclare sur l’honneur disposer de l'autorisation du responsable légal pour effectuer cette démarche",
                                "stringValue": "true",
                            },
                            {
                                "id": "Q2hhbXAtMzQ4NTE3OQ==",
                                "label": "Je déclare que l'ensemble des réponses et documents fournis sont corrects et authentiques",
                                "stringValue": "true",
                            },
                        ],
                        "annotations": annotations
                        or [
                            {
                                "id": "Q2hhbXAtOTE1NDg5",
                                "label": "En attente de validation de structure",
                                "stringValue": "false",
                            },
                            {
                                "id": "Q2hhbXAtMjc2NDk5MA==",
                                "label": "En attente de validation ADAGE",
                                "stringValue": "false",
                            },
                            {
                                "id": "Q2hhbXAtMzYzMDA5NA==",
                                "label": "Motif de mise en attente du dossier",
                                "stringValue": "",
                                "value": None,
                            },
                            {
                                "id": "Q2hhbXAtMzYzMDA5NQ==",
                                "label": "Annotation technique (réservée à pcapi)",
                                "stringValue": "",
                                "value": None,
                            },
                        ],
                        "messages": messages
                        or [
                            {
                                "email": "contact@demarches-simplifiees.fr",
                                "createdAt": last_modification_date,
                            },
                        ],
                    }
                ],
            }
        }
    }
