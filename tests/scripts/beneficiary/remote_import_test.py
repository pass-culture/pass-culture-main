from datetime import date
from datetime import datetime
from datetime import timedelta
from unittest.mock import ANY
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.connectors.api_demarches_simplifiees import DMSGraphQLClient
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.testing import override_features
from pcapi.core.users import api as users_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import PhoneValidationStatusType
from pcapi.core.users.models import User
from pcapi.models import ApiErrors
from pcapi.models import BeneficiaryImport
from pcapi.models import BeneficiaryImportStatus
from pcapi.models import ImportStatus
import pcapi.notifications.push.testing as push_testing
from pcapi.scripts.beneficiary import remote_import

from tests.scripts.beneficiary.fixture import APPLICATION_DETAIL_STANDARD_RESPONSE
from tests.scripts.beneficiary.fixture import make_graphql_application
from tests.scripts.beneficiary.fixture import make_new_application
from tests.scripts.beneficiary.fixture import make_new_beneficiary_application_details
from tests.scripts.beneficiary.fixture import make_new_stranger_application
from tests.scripts.beneficiary.fixture_dms_with_selfie import APPLICATION_DETAIL_STANDARD_RESPONSE_AFTER_GENERALISATION


NOW = datetime.utcnow()


@pytest.mark.usefixtures("db_session")
class RunTest:
    @patch("pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee")
    @patch("pcapi.scripts.beneficiary.remote_import.find_applications_ids_to_retry")
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    @patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
    def test_should_retrieve_applications_from_new_procedure_id(
        self,
        process_beneficiary_application,
        get_details,
        find_applications_ids_to_retry,
        get_closed_application_ids_for_demarche_simplifiee,
    ):
        # given
        get_closed_application_ids_for_demarche_simplifiee.return_value = [123, 456, 789]
        find_applications_ids_to_retry.return_value = []

        get_details.side_effect = [
            make_new_beneficiary_application_details(123, "closed"),
            make_new_beneficiary_application_details(456, "closed"),
            make_new_beneficiary_application_details(789, "closed"),
        ]

        # when
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        assert get_closed_application_ids_for_demarche_simplifiee.call_count == 1
        get_closed_application_ids_for_demarche_simplifiee.assert_called_with(6712558, ANY)

    @patch("pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee")
    @patch("pcapi.scripts.beneficiary.remote_import.find_applications_ids_to_retry")
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    @patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
    def test_all_applications_are_processed_once(
        self,
        process_beneficiary_application,
        get_details,
        find_applications_ids_to_retry,
        get_closed_application_ids_for_demarche_simplifiee,
    ):
        # given
        get_closed_application_ids_for_demarche_simplifiee.return_value = [123, 456, 789]
        find_applications_ids_to_retry.return_value = []

        users_factories.UserFactory(email="email1@example.com")
        users_factories.UserFactory(email="email2@example.com")
        users_factories.UserFactory(email="email3@example.com")
        get_details.side_effect = [
            make_new_beneficiary_application_details(123, "closed", email="email1@example.com"),
            make_new_beneficiary_application_details(456, "closed", email="email2@example.com"),
            make_new_beneficiary_application_details(789, "closed", email="email3@example.com"),
        ]

        # when
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        assert process_beneficiary_application.call_count == 3

    @patch("pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee")
    @patch("pcapi.scripts.beneficiary.remote_import.find_applications_ids_to_retry")
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    @patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
    def test_applications_to_retry_are_processed(
        self,
        process_beneficiary_application,
        get_details,
        find_applications_ids_to_retry,
        get_closed_application_ids_for_demarche_simplifiee,
    ):
        # given
        get_closed_application_ids_for_demarche_simplifiee.return_value = [123]
        find_applications_ids_to_retry.return_value = [456, 789]

        users_factories.UserFactory(email="email1@example.com")
        users_factories.UserFactory(email="email2@example.com")
        users_factories.UserFactory(email="email3@example.com")

        get_details.side_effect = [
            make_new_beneficiary_application_details(123, "closed", email="email1@example.com"),
            make_new_beneficiary_application_details(456, "closed", email="email2@example.com"),
            make_new_beneficiary_application_details(789, "closed", email="email3@example.com"),
        ]

        # when
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        assert process_beneficiary_application.call_count == 3

    @patch("pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee")
    @patch("pcapi.scripts.beneficiary.remote_import.find_applications_ids_to_retry")
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    @patch("pcapi.scripts.beneficiary.remote_import.parse_beneficiary_information")
    def test_an_error_status_is_saved_when_an_application_is_not_parsable(
        self,
        mocked_parse_beneficiary_information,
        get_details,
        find_applications_ids_to_retry,
        get_closed_application_ids_for_demarche_simplifiee,
    ):
        # given
        get_closed_application_ids_for_demarche_simplifiee.return_value = [123]
        find_applications_ids_to_retry.return_value = []

        get_details.side_effect = [make_new_beneficiary_application_details(123, "closed")]
        mocked_parse_beneficiary_information.side_effect = [Exception()]

        # when
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.currentStatus == ImportStatus.ERROR
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.detail == "Le dossier 123 contient des erreurs et a été ignoré - Procedure 6712558"

    @patch("pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee")
    @patch("pcapi.scripts.beneficiary.remote_import.find_applications_ids_to_retry")
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    @patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
    def test_application_with_known_application_id_are_not_processed(
        self,
        process_beneficiary_application,
        get_details,
        find_applications_ids_to_retry,
        get_closed_application_ids_for_demarche_simplifiee,
    ):
        # given
        get_closed_application_ids_for_demarche_simplifiee.return_value = [123]
        find_applications_ids_to_retry.return_value = []
        created_import = users_factories.BeneficiaryImportFactory(applicationId=123, source="demarches_simplifiees")
        users_factories.BeneficiaryImportStatusFactory(
            status=ImportStatus.CREATED,
            beneficiaryImport=created_import,
            author=None,
        )
        get_details.return_value = make_new_beneficiary_application_details(123, "closed")

        # when
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        process_beneficiary_application.assert_not_called()

    @patch("pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee")
    @patch("pcapi.scripts.beneficiary.remote_import.find_applications_ids_to_retry")
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    @patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
    def test_application_with_known_email_and_already_beneficiary_are_saved_as_rejected(
        self,
        process_beneficiary_application,
        get_details,
        find_applications_ids_to_retry,
        get_closed_application_ids_for_demarche_simplifiee,
    ):
        # given
        get_closed_application_ids_for_demarche_simplifiee.return_value = [123]
        find_applications_ids_to_retry.return_value = []

        # same user, but different
        get_details.return_value = make_new_beneficiary_application_details(123, "closed", email="john.doe@example.com")
        users_factories.BeneficiaryGrant18Factory(email="john.doe@example.com")

        # when
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.currentStatus == ImportStatus.REJECTED
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.detail == "Compte existant avec cet email"
        assert beneficiary_import.beneficiary == None
        process_beneficiary_application.assert_not_called()

    @override_features(FORCE_PHONE_VALIDATION=False)
    @patch("pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee")
    @patch("pcapi.scripts.beneficiary.remote_import.find_applications_ids_to_retry")
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    @patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
    def test_beneficiary_is_created_with_procedure_id(
        self,
        process_beneficiary_application,
        get_details,
        find_applications_ids_to_retry,
        get_closed_application_ids_for_demarche_simplifiee,
    ):
        # given
        get_closed_application_ids_for_demarche_simplifiee.return_value = [123]
        find_applications_ids_to_retry.return_value = []

        get_details.side_effect = [make_new_beneficiary_application_details(123, "closed")]

        applicant = users_factories.UserFactory(firstName="Doe", lastName="John", email="john.doe@test.com")

        # when
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        process_beneficiary_application.assert_called_with(
            information=fraud_models.DMSContent(
                last_name="Doe",
                first_name="John",
                civility="Mme",
                email="john.doe@test.com",
                application_id=123,
                procedure_id=6712558,
                department="67",
                phone="0123456789",
                birth_date=date(2000, 5, 1),
                activity="Étudiant",
                address="35 Rue Saint Denis 93130 Noisy-le-Sec",
                postal_code="67200",
            ),
            procedure_id=6712558,
            preexisting_account=applicant,
        )


