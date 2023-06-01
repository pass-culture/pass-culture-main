from datetime import datetime
from unittest.mock import patch

import pytest

from pcapi.core.finance.models import BankInformationStatus
from pcapi.domain.demarches_simplifiees import ApplicationDetail
from pcapi.domain.demarches_simplifiees import get_venue_bank_information_application_details_by_application_id
from pcapi.domain.demarches_simplifiees import parse_raw_bank_info_data

from tests.connector_creators.demarches_simplifiees_creators import get_bank_info_response_procedure_v2


@patch("pcapi.connectors.dms.api.DMSGraphQLClient")
class GetVenueBankInformationApplicationDetailsByApplicationIdTest:
    @pytest.mark.parametrize(
        "annotation",
        [
            {"label": "Erreur traitement pass Culture", "id": "INTERESTINGID"},
            # "Nouvelle annotation Texte" is a default annotation created by DMS
            {"label": "Nouvelle annotation Texte", "id": "OTHERID"},
        ],
    )
    def test_retrieve_and_format_all_fields_v2(self, DMSGraphQLClient, annotation):
        # Given
        updated_at = datetime(2020, 1, 3)
        DMSGraphQLClient.return_value.get_bank_info.return_value = get_bank_info_response_procedure_v2(annotation)

        # When
        application_details = get_venue_bank_information_application_details_by_application_id("8", 3)

        # Then
        assert isinstance(application_details, ApplicationDetail)
        assert application_details.siren == "123456789"
        assert application_details.status == BankInformationStatus.ACCEPTED
        assert application_details.application_id == 8
        assert application_details.iban == "FR7630007000111234567890144"
        assert application_details.bic == "SOGEFRPP"
        assert application_details.siret == "12345678900014"
        assert application_details.dossier_id == "Q2zzbXAtNzgyODAw"
        assert application_details.modification_date == updated_at
        assert application_details.error_annotation_id == (
            annotation["id"] if annotation["label"] == "Erreur traitement pass Culture" else None
        )


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
EXPECTED_RESULT_WITH_SIRET_V3 = {
    "status": "en_construction",
    "updated_at": "2021-11-12T14:51:42+01:00",
    "firstname": "John",
    "lastname": "Doe",
    "phone_number": "0102030405",
    "siret": "43839119500056",
    "siren": "438391195",
    "iban": "FR7630001007941234567890185",
    "bic": "QSDFGH8Z",
    "error_annotation_id": "InterestingId",
    "dossier_id": "Q2zzbXAtNzgyODAw",
    "venue_url_annotation_id": None,
}
EXPECTED_RESULT_V4 = {
    "status": "en_construction",
    "updated_at": "2021-11-12T14:51:42+01:00",
    "dms_token": "50a7536a21c8",
    "firstname": "John",
    "lastname": "Doe",
    "phone_number": "0102030405",
    "iban": "FR7630001007941234567890185",
    "bic": "QSDFGH8Z",
    "error_annotation_id": "InterestingId",
    "venue_url_annotation_id": "AnotherInterestingId",
    "dossier_id": "Q2zzbXAtNzgyODAw",
}


class ParseRawBankInfoDataTest:
    @pytest.mark.parametrize(
        "procedure_version, etablissement, identifiant_du_lieu, expected_result",
        [
            (3, VENUE_FIELD, None, EXPECTED_RESULT_WITH_SIRET_V3),
            (4, None, VENUE_DMS_TOKEN_FIELD_WITHOUT_PRO_PREFIX, EXPECTED_RESULT_V4),
            (4, VENUE_FIELD, VENUE_DMS_TOKEN_FIELD_WITHOUT_PRO_PREFIX, EXPECTED_RESULT_V4),
            (4, None, VENUE_DMS_TOKEN_FIELD_WITH_PRO_PREFIX, EXPECTED_RESULT_V4),
            (4, VENUE_FIELD, VENUE_DMS_TOKEN_FIELD_WITH_PRO_PREFIX, EXPECTED_RESULT_V4),
        ],
    )
    def test_parsing_works(self, procedure_version, etablissement, identifiant_du_lieu, expected_result):
        champs = [
            {"id": "Q2hhbXAtNDA3ODk1", "label": "Mes informations", "stringValue": "", "value": None},
            {"id": "Q2hhbXAtNDA3ODg5", "label": "Mon prénom", "stringValue": "John", "value": "John"},
            {"id": "Q2hhbXAtNDA3ODkw", "label": "Mon nom", "stringValue": "Doe", "value": "Doe"},
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
        ]
        if identifiant_du_lieu:
            champs.insert(3, identifiant_du_lieu)
        input_data = {
            "dossier": {
                "id": "Q2zzbXAtNzgyODAw",
                "champs": champs,
                "dateDerniereModification": "2021-11-12T14:51:42+01:00",
                "state": "en_construction",
                "annotations": [
                    {"label": "Nouvelle annotation texte", "id": "OtherId"},
                    {"label": "Erreur traitement pass Culture", "id": "InterestingId"},
                ],
            }
        }
        if procedure_version == 4:
            input_data["dossier"]["annotations"].append({"label": "URL du lieu", "id": "AnotherInterestingId"})

        result = parse_raw_bank_info_data(input_data, procedure_version)

        assert result == expected_result
