from pcapi.connectors.dms.models import GraphQLApplicationStates


def get_bank_info_response_procedure_v2(annotation: dict):
    return {
        "dossier": {
            "id": "Q2zzbXAtNzgyODAw",
            "champs": [
                {
                    "etablissement": {
                        "entreprise": {
                            "siren": "123456789",
                        },
                        "siret": "12345678900014",
                    },
                    "id": "Q2hhbXAtNzgyODAw",
                    "label": "SIRET",
                    "stringValue": "12345678900014",
                },
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
            "state": "accepte",
            "annotations": [annotation],
        },
    }


def get_bank_info_response_procedure_v4(
    dms_token: str = "1234567890abcdef",
    etablissement: dict | None = None,
    state: str = GraphQLApplicationStates.accepted.value,
    annotations: dict | None = None,
    dossier_id: str = "Q2zzbXAtNzgyODAw",
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
    annotations = annotations or [{"label": "Nouvelle annotation Texte", "id": "OTHERID"}]
    result = {
        "dossier": {
            "id": dossier_id,
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
            "state": state,
            "annotations": annotations,
        },
    }
    return result