class ProcessBeneficiaryApplicationTest:
    @override_features(FORCE_PHONE_VALIDATION=False)
    @pytest.mark.usefixtures("db_session")
    def test_new_beneficiaries_are_recorded_with_deposit(self, app):
        # given
        eighteen_years_in_the_past = datetime.now() - relativedelta(years=18, months=4)
        information = fraud_models.DMSContent(
            department="93",
            last_name="Doe",
            first_name="Jane",
            birth_date=eighteen_years_in_the_past,
            email="jane.doe@example.com",
            phone="0612345678",
            postal_code="93130",
            address="11 Rue du Test",
            application_id=123,
            procedure_id=123456,
            civility="Mme",
            activity="Étudiant",
        )

        # when
        remote_import.process_beneficiary_application(information=information, procedure_id=123456)

        # then
        first = User.query.first()
        assert first.email == "jane.doe@example.com"
        assert first.wallet_balance == 300
        assert first.civility == "Mme"
        assert first.activity == "Étudiant"

        assert len(push_testing.requests) == 1

    @pytest.mark.usefixtures("db_session")
    def test_an_import_status_is_saved_if_beneficiary_is_created(self, app):
        # given
        eighteen_years_in_the_past = datetime.now() - relativedelta(years=18, months=4)
        information = fraud_models.DMSContent(
            department="93",
            last_name="Doe",
            first_name="Jane",
            birth_date=eighteen_years_in_the_past,
            email="jane.doe@example.com",
            phone="0612345678",
            postal_code="93130",
            address="11 Rue du Test",
            application_id=123,
            procedure_id=123456,
            civility="Mme",
            activity="Étudiant",
        )

        # when
        remote_import.process_beneficiary_application(information=information, procedure_id=123456)

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.beneficiary.email == "jane.doe@example.com"
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert beneficiary_import.applicationId == 123

    @patch("pcapi.scripts.beneficiary.remote_import.create_beneficiary_from_application")
    @patch("pcapi.scripts.beneficiary.remote_import.repository")
    @patch("pcapi.scripts.beneficiary.remote_import.user_emails.send_activation_email")
    @pytest.mark.usefixtures("db_session")
    def test_account_activation_email_is_sent(
        self, send_activation_email, mock_repository, create_beneficiary_from_application, app
    ):
        # given
        information = fraud_factories.DMSContentFactory(application_id=123)

        create_beneficiary_from_application.return_value = users_factories.BeneficiaryGrant18Factory.build()

        # when
        remote_import.process_beneficiary_application(information=information, procedure_id=123456)

        # then
        send_activation_email.assert_called()

    @patch("pcapi.scripts.beneficiary.remote_import.create_beneficiary_from_application")
    @patch("pcapi.scripts.beneficiary.remote_import.repository")
    @patch("pcapi.scripts.beneficiary.remote_import.user_emails.send_activation_email")
    @pytest.mark.usefixtures("db_session")
    def test_error_is_collected_if_beneficiary_could_not_be_saved(
        self, send_activation_email, mock_repository, create_beneficiary_from_application, app
    ):
        # given
        information = fraud_factories.DMSContentFactory(application_id=123)
        create_beneficiary_from_application.side_effect = [User()]
        mock_repository.save.side_effect = [ApiErrors({"postalCode": ["baaaaad value"]})]

        # when
        remote_import.process_beneficiary_application(information, procedure_id=123456)

        # then
        send_activation_email.assert_not_called()
        assert len(push_testing.requests) == 0


