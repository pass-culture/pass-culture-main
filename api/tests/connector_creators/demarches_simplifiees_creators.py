from pcapi.connectors.dms.models import GraphQLApplicationStates


def get_bank_info_response_procedure_v5(
    state: str = GraphQLApplicationStates.accepted.value,
    annotations: list[dict] | None = None,
    messages: list[dict] | None = None,
    b64_encoded_application_id: str = "RG9zc2llci0xNDc0MjY1NA==",
    application_id: int = 14742654,
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
                                    "url": "https://static.demarche.numerique.gouv.fr:443/v1/AUTH_db3cbfc79c914f87b192ff7c6bb176f0/ds_activestorage_backup/2023/10/26/Ws/WscW3LjQ2zJd824mF7FDhw95wKwC?temp_url_sig=62e7ef36caebbc88292bed98ce4438c2bad29e2b&temp_url_expires=1699356787&filename=Mon%20RIB.png&inline",
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
                                "email": "contact.demarche.numerique@example.com",
                                "createdAt": last_modification_date,
                            },
                        ],
                    }
                ],
            }
        }
    }


def get_bank_info_response_procedure_nc(
    state: str = GraphQLApplicationStates.accepted.value,
) -> dict:
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
                        "id": "RG9zc2lldi0yOAMzNuAyMQ==",
                        "number": 988,
                        "state": state,
                        "dateDerniereModification": "2025-12-19T09:51:48+01:00",
                        "dateDerniereModificationChamps": "2025-12-19T00:05:33+01:00",
                        "dateDerniereCorrectionEnAttente": None,
                        "usager": {"email": "usager@example.com"},
                        "demandeur": {},
                        "champs": [
                            {
                                "id": "Q2hhbXAtNTU0OTIwNg==",
                                "label": "Votre structure",
                                "stringValue": "",
                                "updatedAt": "2025-12-19T00:05:43+01:00",
                                "value": None,
                            },
                            {
                                "id": "Q2hhbXAtNTU0OTIwOA==",
                                "label": "Nom de la structure",
                                "stringValue": "Structure calédonienne",
                                "updatedAt": "2025-12-18T23:51:09+01:00",
                                "value": "Structure calédonienne",
                            },
                            {
                                "id": "Q2hhbXAtNTU0OTIwOQ==",
                                "label": "RIDET",
                                "stringValue": "1305804001",
                                "updatedAt": "2025-12-18T23:51:22+01:00",
                                "value": "1234567001",
                            },
                            {
                                "id": "Q2hhbXAtNzAwNTA5",
                                "label": "Vos informations bancaires",
                                "stringValue": "",
                                "updatedAt": "2025-12-19T00:05:43+01:00",
                                "value": None,
                            },
                            {
                                "id": "Q2hhbXAtMzU3MzQ1Mw==",
                                "label": "Intitulé du compte bancaire",
                                "stringValue": "Compte bancaire calédonien",
                                "updatedAt": "2025-12-18T23:51:41+01:00",
                                "value": "Compte bancaire calédonien",
                            },
                            {
                                "id": "Q2hhbXAtMzUyNzIy",
                                "label": "IBAN",
                                "stringValue": "NC2014889000000988000000100",
                                "updatedAt": "2025-12-18T23:51:57+01:00",
                                "value": "NC2014889000000988000000100",
                            },
                            {
                                "id": "Q2hhbXAtODU2ODE4",
                                "label": "RIB",
                                "stringValue": None,
                                "updatedAt": "2025-12-18T23:52:50+01:00",
                                "file": {
                                    "url": "https://static.demarches-simplifiees.fr:443/v1/AUTH_123/ds_activestorage_backup/2025/12/18/zM/123?temp_url_sig=123&temp_url_expires=1766161890&filename=RIB-NC.pdf&inline",
                                    "checksum": "NU3qXgqOEeHd4W7R0c+aLQ==",
                                    "contentType": "application/pdf",
                                    "filename": "RIB-NC.pdf",
                                },
                            },
                            {
                                "id": "Q2hhbXAtODU2NzEz",
                                "label": "Identité du responsable légal",
                                "stringValue": "",
                                "updatedAt": "2025-12-19T00:05:43+01:00",
                                "value": None,
                            },
                            {
                                "id": "Q2hhbXAtMzYzMDA4Ng==",
                                "label": "Carte d'identité (recto) ou passeport du responsable légal de la structure",
                                "stringValue": "",
                                "updatedAt": "2025-12-19T00:05:17+01:00",
                            },
                            {
                                "id": "Q2hhbXAtMzYxMzExMA==",
                                "label": "Structure",
                                "stringValue": "",
                                "updatedAt": "2025-12-19T00:05:43+01:00",
                                "value": None,
                            },
                            {
                                "id": "Q2hhbXAtMzQ4NTEwOA==",
                                "label": "Nature juridique de votre structure",
                                "stringValue": "Entreprise individuelle",
                                "updatedAt": "2025-12-18T23:54:07+01:00",
                                "value": "Entreprise individuelle",
                            },
                            {
                                "id": "Q2hhbXAtNTczODY2OQ==",
                                "label": "Extrait KBIS ou Avis d'immatriculation au Répertoire d'identification des Entreprises et des Etablissements ou Certificat d'Immatriculation au Répertoire des Métiers",
                                "stringValue": None,
                                "updatedAt": "2025-12-19T00:05:33+01:00",
                                "file": {
                                    "url": "https://static.demarches-simplifiees.fr:443/v1/AUTH_123/ds_activestorage_backup/2025/12/19/Hk/123?temp_url_sig=123&temp_url_expires=1766161890&filename=avis-1234567-001.pdf&inline",
                                    "checksum": "jios79XJB787bPzTABCAOQ==",
                                    "contentType": "application/pdf",
                                    "filename": "avis-1234567-001.pdf",
                                },
                            },
                            {
                                "id": "Q2hhbXAtMzQ4NTE2Mg==",
                                "label": "Déclaration sur l'honneur",
                                "stringValue": "",
                                "updatedAt": "2025-12-19T00:05:43+01:00",
                                "value": None,
                            },
                            {
                                "id": "Q2hhbXAtMzQ4NTE1Nw==",
                                "label": "Je déclare sur l’honneur disposer de l'autorisation du responsable légal pour effectuer cette démarche",
                                "stringValue": "true",
                                "updatedAt": "2025-12-18T23:58:12+01:00",
                            },
                            {
                                "id": "Q2hhbXAtMzQ4NTE3OQ==",
                                "label": "Je déclare que l'ensemble des réponses et documents fournis sont corrects et authentiques",
                                "stringValue": "true",
                                "updatedAt": "2025-12-18T23:58:15+01:00",
                            },
                        ],
                        "annotations": [
                            {
                                "id": "Q2hhbXAtOTE1NDg5",
                                "label": "En attente de validation de structure",
                                "updatedAt": "2025-12-18T23:50:42+01:00",
                                "stringValue": "false",
                                "checked": False,
                            },
                            {
                                "id": "Q2hhbXAtMjc2NDk5MA==",
                                "label": "En attente de validation ADAGE",
                                "updatedAt": "2025-12-18T23:50:42+01:00",
                                "stringValue": "false",
                                "checked": False,
                            },
                            {
                                "id": "Q2hhbXAtMzYzMDA5NA==",
                                "label": "Motif de mise en attente du dossier",
                                "updatedAt": "2025-12-18T23:50:42+01:00",
                                "stringValue": "",
                                "value": None,
                            },
                            {
                                "id": "Q2hhbXAtMzYzMDA5NQ==",
                                "label": "Remarques Tech/Produit",
                                "updatedAt": "2025-12-18T23:50:42+01:00",
                                "stringValue": "",
                                "value": None,
                            },
                        ],
                        "messages": [
                            {
                                "email": "contact.demarche.numerique@example.com",
                                "createdAt": "2025-12-19T00:05:43+01:00",
                            },
                            {
                                "email": "contact.demarche.numerique@example.com",
                                "createdAt": "2025-12-19T09:51:45+01:00",
                            },
                            {
                                "email": "contact.demarche.numerique@example.com",
                                "createdAt": "2025-12-19T09:51:48+01:00",
                            },
                        ],
                    }
                ],
            }
        }
    }
