from datetime import date
from datetime import datetime
from datetime import timedelta
from unittest.mock import ANY
from unittest.mock import Mock
from unittest.mock import patch

from mailjet_rest import Client
import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.testing import override_features
from pcapi.core.users import api as users_api
from pcapi.core.users.models import PhoneValidationStatusType
from pcapi.core.users.models import User
from pcapi.model_creators.generic_creators import create_user
from pcapi.models import ApiErrors
from pcapi.models import BeneficiaryImport
from pcapi.models import ImportStatus
import pcapi.notifications.push.testing as push_testing
from pcapi.repository import repository
from pcapi.scripts.beneficiary import remote_import
from pcapi.scripts.beneficiary.remote_import import parse_beneficiary_information

from tests.scripts.beneficiary.fixture import APPLICATION_DETAIL_STANDARD_RESPONSE
from tests.scripts.beneficiary.fixture import make_new_beneficiary_application_details
from tests.scripts.beneficiary.fixture_dms_with_selfie import APPLICATION_DETAIL_STANDARD_RESPONSE_AFTER_GENERALISATION


NOW = datetime.utcnow()
ONE_WEEK_AGO = NOW - timedelta(days=7)


class RunTest:
    @patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
    def test_should_retrieve_applications_from_new_procedure_id(self, process_beneficiary_application):
        # given
        get_all_application_ids = Mock(return_value=[123, 456, 789])
        find_applications_ids_to_retry = Mock(return_value=[])

        get_details = Mock()
        get_details.side_effect = [
            make_new_beneficiary_application_details(123, "closed"),
            make_new_beneficiary_application_details(456, "closed"),
            make_new_beneficiary_application_details(789, "closed"),
        ]

        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=False)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            procedure_id=6712558,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created,
        )

        # then
        assert get_all_application_ids.call_count == 1
        get_all_application_ids.assert_called_with(6712558, ANY, ANY)

    @patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
    def test_all_applications_are_processed_once(self, process_beneficiary_application):
        # given
        get_all_application_ids = Mock(return_value=[123, 456, 789])
        find_applications_ids_to_retry = Mock(return_value=[])

        get_details = Mock()
        get_details.side_effect = [
            make_new_beneficiary_application_details(123, "closed"),
            make_new_beneficiary_application_details(456, "closed"),
            make_new_beneficiary_application_details(789, "closed"),
        ]

        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=False)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            procedure_id=6712558,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created,
        )

        # then
        assert process_beneficiary_application.call_count == 3

    @patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
    def test_applications_to_retry_are_processed(self, process_beneficiary_application):
        # given
        get_all_application_ids = Mock(return_value=[123])
        find_applications_ids_to_retry = Mock(return_value=[456, 789])

        get_details = Mock()
        get_details.side_effect = [
            make_new_beneficiary_application_details(123, "closed"),
            make_new_beneficiary_application_details(456, "closed"),
            make_new_beneficiary_application_details(789, "closed"),
        ]

        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=False)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            procedure_id=6712558,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created,
        )

        # then
        assert process_beneficiary_application.call_count == 3

    @patch("pcapi.scripts.beneficiary.remote_import.parse_beneficiary_information")
    @pytest.mark.usefixtures("db_session")
    def test_an_error_status_is_saved_when_an_application_is_not_parsable(
        self, mocked_parse_beneficiary_information, app
    ):
        # given
        get_all_application_ids = Mock(return_value=[123])
        find_applications_ids_to_retry = Mock(return_value=[])

        get_details = Mock(side_effect=[make_new_beneficiary_application_details(123, "closed")])
        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=False)
        mocked_parse_beneficiary_information.side_effect = [Exception()]

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            procedure_id=6712558,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created,
        )

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.currentStatus == ImportStatus.ERROR
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.detail == "Le dossier 123 contient des erreurs et a été ignoré - Procedure 6712558"

    @patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
    def test_application_with_known_application_id_are_not_processed(self, process_beneficiary_application):
        # given
        get_all_application_ids = Mock(return_value=[123, 456])
        find_applications_ids_to_retry = Mock(return_value=[])

        get_details = Mock(return_value=make_new_beneficiary_application_details(123, "closed"))
        user = User()
        user.email = "john.doe@example.com"
        has_already_been_imported = Mock(return_value=True)
        has_already_been_created = Mock(return_value=False)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            procedure_id=6712558,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created,
        )

        # then
        process_beneficiary_application.assert_not_called()

    @patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
    @pytest.mark.usefixtures("db_session")
    def test_application_with_known_email_are_saved_as_rejected(self, process_beneficiary_application, app):
        # given
        get_all_application_ids = Mock(return_value=[123])
        find_applications_ids_to_retry = Mock(return_value=[])

        get_details = Mock(return_value=make_new_beneficiary_application_details(123, "closed"))
        user = User()
        user.email = "john.doe@example.com"
        user.isBeneficiary = True
        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=user)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            procedure_id=6712558,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created,
        )

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.currentStatus == ImportStatus.REJECTED
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.detail == "Compte existant avec cet email"
        process_beneficiary_application.assert_not_called()

    @override_features(FORCE_PHONE_VALIDATION=False)
    @patch("pcapi.scripts.beneficiary.remote_import.process_beneficiary_application")
    @pytest.mark.usefixtures("db_session")
    def test_beneficiary_is_created_with_procedure_id(self, process_beneficiary_application, app):
        # given
        get_all_application_ids = Mock(return_value=[123])
        find_applications_ids_to_retry = Mock(return_value=[])

        get_details = Mock(side_effect=[make_new_beneficiary_application_details(123, "closed")])
        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=False)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            procedure_id=6712558,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created,
        )

        # then
        process_beneficiary_application.assert_called_with(
            information={
                "last_name": "Doe",
                "first_name": "John",
                "civility": "Mme",
                "email": "john.doe@test.com",
                "application_id": 123,
                "department": "67",
                "phone": "0123456789",
                "birth_date": datetime(2000, 5, 1, 0, 0),
                "activity": "Étudiant",
                "address": "35 Rue Saint Denis 93130 Noisy-le-Sec",
                "postal_code": "67200",
            },
            error_messages=[],
            new_beneficiaries=[],
            retry_ids=[],
            procedure_id=6712558,
            preexisting_account=False,
        )


