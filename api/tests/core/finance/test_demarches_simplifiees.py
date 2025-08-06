import pytest

from pcapi.core.finance.ds import parse_raw_bank_info_data


VENUE_DMS_TOKEN_FIELD_WITHOUT_PRO_PREFIX = {
    "id": "Q2hhbXAtMjY3NDMyMQ==",
    "label": "Identifiant du lieu",
    "stringValue": "50a7536a21c8",
    "value": "50a7536a21c8",
}
VENUE_DMS_TOKEN_FIELD_WITH_PRO_PREFIX = {
    "id": "Q2hhbXAtMjY3NDMyMQ==",
    "label": "Identifiant du lieu",
    "stringValue": "PRO-50a7536a21c8",
    "value": "PRO-50a7536a21c8",
}
VENUE_FIELD = {
    "siret": "43839119500056",
}
EXPECTED_RESULT_V4 = {
    "application_id": 1234,
    "status": "en_construction",
    "updated_at": "2021-11-12T14:51:42+01:00",
    "dms_token": "50a7536a21c8",
    "firstname": "John",
    "lastname": "Doe",
    "phone_number": "0102030405",
    "iban": "FR7630001007941234567890185",
    "bic": "QSDFGH8Z",
    "error_annotation_id": "InterestingId",
    "error_annotation_value": "",
    "venue_url_annotation_id": "AnotherInterestingId",
    "venue_url_annotation_value": "",
    "dossier_id": "Q2zzbXAtNzgyODAw",
    "last_pending_correction_date": None,
}


class ParseRawBankInfoDataTest:
    @pytest.mark.parametrize(
        "procedure_version, etablissement, identifiant_du_lieu, expected_result, prenom, nom",
        [
            (4, None, VENUE_DMS_TOKEN_FIELD_WITHOUT_PRO_PREFIX, EXPECTED_RESULT_V4, "Prénom", "nom"),
            (4, VENUE_FIELD, VENUE_DMS_TOKEN_FIELD_WITHOUT_PRO_PREFIX, EXPECTED_RESULT_V4, "prénom", "nom"),
            (4, None, VENUE_DMS_TOKEN_FIELD_WITH_PRO_PREFIX, EXPECTED_RESULT_V4, "Prénom", "Nom"),
            (4, VENUE_FIELD, VENUE_DMS_TOKEN_FIELD_WITH_PRO_PREFIX, EXPECTED_RESULT_V4, "prénom", "nom"),
        ],
    )
    def test_parsing_works(self, procedure_version, etablissement, identifiant_du_lieu, expected_result, prenom, nom):
        champs = [
            {"id": "Q2hhbXAtNDA3ODk1", "label": "Mes informations", "stringValue": "", "value": None},
            {"id": "Q2hhbXAtNDA3ODg5", "label": prenom, "stringValue": "John", "value": "John"},
            {"id": "Q2hhbXAtNDA3ODkw", "label": nom, "stringValue": "Doe", "value": "Doe"},
            {
                "id": "Q2hhbXAtNDA3ODky",
                "label": "Mon numéro de téléphone",
                "stringValue": "01 02 03 04 05",
                "value": "0102030405",
            },
            {
                "id": "Q2hhbXAtODU2NzEz",
                "label": "Informations relatives au responsable légal et à ma délégation de gestion financière",
                "stringValue": "",
                "value": None,
            },
            {
                "file": {
                    "checksum": "dIUGYwKmurZztL/3bL/m/g==",
                    "contentType": "application/pdf",
                    "filename": "test.pdf",
                    "url": "http://localhost/somefile",
                },
                "id": "Q2hhbXAtMzUyNzI1",
                "label": "Responsable légal de votre structure ou de votre lieu",
                "stringValue": "",
            },
            {
                "file": {
                    "checksum": "dIUGYwKmurZztL/3bL/m/g==",
                    "contentType": "application/pdf",
                    "filename": "test.pdf",
                    "url": "http://https://localhost/somefile",
                },
                "id": "Q2hhbXAtMjA2MTE4Nw==",
                "label": "Document d'identité de ce dirigeant (daté, certifié conforme et signé)",
                "stringValue": "",
            },
            {
                "file": None,
                "id": "Q2hhbXAtNzAwNTUy",
                "label": "Si vous n'êtes pas le responsable légal de votre structure ou de votre lieu",
                "stringValue": "",
            },
            {
                "id": "Q2hhbXAtMzUyNzIz",
                "label": "Informations sur le lieu à rembourser",
                "stringValue": "",
                "value": None,
            },
            {
                "etablissement": etablissement,
                "id": "Q2hhbXAtNzgyODAw",
                "label": "SIRET",
                "stringValue": "43839119500056",
            },
            {"id": "Q2hhbXAtNzAwNTA5", "label": "Vos coordonnées bancaires", "stringValue": "", "value": None},
            {
                "id": "Q2hhbXAtMzUyNzIy",
                "label": "IBAN",
                "stringValue": "FR7630001007941234567890185",
                "value": "FR7630001007941234567890185",
            },
            {"id": "Q2hhbXAtMzUyNzI3", "label": "BIC", "stringValue": "QSDFGH8Z", "value": "QSDFGH8Z"},
            {
                "file": {
                    "checksum": "dIUGYwKmurZztL/3bL/m/g==",
                    "contentType": "application/pdf",
                    "filename": "test.pdf",
                    "url": "http://localhost/somefile",
                },
                "id": "Q2hhbXAtODU2ODE4",
                "label": "RIB",
                "stringValue": "",
            },
            {
                "id": "Q2hhbXAtMjY0MjE3Nw==",
                "label": "Devilish label write by a user *nom* that could match a regex",
                "stringValue": "",
                "file": {
                    "url": "http://url.com",
                    "checksum": "KKrLwnPYU67Z7CD1B4vIDA==",
                    "contentType": "application/pdf",
                    "filename": "file.pdf",
                },
            },
        ]
        champs.insert(3, identifiant_du_lieu)
        input_data = {
            "id": "Q2zzbXAtNzgyODAw",
            "number": 1234,
            "champs": champs,
            "dateDerniereModification": "2021-11-12T14:51:42+01:00",
            "dateDerniereCorrectionEnAttente": None,
            "state": "en_construction",
            "annotations": [
                {"label": "Nouvelle annotation texte", "id": "OtherId"},
                {"label": "Erreur traitement pass Culture", "id": "InterestingId", "stringValue": ""},
            ],
        }
        input_data["annotations"].append({"label": "URL du lieu", "id": "AnotherInterestingId", "stringValue": ""})

        result = parse_raw_bank_info_data(input_data, procedure_version)

        assert result == expected_result