class ParseBeneficiaryInformationTest:
    class BeforeGeneralOpenningTest:
        def test_personal_information_of_beneficiary_are_parsed_from_application_detail(self):
            # when
            information = remote_import.parse_beneficiary_information(
                APPLICATION_DETAIL_STANDARD_RESPONSE, procedure_id=201201
            )

            # then
            assert information.last_name == "Doe"
            assert information.first_name == "John"
            assert information.birth_date == date(2000, 5, 1)
            assert information.civility == "M."
            assert information.email == "john.doe@test.com"
            assert information.phone == "0123456789"
            assert information.postal_code == "93130"
            assert information.application_id == 123

        def test_handles_two_digits_department_code(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", department_code="67 - Bas-Rhin")

            # when
            information = remote_import.parse_beneficiary_information(application_detail, procedure_id=201201)

            # then
            assert information.department == "67"

        def test_handles_three_digits_department_code(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", department_code="973 - Guyane")

            # when
            information = remote_import.parse_beneficiary_information(application_detail, procedure_id=201201)

            # then
            assert information.department == "973"

        def test_handles_uppercased_mixed_digits_and_letter_department_code(self):
            # given
            application_detail = make_new_beneficiary_application_details(
                1, "closed", department_code="2B - Haute-Corse"
            )

            # when
            information = remote_import.parse_beneficiary_information(application_detail, procedure_id=201201)

            # then
            assert information.department == "2B"

        def test_handles_lowercased_mixed_digits_and_letter_department_code(self):
            # given
            application_detail = make_new_beneficiary_application_details(
                1, "closed", department_code="2a - Haute-Corse"
            )

            # when
            information = remote_import.parse_beneficiary_information(application_detail, procedure_id=201201)

            # then
            assert information.department == "2a"

        def test_handles_department_code_with_another_label(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", department_code="67 - Bas-Rhin")
            for field in application_detail["dossier"]["champs"]:
                label = field["type_de_champ"]["libelle"]
                if label == "Veuillez indiquer votre département":
                    field["type_de_champ"]["libelle"] = "Veuillez indiquer votre département de résidence"

            # when
            information = remote_import.parse_beneficiary_information(application_detail, procedure_id=201201)

            # then
            assert information.department == "67"

        def test_handles_postal_codes_wrapped_with_spaces(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", postal_code="  93130  ")

            # when
            information = remote_import.parse_beneficiary_information(application_detail, procedure_id=201201)

            # then
            assert information.postal_code == "93130"

        def test_handles_postal_codes_containing_spaces(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", postal_code="67 200")

            # when
            information = remote_import.parse_beneficiary_information(application_detail, procedure_id=201201)

            # then
            assert information.postal_code == "67200"

        def test_handles_postal_codes_containing_city_name(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", postal_code="67 200 Strasbourg ")

            # when
            information = remote_import.parse_beneficiary_information(application_detail, procedure_id=201201)

            # then
            assert information.postal_code == "67200"

        def test_handles_civility_parsing(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", civility="M.")

            # when
            information = remote_import.parse_beneficiary_information(application_detail, procedure_id=201201)

            # then
            assert information.civility == "M."

        def test_handles_activity_parsing(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed")

            # when
            information = remote_import.parse_beneficiary_information(application_detail, procedure_id=201201)

            # then
            assert information.activity == "Étudiant"

        def test_handles_activity_even_if_activity_is_not_filled(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", activity=None)

            # when
            information = remote_import.parse_beneficiary_information(application_detail, procedure_id=201201)

            # then
            assert information.activity is None

    class AfterGeneralOpenningTest:
        def test_personal_information_of_beneficiary_are_parsed_from_application_detail(self):
            # when
            information = remote_import.parse_beneficiary_information(
                APPLICATION_DETAIL_STANDARD_RESPONSE_AFTER_GENERALISATION, procedure_id=201201
            )

            # then
            assert information.last_name == "Doe"
            assert information.first_name == "John"
            assert information.birth_date == date(2000, 5, 1)
            assert information.civility == "M."
            assert information.email == "john.doe@test.com"
            assert information.phone == "0123456789"
            assert information.postal_code == "93130"
            assert information.application_id == 123
            assert information.procedure_id == 201201

        @pytest.mark.parametrize("possible_value", ["0123456789", " 0123456789", "0123456789 ", " 0123456789 "])
        def test_beneficiary_information_id_piece_number_with_spaces(self, possible_value):
            application_detail = make_new_beneficiary_application_details(1, "closed", id_piece_number=possible_value)
            information = remote_import.parse_beneficiary_information(application_detail, procedure_id=123123)
            assert information.id_piece_number == "0123456789"

        @pytest.mark.parametrize("possible_value", ["0123456789", " 0123456789", "0123456789 ", " 0123456789 "])
        def test_beneficiary_information_id_piece_number_with_spaces_graphql(self, possible_value):
            application_detail = make_graphql_application(1, "closed", id_piece_number=possible_value)
            information = remote_import.parse_beneficiary_information_graphql(application_detail, procedure_id=123123)

            assert information.id_piece_number == "0123456789"

        @patch.object(DMSGraphQLClient, "get_applications_with_details")
        def test_new_procedure(self, get_applications_with_details):
            raw_data = make_new_application()
            content = remote_import.parse_beneficiary_information_graphql(raw_data, 32)
            assert content.last_name == "VALGEAN"
            assert content.first_name == "Jean"
            assert content.civility == "M"
            assert content.email == "jean.valgean@example.com"
            assert content.application_id == 5718303
            assert content.procedure_id == 32
            assert content.department == None
            assert content.birth_date == date(1984, 12, 19)
            assert content.phone == "0601010101"
            assert content.postal_code == "92700"
            assert content.activity == "Employé"
            assert content.address == "32 rue des sapins gris 21350 l'îsle à dent"
            assert content.id_piece_number == "F9GFAL123"

        @patch.object(DMSGraphQLClient, "get_applications_with_details")
        def test_new_procedure_for_stranger_residents(self, get_applications_with_details):
            raw_data = make_new_stranger_application()
            content = remote_import.parse_beneficiary_information_graphql(raw_data, 32)
            assert content.last_name == "VALGEAN"
            assert content.first_name == "Jean"
            assert content.civility == "M"
            assert content.email == "jean.valgean@example.com"
            assert content.application_id == 5742994
            assert content.procedure_id == 32
            assert content.department == None
            assert content.birth_date == date(2000, 12, 18)
            assert content.phone == "0601010101"
            assert content.postal_code == "92700"
            assert content.activity == "Employé"
            assert content.address == "32 rue des sapins gris 21350 l'îsle à dent"
            assert content.id_piece_number == "K682T8YLO"

    class ParsingErrorsTest:
        def test_beneficiary_information_postalcode_error(self):
            application_detail = make_new_beneficiary_application_details(1, "closed", postal_code="Strasbourg")
            with pytest.raises(ValueError) as exc_info:
                remote_import.parse_beneficiary_information(application_detail, procedure_id=123123)

            assert exc_info.value.errors["postal_code"] == "Strasbourg"

        @pytest.mark.parametrize("possible_value", ["Passeport n: XXXXX", "sans numéro"])
        def test_beneficiary_information_id_piece_number_error(self, possible_value):
            application_detail = make_new_beneficiary_application_details(1, "closed", id_piece_number=possible_value)
            with pytest.raises(ValueError) as exc_info:
                remote_import.parse_beneficiary_information(application_detail, procedure_id=123123)

            assert exc_info.value.errors["id_piece_number"] == possible_value


@pytest.mark.usefixtures("db_session")
class RunIntegrationTest:
    EMAIL = "john.doe@example.com"
    BENEFICIARY_BIRTH_DATE = date.today() - timedelta(days=6752)  # ~18.5 years

    def _get_details(self, application_id: int, procedure_id: int, token: str):
        return {
            "dossier": {
                "individual": {
                    "nom": "doe",
                    "prenom": "john",
                    "civilite": "M",
                },
                "email": self.EMAIL,
                "id": application_id,
                "champs": [
                    {"type_de_champ": {"libelle": "Veuillez indiquer votre département :"}, "value": "93"},
                    {
                        "type_de_champ": {"libelle": "Quelle est votre date de naissance"},
                        "value": self.BENEFICIARY_BIRTH_DATE.strftime("%Y-%m-%d"),
                    },
                    {
                        "type_de_champ": {"libelle": "Quel est votre numéro de téléphone"},
                        "value": "0102030405",
                    },
                    {
                        "type_de_champ": {"libelle": "Quel est le code postal de votre commune de résidence ?"},
                        "value": "93450",
                    },
                    {
                        "type_de_champ": {"libelle": "Quelle est votre adresse de résidence"},
                        "value": "11 Rue du Test",
                    },
                    {"type_de_champ": {"libelle": "Veuillez indiquer votre statut"}, "value": "Etudiant"},
                    {
                        "type_de_champ": {"libelle": "Quel est le numéro de la pièce que vous venez de saisir ?"},
                        "value": "1234123412",
                    },
                ],
            }
        }

    def _get_all_applications_ids(self, procedure_id: str, token: str):
        return [123]

    @override_features(FORCE_PHONE_VALIDATION=False)
    @patch(
        "pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee",
    )
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    def test_import_user(self, get_application_details, get_closed_application_ids_for_demarche_simplifiee):
        # when
        get_closed_application_ids_for_demarche_simplifiee.side_effect = self._get_all_applications_ids
        get_application_details.side_effect = self._get_details
        user = users_factories.UserFactory(firstName="john", lastName="doe", email="john.doe@example.com")

        remote_import.run(
            procedure_id=6712558,
        )

        # then
        assert User.query.count() == 1
        user = User.query.first()
        assert user.firstName == "john"
        assert user.postalCode == "93450"
        assert user.address == "11 Rue du Test"
        assert user.phoneNumber == "0102030405"

        assert BeneficiaryImport.query.count() == 1

        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.source == "demarches_simplifiees"
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.beneficiary == user
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert len(push_testing.requests) == 1

    @patch(
        "pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee",
    )
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    def test_import_user_requires_pre_creation(
        self, get_application_details, get_closed_application_ids_for_demarche_simplifiee
    ):
        # when
        get_closed_application_ids_for_demarche_simplifiee.side_effect = self._get_all_applications_ids
        get_application_details.side_effect = self._get_details

        remote_import.run(
            procedure_id=6712558,
        )
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.source == "demarches_simplifiees"
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.currentStatus == ImportStatus.ERROR
        assert beneficiary_import.statuses[-1].detail == "Aucun utilisateur trouvé pour l'email john.doe@example.com"

    @override_features(FORCE_PHONE_VALIDATION=True)
    @patch(
        "pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee",
    )
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    def test_import_does_not_make_user_beneficiary(
        self, get_application_details, get_closed_application_ids_for_demarche_simplifiee
    ):
        """
        Test that an imported user without a validated phone number, and the
        FORCE_PHONE_VALIDATION feature flag activated, cannot become
        beneficiary.
        """
        date_of_birth = self.BENEFICIARY_BIRTH_DATE.strftime("%Y-%m-%dT%H:%M:%S")

        # Create a user that has validated its email and phone number, meaning it
        # should become beneficiary.
        user = users_factories.UserFactory(
            email=self.EMAIL,
            isBeneficiary=False,
            isEmailValidated=True,
            dateOfBirth=date_of_birth,
            phoneValidationStatus=None,
        )
        get_closed_application_ids_for_demarche_simplifiee.side_effect = self._get_all_applications_ids
        get_application_details.side_effect = self._get_details

        # when
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        assert User.query.count() == 1
        user = User.query.first()

        assert user.firstName == "john"
        assert user.postalCode == "93450"
        assert user.address == "11 Rue du Test"
        assert not user.isBeneficiary

        assert len(user.beneficiaryFraudChecks) == 1
        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.DMS
        fraud_content = fraud_models.DMSContent(**fraud_check.resultContent)
        assert fraud_content.birth_date == user.dateOfBirth.date()
        assert fraud_content.address == "11 Rue du Test"

        fraud_result = user.beneficiaryFraudResult
        assert fraud_result.status == fraud_models.FraudStatus.KO
        assert "Le n° de téléphone de l'utilisateur n'est pas validé" in fraud_result.reason
        assert BeneficiaryImport.query.count() == 1
        beneficiary_import = BeneficiaryImport.query.first()

        assert beneficiary_import.source == "demarches_simplifiees"
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.beneficiary == user
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert len(push_testing.requests) == 1

        assert len(push_testing.requests) == 1

    @patch(
        "pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee",
    )
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    def test_import_makes_user_beneficiary(
        self, get_application_details, get_closed_application_ids_for_demarche_simplifiee
    ):
        """
        Test that an existing user with its phone number validated can become
        beneficiary.
        """
        date_of_birth = self.BENEFICIARY_BIRTH_DATE.strftime("%Y-%m-%dT%H:%M:%S")

        # Create a user that has validated its email and phone number, meaning it
        # should become beneficiary.
        user = users_factories.UserFactory(
            email=self.EMAIL,
            isBeneficiary=False,
            isEmailValidated=True,
            dateOfBirth=date_of_birth,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )
        get_closed_application_ids_for_demarche_simplifiee.side_effect = self._get_all_applications_ids
        get_application_details.side_effect = self._get_details

        # when
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        assert User.query.count() == 1
        user = User.query.first()

        assert user.firstName == "john"
        assert user.postalCode == "93450"
        assert user.address == "11 Rue du Test"
        assert user.isBeneficiary
        assert user.phoneNumber == "0102030405"
        assert user.idPieceNumber == "1234123412"

        assert len(user.beneficiaryFraudChecks) == 1
        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.DMS
        fraud_content = fraud_models.DMSContent(**fraud_check.resultContent)
        assert fraud_content.birth_date == user.dateOfBirth.date()
        assert fraud_content.address == "11 Rue du Test"

        assert BeneficiaryImport.query.count() == 1
        beneficiary_import = BeneficiaryImport.query.first()

        assert beneficiary_import.source == "demarches_simplifiees"
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.beneficiary == user
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert len(push_testing.requests) == 1

        assert len(push_testing.requests) == 1

    @override_features(FORCE_PHONE_VALIDATION=False)
    @patch(
        "pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee",
    )
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    def test_import_duplicated_user(self, get_application_details, get_closed_application_ids_for_demarche_simplifiee):
        # given
        user = users_factories.BeneficiaryGrant18Factory(
            firstName="john",
            lastName="doe",
            email="john.doe@example.com",
            postalCode="93450",
            phoneNumber="0102030405",
            idPieceNumber="121316",
            isEmailValidated=True,
            isActive=True,
        )

        created_import = users_factories.BeneficiaryImportFactory(
            applicationId=123, beneficiary=user, source="demarches_simplifiees"
        )
        users_factories.BeneficiaryImportStatusFactory(
            status=ImportStatus.CREATED,
            beneficiaryImport=created_import,
            author=None,
        )
        get_closed_application_ids_for_demarche_simplifiee.side_effect = self._get_all_applications_ids
        get_application_details.side_effect = self._get_details

        # when
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        assert User.query.count() == 1
        assert BeneficiaryImport.query.count() == 1
        user = User.query.get(user.id)
        assert len(user.beneficiaryFraudChecks) == 1
        assert user.beneficiaryFraudChecks[0].type == fraud_models.FraudCheckType.DMS

        assert user.beneficiaryFraudResult.status == fraud_models.FraudStatus.KO
        assert "L'utilisateur est déjà bénéficiaire" in user.beneficiaryFraudResult.reason

        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.source == "demarches_simplifiees"
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.beneficiary == user
        assert beneficiary_import.currentStatus == ImportStatus.REJECTED

    @override_features(FORCE_PHONE_VALIDATION=False)
    @patch(
        "pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee",
    )
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    def test_import_with_existing_id_card(
        self, get_application_details, get_closed_application_ids_for_demarche_simplifiee, mocker
    ):
        user = users_factories.UserFactory(
            email=self.EMAIL,
            isBeneficiary=False,
            isEmailValidated=True,
            dateOfBirth=self.BENEFICIARY_BIRTH_DATE.strftime("%Y-%m-%dT%H:%M:%S"),
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
            idPieceNumber="1234123412",
        )
        get_closed_application_ids_for_demarche_simplifiee.side_effect = self._get_all_applications_ids
        get_application_details.side_effect = self._get_details

        # when
        process_mock = mocker.patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        assert process_mock.call_count == 0
        assert User.query.count() == 1
        assert BeneficiaryImport.query.count() == 1
        user = User.query.first()
        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.DMS
        fraud_content = fraud_models.DMSContent(**fraud_check.resultContent)
        assert fraud_content.birth_date == user.dateOfBirth.date()
        assert fraud_content.address == "11 Rue du Test"

        beneficiary_import = BeneficiaryImport.query.first()
        beneficiary_import_status = BeneficiaryImportStatus.query.first()
        assert beneficiary_import.source == "demarches_simplifiees"
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.beneficiary == user
        assert beneficiary_import.currentStatus == ImportStatus.REJECTED
        assert beneficiary_import_status.beneficiaryImportId == beneficiary_import.id
        assert beneficiary_import_status.detail == f"Nr de piece déjà utilisé par {user.id}"

    @override_features(FORCE_PHONE_VALIDATION=False)
    @patch(
        "pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee",
    )
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    def test_import_with_existing_id_card_with_existing_applicant(
        self, get_application_details, get_closed_application_ids_for_demarche_simplifiee, mocker
    ):
        applicant = users_factories.UserFactory(email=self.EMAIL, isBeneficiary=False)
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            isEmailValidated=True,
            dateOfBirth=self.BENEFICIARY_BIRTH_DATE.strftime("%Y-%m-%dT%H:%M:%S"),
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
            idPieceNumber="1234123412",
        )
        get_closed_application_ids_for_demarche_simplifiee.side_effect = self._get_all_applications_ids
        get_application_details.side_effect = self._get_details

        # when
        process_mock = mocker.patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        assert process_mock.call_count == 0
        assert BeneficiaryImport.query.count() == 1
        fraud_check = applicant.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.DMS

        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.source == "demarches_simplifiees"
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.beneficiary == applicant
        assert beneficiary_import.currentStatus == ImportStatus.REJECTED

        assert applicant.beneficiaryFraudResult.status == fraud_models.FraudStatus.SUSPICIOUS
        assert (
            f"Le n° de cni 1234123412 est déjà pris par l'utilisateur {beneficiary.id}"
            in applicant.beneficiaryFraudResult.reason
        )

    @override_features(FORCE_PHONE_VALIDATION=False)
    @patch(
        "pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee",
    )
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    def test_import_native_app_user(self, get_application_details, get_closed_application_ids_for_demarche_simplifiee):
        # given
        user = users_api.create_account(
            email=self.EMAIL,
            password="aBc123@567",
            birthdate=self.BENEFICIARY_BIRTH_DATE,
            is_email_validated=True,
            send_activation_mail=False,
            phone_number="0607080900",
        )
        push_testing.reset_requests()
        get_closed_application_ids_for_demarche_simplifiee.side_effect = self._get_all_applications_ids
        get_application_details.side_effect = self._get_details

        # when
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        assert User.query.count() == 1

        user = User.query.first()
        assert user.firstName == "john"
        assert user.postalCode == "93450"

        # Since the User already exists, the phone number should not be updated
        # during the import process
        assert user.phoneNumber == "0607080900"

        assert BeneficiaryImport.query.count() == 1

        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.source == "demarches_simplifiees"
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.beneficiary == user
        assert beneficiary_import.currentStatus == ImportStatus.CREATED

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2016025

        assert len(push_testing.requests) == 1
        assert push_testing.requests[0]["attribute_values"]["u.is_beneficiary"]

    @patch("pcapi.scripts.beneficiary.remote_import.user_emails.send_activation_email")
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    @patch(
        "pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee",
    )
    @patch("pcapi.scripts.beneficiary.remote_import.parse_beneficiary_information")
    def test_beneficiary_is_not_created_if_duplicates_are_found(
        self,
        parse_beneficiary_info,
        get_closed_application_ids_for_dms,
        get_applications_details,
        send_activation_email,
    ):
        # given
        eighteen_years_in_the_past = datetime.now() - relativedelta(years=18, months=4)
        information = fraud_factories.DMSContentFactory(
            department="93",
            last_name="Doe",
            first_name="Jane",
            birth_date=eighteen_years_in_the_past,
            email="jane.doe@example.com",
            phone="0612345678",
            postal_code="93130",
            application_id=123,
            civility="M",
            activity="Étudiant",
        )
        parse_beneficiary_info.return_value = information
        get_closed_application_ids_for_dms.return_value = [information.application_id]
        applicant = users_factories.UserFactory(
            isBeneficiary=False,
            dateOfBirth=information.birth_date,
            firstName=information.first_name,
            lastName=information.last_name,
            email=information.email,
        )
        beneficiary = users_factories.BeneficiaryGrant18Factory(
            dateOfBirth=information.birth_date,
            firstName=information.first_name,
            lastName=information.last_name,
        )

        # when
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        send_activation_email.assert_not_called()
        assert len(push_testing.requests) == 0

        beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=123).first()
        assert beneficiary_import.currentStatus == ImportStatus.DUPLICATE

        assert applicant.beneficiaryFraudResult.status == fraud_models.FraudStatus.SUSPICIOUS
        assert f"Duplicat de l'utilisateur {beneficiary.id}" in applicant.beneficiaryFraudResult.reason

    @patch("pcapi.domain.user_emails.send_accepted_as_beneficiary_email")
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    @patch(
        "pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee",
    )
    @patch("pcapi.scripts.beneficiary.remote_import.find_applications_ids_to_retry")
    @patch("pcapi.scripts.beneficiary.remote_import.parse_beneficiary_information")
    def test_beneficiary_is_created_if_duplicates_are_found_but_id_is_in_retry_list(
        self,
        parse_beneficiary_info,
        find_applications_ids_to_retryretry_ids,
        get_closed_application_ids_for_dms,
        get_applications_details,
        send_accepted_as_beneficiary_email,
    ):
        # given
        eighteen_years_in_the_past = datetime.now() - relativedelta(years=18, months=4)
        information = fraud_factories.DMSContentFactory(
            department="93",
            last_name="Doe",
            first_name="Jane",
            birth_date=eighteen_years_in_the_past,
            email="jane.doe@example.com",
            phone="0612345678",
            postal_code="93130",
            address="11 Rue du Test",
            application_id=123,
            civility="Mme",
            activity="Étudiant",
        )
        users_factories.UserFactory(
            email="unexistant@example.com", dateOfBirth=eighteen_years_in_the_past, firstName="Jane", lastName="Doe"
        )
        users_factories.UserFactory(firstName="Jane", lastName="Doe", email="jane.doe@example.com")
        find_applications_ids_to_retryretry_ids.return_value = [123]
        parse_beneficiary_info.return_value = information
        # beware to not add this application twice
        get_closed_application_ids_for_dms.return_value = []

        # when
        remote_import.run(
            procedure_id=6712558,
        )

        # then
        beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=123).first()
        send_accepted_as_beneficiary_email.assert_called()
        assert beneficiary_import.currentStatus == ImportStatus.CREATED

    @patch(
        "pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee",
    )
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    def test_dms_application_value_error(self, application_details, get_closed_application_ids_for_demarche_simplifiee):
        get_closed_application_ids_for_demarche_simplifiee.side_effect = self._get_all_applications_ids

        application_details.return_value = make_new_beneficiary_application_details(
            application_id=1, state="closed", postal_code="Strasbourg", id_piece_number="121314"
        )
        remote_import.run(
            procedure_id=6712558,
        )

        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.currentStatus == ImportStatus.ERROR
        assert beneficiary_import.sourceId == 6712558
        assert (
            beneficiary_import.statuses[0].detail
            == "Erreur dans les données soumises dans le dossier DMS : 'id_piece_number' (121314),'postal_code' (Strasbourg)"
        )
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 3124925

    @patch(
        "pcapi.scripts.beneficiary.remote_import.get_closed_application_ids_for_demarche_simplifiee",
    )
    @patch("pcapi.scripts.beneficiary.remote_import.get_application_details")
    def test_dms_application_value_error_known_user(
        self, application_details, get_closed_application_ids_for_demarche_simplifiee
    ):
        user = users_factories.UserFactory()
        get_closed_application_ids_for_demarche_simplifiee.side_effect = self._get_all_applications_ids
        application_details.return_value = make_new_beneficiary_application_details(
            application_id=1, state="closed", postal_code="Strasbourg", id_piece_number="121314", email=user.email
        )
        remote_import.run(
            procedure_id=6712558,
        )

        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.currentStatus == ImportStatus.ERROR
        assert beneficiary_import.sourceId == 6712558
        assert (
            beneficiary_import.statuses[0].detail
            == "Erreur dans les données soumises dans le dossier DMS : 'id_piece_number' (121314),'postal_code' (Strasbourg)"
        )
        assert beneficiary_import.beneficiary == user
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 3124925


@pytest.mark.usefixtures("db_session")
class GraphQLSourceProcessApplicationTest:
    def test_parsing(self):
        application_id = 123123
        application_details = make_graphql_application(application_id, "closed")

        beneficiary_information = remote_import.parse_beneficiary_information_graphql(
            application_details,
            procedure_id=123,
        )
        assert beneficiary_information.last_name == "Doe"
        assert beneficiary_information.first_name == "John"
        assert beneficiary_information.civility == "Mme"
        assert beneficiary_information.email == "young.individual@example.com"
        assert beneficiary_information.application_id == application_id
        assert beneficiary_information.procedure_id == 123
        assert beneficiary_information.department == "67"
        assert beneficiary_information.birth_date == date(2002, 5, 12)
        assert beneficiary_information.phone == "0783442376"
        assert beneficiary_information.postal_code == "67200"
        assert beneficiary_information.activity == "Étudiant"
        assert beneficiary_information.address == "3 La Bigotais 22800 Saint-Donan"
        assert beneficiary_information.id_piece_number == "123123123"

    def test_process_application_user_already_created(self):
        user = users_factories.UserFactory()
        application_id = 123123
        application_details = make_graphql_application(application_id, "closed", email=user.email)
        # fixture
        remote_import.process_application(
            123123, 4234, application_details, [], parsing_function=remote_import.parse_beneficiary_information_graphql
        )
        assert BeneficiaryImport.query.count() == 1
        import_status = BeneficiaryImport.query.one_or_none()
        assert import_status.currentStatus == ImportStatus.CREATED
        assert import_status.beneficiary == user

    @patch.object(DMSGraphQLClient, "get_applications_with_details")
    def test_run(self, get_applications_with_details):
        user = users_factories.UserFactory()
        application_id = 123123

        get_applications_with_details.return_value = [
            make_graphql_application(application_id, "closed", email=user.email)
        ]
        remote_import.run(123123, use_graphql_api=True)

        import_status = BeneficiaryImport.query.one_or_none()

        assert import_status.currentStatus == ImportStatus.CREATED
        assert import_status.beneficiary == user

    @patch.object(DMSGraphQLClient, "get_applications_with_details")
    def test_dms_application_value_error(self, get_applications_with_details):
        user = users_factories.UserFactory()
        get_applications_with_details.return_value = [
            make_graphql_application(
                application_id=1, state="closed", postal_code="Strasbourg", id_piece_number="121314", email=user.email
            )
        ]

        remote_import.run(procedure_id=6712558, use_graphql_api=True)

        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.currentStatus == ImportStatus.ERROR
        assert beneficiary_import.sourceId == 6712558
        assert beneficiary_import.beneficiary == user
        assert (
            beneficiary_import.statuses[0].detail
            == "Erreur dans les données soumises dans le dossier DMS : 'id_piece_number' (121314),'postal_code' (Strasbourg)"
        )

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 3124925

    @patch.object(DMSGraphQLClient, "get_applications_with_details")
    def test_avoid_reimporting_already_imported_user(self, get_applications_with_details):
        procedure_id = 42
        user = users_factories.UserFactory()
        already_imported_user = users_factories.BeneficiaryGrant18Factory()
        users_factories.BeneficiaryImportFactory(
            beneficiary=already_imported_user, applicationId=2, sourceId=procedure_id
        )
        get_applications_with_details.return_value = [
            make_graphql_application(application_id=1, state="closed", email=user.email),
            make_graphql_application(
                application_id=2,
                state="closed",
                email=already_imported_user.email,
            ),
        ]

        remote_import.run(procedure_id=procedure_id, use_graphql_api=True)

        imports = BeneficiaryImport.query.all()
        assert len(imports) == 2
        assert len(mails_testing.outbox) == 1
        sent_email = mails_testing.outbox[0]
        assert sent_email.sent_data["To"] == user.email
        assert sent_email.sent_data["Mj-campaign"] == "confirmation-credit"