class ProcessBeneficiaryApplicationTest:
    @override_features(FORCE_PHONE_VALIDATION=False)
    @pytest.mark.usefixtures("db_session")
    def test_new_beneficiaries_are_recorded_with_deposit(self, app):
        # given
        app.mailjet_client = Mock(spec=Client)
        app.mailjet_client.send = Mock()
        information = {
            "department": "93",
            "last_name": "Doe",
            "first_name": "Jane",
            "birth_date": datetime(2000, 5, 1),
            "email": "jane.doe@example.com",
            "phone": "0612345678",
            "postal_code": "93130",
            "address": "11 Rue du Test",
            "application_id": 123,
            "civility": "Mme",
            "activity": "Étudiant",
        }

        # when
        remote_import.process_beneficiary_application(
            information, error_messages=[], new_beneficiaries=[], retry_ids=[], procedure_id=123456
        )

        # then
        first = User.query.first()
        assert first.email == "jane.doe@example.com"
        assert first.wallet_balance == 300
        assert first.civility == "Mme"
        assert first.activity == "Étudiant"

        assert push_testing.requests == [
            {
                "attribute_values": {
                    "date(u.date_created)": first.dateCreated.strftime("%Y-%m-%dT%H:%M:%S"),
                    "date(u.date_of_birth)": "2000-05-01T00:00:00",
                    "date(u.deposit_expiration_date)": first.deposit.expirationDate.strftime("%Y-%m-%dT%H:%M:%S"),
                    "u.credit": 30000,
                    "u.departement_code": "93",
                    "u.is_beneficiary": True,
                    "u.marketing_push_subscription": True,
                    "u.postal_code": "93130",
                },
                "user_id": first.id,
            }
        ]

    @pytest.mark.usefixtures("db_session")
    def test_an_import_status_is_saved_if_beneficiary_is_created(self, app):
        # given
        app.mailjet_client = Mock(spec=Client)
        app.mailjet_client.send = Mock()
        information = {
            "department": "93",
            "last_name": "Doe",
            "first_name": "Jane",
            "birth_date": datetime(2000, 5, 1),
            "email": "jane.doe@example.com",
            "phone": "0612345678",
            "postal_code": "93130",
            "address": "11 Rue du Test",
            "application_id": 123,
            "civility": "Mme",
            "activity": "Étudiant",
        }

        # when
        remote_import.process_beneficiary_application(
            information, error_messages=[], new_beneficiaries=[], retry_ids=[], procedure_id=123456
        )

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.beneficiary.email == "jane.doe@example.com"
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert beneficiary_import.applicationId == 123

    @patch("pcapi.scripts.beneficiary.remote_import.create_beneficiary_from_application")
    @patch("pcapi.scripts.beneficiary.remote_import.repository")
    @patch("pcapi.scripts.beneficiary.remote_import.send_activation_email")
    @pytest.mark.usefixtures("db_session")
    def test_account_activation_email_is_sent(
        self, send_activation_email, mock_repository, create_beneficiary_from_application, app
    ):
        # given
        information = {
            "department": "93",
            "last_name": "Doe",
            "first_name": "Jane",
            "birth_date": datetime(2000, 5, 1),
            "email": "jane.doe@example.com",
            "phone": "0612345678",
            "postal_code": "93130",
            "application_id": 123,
            "civility": "Mme",
            "activity": "Étudiant",
        }

        create_beneficiary_from_application.return_value = create_user()

        # when
        remote_import.process_beneficiary_application(
            information, error_messages=[], new_beneficiaries=[], retry_ids=[], procedure_id=123456
        )

        # then
        send_activation_email.assert_called()

    @patch("pcapi.scripts.beneficiary.remote_import.create_beneficiary_from_application")
    @patch("pcapi.scripts.beneficiary.remote_import.repository")
    @patch("pcapi.scripts.beneficiary.remote_import.send_activation_email")
    @pytest.mark.usefixtures("db_session")
    def test_error_is_collected_if_beneficiary_could_not_be_saved(
        self, send_activation_email, mock_repository, create_beneficiary_from_application, app
    ):
        # given
        information = {
            "department": "93",
            "last_name": "Doe",
            "first_name": "Jane",
            "birth_date": datetime(2000, 5, 1),
            "email": "jane.doe@example.com",
            "phone": "0612345678",
            "postal_code": "93130",
            "application_id": 123,
            "civility": "Mme",
            "activity": "Étudiant",
        }
        create_beneficiary_from_application.side_effect = [User()]
        mock_repository.save.side_effect = [ApiErrors({"postalCode": ["baaaaad value"]})]
        new_beneficiaries = []
        error_messages = []

        # when
        remote_import.process_beneficiary_application(
            information, error_messages, new_beneficiaries, retry_ids=[], procedure_id=123456
        )

        # then
        send_activation_email.assert_not_called()
        assert len(push_testing.requests) == 0
        assert error_messages == ['{\n  "postalCode": [\n    "baaaaad value"\n  ]\n}']
        assert not new_beneficiaries

    @patch("pcapi.scripts.beneficiary.remote_import.repository")
    @patch("pcapi.scripts.beneficiary.remote_import.send_activation_email")
    @pytest.mark.usefixtures("db_session")
    def test_beneficiary_is_not_created_if_duplicates_are_found(self, send_activation_email, mock_repository, app):
        # given
        information = {
            "department": "93",
            "last_name": "Doe",
            "first_name": "Jane",
            "birth_date": datetime(2000, 5, 1),
            "email": "jane.doe@example.com",
            "phone": "0612345678",
            "postal_code": "93130",
            "application_id": 123,
            "civility": "Mme",
            "activity": "Étudiant",
        }
        existing_user = create_user(date_of_birth=datetime(2000, 5, 1), first_name="Jane", last_name="Doe")
        repository.save(existing_user)

        # when
        remote_import.process_beneficiary_application(
            information, error_messages=[], new_beneficiaries=[], retry_ids=[], procedure_id=123456
        )

        # then
        send_activation_email.assert_not_called()
        assert len(push_testing.requests) == 0
        mock_repository.save.assert_not_called()
        beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=123).first()
        assert beneficiary_import.currentStatus == ImportStatus.DUPLICATE

    @patch("pcapi.scripts.beneficiary.remote_import.send_activation_email")
    @pytest.mark.usefixtures("db_session")
    def test_beneficiary_is_created_if_duplicates_are_found_but_id_is_in_retry_list(self, send_activation_email, app):
        # given
        information = {
            "department": "93",
            "last_name": "Doe",
            "first_name": "Jane",
            "birth_date": datetime(2000, 5, 1),
            "email": "jane.doe@example.com",
            "phone": "0612345678",
            "postal_code": "93130",
            "address": "11 Rue du Test",
            "application_id": 123,
            "civility": "Mme",
            "activity": "Étudiant",
        }
        existing_user = create_user(date_of_birth=datetime(2000, 5, 1), first_name="Jane", last_name="Doe")
        repository.save(existing_user)
        retry_ids = [123]

        # when
        remote_import.process_beneficiary_application(
            information, error_messages=[], new_beneficiaries=[], retry_ids=retry_ids, procedure_id=123456
        )

        # then
        send_activation_email.assert_called()
        beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=123).first()
        assert beneficiary_import.currentStatus == ImportStatus.CREATED

    @patch("pcapi.scripts.beneficiary.remote_import.get_beneficiary_duplicates")
    @pytest.mark.usefixtures("db_session")
    def test_an_import_status_is_saved_if_beneficiary_is_a_duplicate(self, mock_get_beneficiary_duplicates, app):
        # given
        information = {
            "department": "93",
            "last_name": "Doe",
            "first_name": "Jane",
            "birth_date": datetime(2000, 5, 1),
            "email": "jane.doe@example.com",
            "phone": "0612345678",
            "postal_code": "93130",
            "application_id": 123,
            "civility": "Mme",
            "activity": "Étudiant",
        }
        mock_get_beneficiary_duplicates.return_value = [create_user(idx=11), create_user(idx=22)]

        # when
        remote_import.process_beneficiary_application(
            information, error_messages=[], new_beneficiaries=[], retry_ids=[], procedure_id=123456
        )

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.currentStatus == ImportStatus.DUPLICATE
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.detail == "Utilisateur en doublon : 11, 22"


