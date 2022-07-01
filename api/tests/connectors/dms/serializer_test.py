from datetime import date
from datetime import datetime
from unittest.mock import patch

import pytest

from pcapi.connectors.dms import models as dms_models
from pcapi.connectors.dms import serializer as dms_serializer
from pcapi.core.users import models as users_models

from tests.scripts.beneficiary import fixture


class ParseBeneficiaryInformationTest:
    @pytest.mark.parametrize(
        "postal_code,expected_code",
        [
            ("  93130  ", "93130"),
            ("67 200", "67200"),
            ("67 200 Strasbourg ", "67200"),
        ],
    )
    def test_handles_postal_codes(self, postal_code, expected_code):
        application_detail = fixture.make_parsed_graphql_application(1, "accepte", postal_code=postal_code)
        information, _ = dms_serializer.parse_beneficiary_information_graphql(application_detail)
        assert information.postal_code == expected_code

    def test_handles_civility_parsing(self):
        # given
        application_detail = fixture.make_parsed_graphql_application(1, "accepte", civility="M")

        # when
        information, _ = dms_serializer.parse_beneficiary_information_graphql(application_detail)

        # then
        assert information.civility == users_models.GenderEnum.M

    @pytest.mark.parametrize("activity", ["Étudiant", None])
    def test_handles_activity(self, activity):
        application_detail = fixture.make_parsed_graphql_application(1, "accepte", activity=activity)
        information, _ = dms_serializer.parse_beneficiary_information_graphql(application_detail)
        assert information.activity == activity

    @pytest.mark.parametrize("possible_value", ["0123456789", " 0123456789", "0123456789 ", " 0123456789 "])
    def test_beneficiary_information_id_piece_number_with_spaces_graphql(self, possible_value):
        application_detail = fixture.make_parsed_graphql_application(1, "accepte", id_piece_number=possible_value)
        information, _ = dms_serializer.parse_beneficiary_information_graphql(application_detail)

        assert information.id_piece_number == "0123456789"

    def test_new_procedure(self):
        raw_data = fixture.make_new_application()
        content, _ = dms_serializer.parse_beneficiary_information_graphql(dms_models.DmsApplicationResponse(**raw_data))
        assert content.last_name == "VALGEAN"
        assert content.first_name == "Jean"
        assert content.civility == users_models.GenderEnum.M
        assert content.email == "jean.valgean@example.com"
        assert content.application_number == 5718303
        assert content.procedure_id == 32
        assert content.department == None
        assert content.birth_date == date(2004, 12, 19)
        assert content.phone == "0601010101"
        assert content.postal_code == "92700"
        assert content.activity == "Employé"
        assert content.address == "32 rue des sapins gris 21350 l'îsle à dent"
        assert content.id_piece_number == "F9GFAL123"

    def test_new_procedure_for_stranger_residents(self):
        raw_data = fixture.make_new_stranger_application()
        content, _ = dms_serializer.parse_beneficiary_information_graphql(dms_models.DmsApplicationResponse(**raw_data))
        assert content.last_name == "VALGEAN"
        assert content.first_name == "Jean"
        assert content.civility == users_models.GenderEnum.M
        assert content.email == "jean.valgean@example.com"
        assert content.application_number == 5742994
        assert content.procedure_id == 32
        assert content.department == None
        assert content.birth_date == date(2006, 5, 12)
        assert content.phone == "0601010101"
        assert content.postal_code == "92700"
        assert content.activity == "Employé"
        assert content.address == "32 rue des sapins gris 21350 l'îsle à dent"
        assert content.id_piece_number == "K682T8YLO"

    def test_processed_datetime_none(self):
        raw_data = fixture.make_graphql_application(1, "en_construction", processed_datetime=None)
        content, _ = dms_serializer.parse_beneficiary_information_graphql(dms_models.DmsApplicationResponse(**raw_data))
        assert content.processed_datetime is None

    def test_processed_datetime_not_none(self):
        raw_data = fixture.make_graphql_application(1, "accepte")
        content, _ = dms_serializer.parse_beneficiary_information_graphql(dms_models.DmsApplicationResponse(**raw_data))
        assert content.processed_datetime == datetime(2020, 5, 13, 8, 41, 21)

    @pytest.mark.parametrize(
        "dms_activity, expected_activity",
        [
            ("Lycéen", users_models.ActivityEnum.HIGH_SCHOOL_STUDENT.value),
            ("Etudiant", users_models.ActivityEnum.STUDENT.value),
            ("Employé", users_models.ActivityEnum.EMPLOYEE.value),
            ("En recherche d'emploi ou chômeur", users_models.ActivityEnum.UNEMPLOYED.value),
            (
                "Inactif (ni en emploi ni au chômage), En incapacité de travailler",
                users_models.ActivityEnum.INACTIVE.value,
            ),
            ("Apprenti", users_models.ActivityEnum.APPRENTICE.value),
            ("Alternant", users_models.ActivityEnum.APPRENTICE_STUDENT.value),
            ("Volontaire en service civique rémunéré", users_models.ActivityEnum.VOLUNTEER.value),
        ],
    )
    def test_activity_accepted_values(self, dms_activity, expected_activity):
        raw_data = fixture.make_graphql_application(1, "accepte", activity=dms_activity)
        content, _ = dms_serializer.parse_beneficiary_information_graphql(dms_models.DmsApplicationResponse(**raw_data))
        assert content.activity == expected_activity

    @patch("pcapi.connectors.dms.serializer.logger.error")
    def test_activity_unknown_values(self, mocked_logger):
        raw_data = fixture.make_graphql_application(1, "accepte", activity="invalid")
        content, _ = dms_serializer.parse_beneficiary_information_graphql(dms_models.DmsApplicationResponse(**raw_data))
        assert content.activity == None
        mocked_logger.assert_called_once_with("Unknown activity value for application %s: %s", 1, "invalid")