class ParseBeneficiaryInformationTest:
    class BeforeGeneralOpenningTest:
        def test_personal_information_of_beneficiary_are_parsed_from_application_detail(self):
            # when
            information = parse_beneficiary_information(APPLICATION_DETAIL_STANDARD_RESPONSE)

            # then
            assert information["last_name"] == "Doe"
            assert information["first_name"] == "John"
            assert information["birth_date"] == datetime(2000, 5, 1)
            assert information["civility"] == "M."
            assert information["email"] == "john.doe@test.com"
            assert information["phone"] == "0123456789"
            assert information["postal_code"] == "93130"
            assert information["application_id"] == 123

        def test_handles_two_digits_department_code(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", department_code="67 - Bas-Rhin")

            # when
            information = parse_beneficiary_information(application_detail)

            # then
            assert information["department"] == "67"

        def test_handles_three_digits_department_code(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", department_code="973 - Guyane")

            # when
            information = parse_beneficiary_information(application_detail)

            # then
            assert information["department"] == "973"

        def test_handles_uppercased_mixed_digits_and_letter_department_code(self):
            # given
            application_detail = make_new_beneficiary_application_details(
                1, "closed", department_code="2B - Haute-Corse"
            )

            # when
            information = parse_beneficiary_information(application_detail)

            # then
            assert information["department"] == "2B"

        def test_handles_lowercased_mixed_digits_and_letter_department_code(self):
            # given
            application_detail = make_new_beneficiary_application_details(
                1, "closed", department_code="2a - Haute-Corse"
            )

            # when
            information = parse_beneficiary_information(application_detail)

            # then
            assert information["department"] == "2a"

        def test_handles_department_code_with_another_label(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", department_code="67 - Bas-Rhin")
            for field in application_detail["dossier"]["champs"]:
                label = field["type_de_champ"]["libelle"]
                if label == "Veuillez indiquer votre département":
                    field["type_de_champ"]["libelle"] = "Veuillez indiquer votre département de résidence"

            # when
            information = parse_beneficiary_information(application_detail)

            # then
            assert information["department"] == "67"

        def test_handles_postal_codes_wrapped_with_spaces(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", postal_code="  93130  ")

            # when
            information = parse_beneficiary_information(application_detail)

            # then
            assert information["postal_code"] == "93130"

        def test_handles_postal_codes_containing_spaces(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", postal_code="67 200")

            # when
            information = parse_beneficiary_information(application_detail)

            # then
            assert information["postal_code"] == "67200"

        def test_handles_postal_codes_containing_city_name(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", postal_code="67 200 Strasbourg ")

            # when
            information = parse_beneficiary_information(application_detail)

            # then
            assert information["postal_code"] == "67200"

        def test_handles_civility_parsing(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", civility="M.")

            # when
            information = parse_beneficiary_information(application_detail)

            # then
            assert information["civility"] == "M."

        def test_handles_activity_parsing(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed")

            # when
            information = parse_beneficiary_information(application_detail)

            # then
            assert information["activity"] == "Étudiant"

        def test_handles_activity_even_if_activity_is_not_filled(self):
            # given
            application_detail = make_new_beneficiary_application_details(1, "closed", activity=None)

            # when
            information = parse_beneficiary_information(application_detail)

            # then
            assert information["activity"] is None

    class AfterGeneralOpenningTest:
        def test_personal_information_of_beneficiary_are_parsed_from_application_detail(self):
            # when
            information = parse_beneficiary_information(APPLICATION_DETAIL_STANDARD_RESPONSE_AFTER_GENERALISATION)

            # then
            assert information["last_name"] == "Doe"
            assert information["first_name"] == "John"
            assert information["birth_date"] == datetime(2000, 5, 1)
            assert information["civility"] == "M."
            assert information["email"] == "john.doe@test.com"
            assert information["phone"] == "0123456789"
            assert information["postal_code"] == "93130"
            assert information["application_id"] == 123


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
                        "value": "121314",
                    },
                ],
            }
        }

    def _get_all_applications_ids(self, procedure_id: str, token: str, last_update: datetime):
        return [123]

    @override_features(FORCE_PHONE_VALIDATION=False)
    def test_import_user(self):
        # when
        remote_import.run(
            ONE_WEEK_AGO,
            procedure_id=6712558,
            get_details=self._get_details,
            get_all_applications_ids=self._get_all_applications_ids,
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
        assert push_testing.requests[0]["attribute_values"][
            "date(u.date_of_birth)"
        ] == self.BENEFICIARY_BIRTH_DATE.strftime("%Y-%m-%dT%H:%M:%S")

    @override_features(FORCE_PHONE_VALIDATION=True)
    def test_import_does_not_make_user_beneficiary(self):
        """
        Test that an imported user without a validated phone number, and the
        FORCE_PHONE_VALIDATION feature flag activated, cannot become
        beneficiary.
        """
        date_of_birth = self.BENEFICIARY_BIRTH_DATE.strftime("%Y-%m-%dT%H:%M:%S")

        # Create a user that has validated its email and phone number, meaning it
        # should become beneficiary.
        user = create_user(
            idx=4, email=self.EMAIL, is_beneficiary=False, is_email_validated=True, date_of_birth=date_of_birth
        )
        user.phoneValidationStatus = None
        repository.save(user)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            procedure_id=6712558,
            get_details=self._get_details,
            get_all_applications_ids=self._get_all_applications_ids,
        )

        # then
        assert User.query.count() == 1
        user = User.query.first()

        assert user.firstName == "john"
        assert user.postalCode == "93450"
        assert user.address == "11 Rue du Test"
        assert not user.isBeneficiary

        assert BeneficiaryImport.query.count() == 1
        beneficiary_import = BeneficiaryImport.query.first()

        assert beneficiary_import.source == "demarches_simplifiees"
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.beneficiary == user
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert len(push_testing.requests) == 1

        assert push_testing.requests == [
            {
                "attribute_values": {
                    "date(u.date_created)": user.dateCreated.strftime("%Y-%m-%dT%H:%M:%S"),
                    "date(u.date_of_birth)": date_of_birth,
                    "date(u.deposit_expiration_date)": None,
                    "u.credit": 0,
                    "u.departement_code": "93",
                    "u.is_beneficiary": False,
                    "u.marketing_push_subscription": True,
                    "u.postal_code": "93450",
                },
                "user_id": user.id,
            }
        ]

    def test_import_makes_user_beneficiary(self):
        """
        Test that an existing user with its phone number validated can become
        beneficiary.
        """
        date_of_birth = self.BENEFICIARY_BIRTH_DATE.strftime("%Y-%m-%dT%H:%M:%S")

        # Create a user that has validated its email and phone number, meaning it
        # should become beneficiary.
        user = create_user(
            idx=4, email=self.EMAIL, is_beneficiary=False, is_email_validated=True, date_of_birth=date_of_birth
        )
        user.phoneValidationStatus = PhoneValidationStatusType.VALIDATED
        repository.save(user)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            procedure_id=6712558,
            get_details=self._get_details,
            get_all_applications_ids=self._get_all_applications_ids,
        )

        # then
        assert User.query.count() == 1
        user = User.query.first()

        assert user.firstName == "john"
        assert user.postalCode == "93450"
        assert user.address == "11 Rue du Test"
        assert user.isBeneficiary
        assert user.phoneNumber == "0102030405"
        assert user.idPieceNumber == "121314"

        assert BeneficiaryImport.query.count() == 1
        beneficiary_import = BeneficiaryImport.query.first()

        assert beneficiary_import.source == "demarches_simplifiees"
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.beneficiary == user
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert len(push_testing.requests) == 1

        assert push_testing.requests == [
            {
                "attribute_values": {
                    "date(u.date_created)": user.dateCreated.strftime("%Y-%m-%dT%H:%M:%S"),
                    "date(u.date_of_birth)": date_of_birth,
                    "date(u.deposit_expiration_date)": user.deposit.expirationDate.strftime("%Y-%m-%dT%H:%M:%S"),
                    "u.credit": 30000,
                    "u.departement_code": "93",
                    "u.is_beneficiary": True,
                    "u.marketing_push_subscription": True,
                    "u.postal_code": "93450",
                },
                "user_id": user.id,
            }
        ]

    @override_features(FORCE_PHONE_VALIDATION=False)
    def test_import_duplicated_user(self):
        # given
        self.test_import_user()

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            procedure_id=6712558,
            get_details=self._get_details,
            get_all_applications_ids=self._get_all_applications_ids,
        )

        # then
        assert User.query.count() == 1
        assert BeneficiaryImport.query.count() == 1
        user = User.query.first()
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.source == "demarches_simplifiees"
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.beneficiary == user
        assert beneficiary_import.currentStatus == ImportStatus.REJECTED

    @override_features(FORCE_PHONE_VALIDATION=False)
    def test_import_native_app_user(self):
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

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            procedure_id=6712558,
            get_details=self._get_details,
            get_all_applications_ids=self._get_all_applications_ids,
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
