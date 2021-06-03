from datetime import datetime
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest

from pcapi.connectors.beneficiaries.jouve_backend import FraudDetectionItem
import pcapi.core.mails.testing as mails_testing
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import api as users_api
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_exceptions import BeneficiaryIsADuplicate
from pcapi.model_creators.generic_creators import create_user
from pcapi.models import BeneficiaryImport
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.db import db
from pcapi.models.deposit import Deposit
from pcapi.notifications.push import testing as push_testing
from pcapi.repository import repository
from pcapi.use_cases.create_beneficiary_from_application import create_beneficiary_from_application


PRE_SUBSCRIPTION_BASE_DATA = {
    "activity": "Apprenti",
    "address": "3 rue de Valois",
    "city": "Paris",
    "civility": "Mme",
    "date_of_birth": datetime(1995, 2, 5),
    "email": "rennes@example.org",
    "id_piece_number": "id-piece-number",
    "first_name": "Thomas",
    "last_name": "DURAND",
    "phone_number": "0123456789",
    "source": "jouve",
    "source_id": None,
    "fraud_fields": {
        "strict_controls": [FraudDetectionItem("posteCodeCtrl", "OK", True)],
        "non_blocking_controls": [FraudDetectionItem("bodyNameLevel", "80", True)],
    },
}


class FakeBeneficiaryJouveBackend:
    def get_application_by(self, application_id: int, fraud_detection: bool = True) -> BeneficiaryPreSubscription:
        return BeneficiaryPreSubscription(
            application_id=application_id,
            postal_code=f"{application_id:02d}123",
            **PRE_SUBSCRIPTION_BASE_DATA,
        )


@override_features(FORCE_PHONE_VALIDATION=False)
@patch("pcapi.use_cases.create_beneficiary_from_application.send_activation_email")
@patch("pcapi.domain.password.random_token")
@override_settings(
    JOUVE_APPLICATION_BACKEND="tests.use_cases.create_beneficiary_from_application_test.FakeBeneficiaryJouveBackend",
)
@freeze_time("2013-05-15 09:00:00")
@pytest.mark.usefixtures("db_session")
def test_saved_a_beneficiary_from_application(stubed_random_token, mocked_send_activation_email, app):
    # Given
    application_id = 35
    stubed_random_token.return_value = "token"

    # When
    create_beneficiary_from_application.execute(application_id)

    # Then
    beneficiary = User.query.one()
    assert beneficiary.activity == "Apprenti"
    assert beneficiary.address == "3 rue de Valois"
    assert beneficiary.isBeneficiary is True
    assert beneficiary.city == "Paris"
    assert beneficiary.civility == "Mme"
    assert beneficiary.dateOfBirth == datetime(1995, 2, 5)
    assert beneficiary.departementCode == "35"
    assert beneficiary.email == "rennes@example.org"
    assert beneficiary.firstName == "Thomas"
    assert beneficiary.hasSeenTutorials is False
    assert beneficiary.isAdmin is False
    assert beneficiary.lastName == "DURAND"
    assert beneficiary.password is not None
    assert beneficiary.phoneNumber == "0123456789"
    assert beneficiary.postalCode == "35123"
    assert beneficiary.publicName == "Thomas DURAND"
    assert beneficiary.notificationSubscriptions == {"marketing_push": True, "marketing_email": True}

    deposit = Deposit.query.one()
    assert deposit.amount == 300
    assert deposit.source == "dossier jouve [35]"
    assert deposit.userId == beneficiary.id

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.CREATED
    assert beneficiary_import.applicationId == application_id
    assert beneficiary_import.beneficiary == beneficiary

    assert len(beneficiary.tokens) == 1
    assert beneficiary.tokens[0].type == TokenType.RESET_PASSWORD

    mocked_send_activation_email.assert_called_once()

    assert push_testing.requests == [
        {
            "user_id": beneficiary.id,
            "attribute_values": {
                "u.credit": 30000,
                "date(u.date_of_birth)": "1995-02-05T00:00:00",
                "u.postal_code": "35123",
                "date(u.date_created)": beneficiary.dateCreated.strftime("%Y-%m-%dT%H:%M:%S"),
                "u.marketing_push_subscription": True,
                "u.is_beneficiary": True,
                "date(u.deposit_expiration_date)": "2015-05-15T09:00:00",
            },
        }
    ]


@override_features(FORCE_PHONE_VALIDATION=False)
@patch("pcapi.use_cases.create_beneficiary_from_application.send_accepted_as_beneficiary_email")
@override_settings(
    JOUVE_APPLICATION_BACKEND="tests.use_cases.create_beneficiary_from_application_test.FakeBeneficiaryJouveBackend",
)
@freeze_time("2013-05-15 09:00:00")
@pytest.mark.usefixtures("db_session")
def test_application_for_native_app_user(mocked_send_accepted_as_beneficiary_email, app):
    # Given
    application_id = 35
    users_api.create_account(
        email=PRE_SUBSCRIPTION_BASE_DATA["email"],
        password="123456789",
        birthdate=PRE_SUBSCRIPTION_BASE_DATA["date_of_birth"],
        is_email_validated=True,
        send_activation_mail=False,
        marketing_email_subscription=False,
        phone_number="0607080900",
    )
    push_testing.reset_requests()

    # When
    create_beneficiary_from_application.execute(application_id)

    # Then
    mocked_send_accepted_as_beneficiary_email.assert_called_once()

    beneficiary = User.query.one()

    # the fake Jouve backend returns a default phone number. Since a User
    # alredy exists, the phone number should not be updated during the import process
    assert beneficiary.phoneNumber == "0607080900"

    deposit = Deposit.query.one()
    assert deposit.amount == 300
    assert deposit.source == "dossier jouve [35]"
    assert deposit.userId == beneficiary.id

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.CREATED
    assert beneficiary_import.applicationId == application_id
    assert beneficiary_import.beneficiary == beneficiary
    assert beneficiary.notificationSubscriptions == {"marketing_push": True, "marketing_email": False}

    assert push_testing.requests == [
        {
            "user_id": beneficiary.id,
            "attribute_values": {
                "u.credit": 30000,
                "date(u.date_of_birth)": "1995-02-05T00:00:00",
                "u.postal_code": "35123",
                "date(u.date_created)": beneficiary.dateCreated.strftime("%Y-%m-%dT%H:%M:%S"),
                "u.marketing_push_subscription": True,
                "u.is_beneficiary": True,
                "date(u.deposit_expiration_date)": "2015-05-15T09:00:00",
            },
        }
    ]


@override_features(FORCE_PHONE_VALIDATION=False)
@override_settings(
    JOUVE_APPLICATION_BACKEND="tests.use_cases.create_beneficiary_from_application_test.FakeBeneficiaryJouveBackend",
)
@pytest.mark.usefixtures("db_session")
def test_cannot_save_beneficiary_if_email_is_already_taken(app):
    # Given
    application_id = 35
    email = "rennes@example.org"
    user = create_user(email=email, idx=4)
    repository.save(user)

    # When
    create_beneficiary_from_application.execute(application_id)

    # Then
    user = User.query.one()
    assert user.id == 4

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.applicationId == application_id
    assert beneficiary_import.beneficiary == user
    assert beneficiary_import.detail == f"Email {email} is already taken."

    assert push_testing.requests == []


@override_settings(
    JOUVE_APPLICATION_BACKEND="tests.use_cases.create_beneficiary_from_application_test.FakeBeneficiaryJouveBackend",
)
@pytest.mark.usefixtures("db_session")
def test_cannot_save_beneficiary_if_duplicate(app):
    # Given
    first_name = "Thomas"
    last_name = "DURAND"
    date_of_birth = datetime(1995, 2, 5)
    existing_user_id = 4

    user = create_user(first_name=first_name, last_name=last_name, date_of_birth=date_of_birth, idx=existing_user_id)
    repository.save(user)

    application_id = 35

    # When
    create_beneficiary_from_application.execute(application_id)

    # Then
    user = User.query.one()
    assert user.id == existing_user_id

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.applicationId == application_id
    assert beneficiary_import.beneficiary is None
    assert beneficiary_import.detail == f"User with id {existing_user_id} is a duplicate."


@pytest.mark.usefixtures("db_session")
@override_settings(
    JOUVE_APPLICATION_BACKEND="tests.use_cases.create_beneficiary_from_application_test.FakeBeneficiaryJouveBackend"
)
@override_features(WHOLE_FRANCE_OPENING=False)
def test_cannot_save_beneficiary_if_department_is_not_eligible_legacy_behaviour(app):
    # Given
    application_id = 36
    postal_code = f"{application_id}123"

    # When
    create_beneficiary_from_application.execute(application_id)

    # Then
    users_count = User.query.count()
    assert users_count == 0

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.applicationId == application_id
    assert beneficiary_import.beneficiary is None
    assert beneficiary_import.detail == f"Postal code {postal_code} is not eligible."


@pytest.mark.usefixtures("db_session")
@override_settings(
    JOUVE_APPLICATION_BACKEND="tests.use_cases.create_beneficiary_from_application_test.FakeBeneficiaryJouveBackend"
)
@override_features(WHOLE_FRANCE_OPENING=True)
def test_cannot_save_beneficiary_if_department_is_not_eligible(app):
    # Given
    application_id = 988
    postal_code = f"{application_id}123"

    # When
    create_beneficiary_from_application.execute(application_id)

    # Then
    users_count = User.query.count()
    assert users_count == 0

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.applicationId == application_id
    assert beneficiary_import.beneficiary is None
    assert beneficiary_import.detail == f"Postal code {postal_code} is not eligible."


@patch("pcapi.use_cases.create_beneficiary_from_application.validate")
@patch("pcapi.use_cases.create_beneficiary_from_application.send_rejection_email_to_beneficiary_pre_subscription")
@override_settings(
    JOUVE_APPLICATION_BACKEND="tests.use_cases.create_beneficiary_from_application_test.FakeBeneficiaryJouveBackend",
)
@pytest.mark.usefixtures("db_session")
def test_calls_send_rejection_mail_with_validation_error(
    mocked_send_rejection_email_to_beneficiary_pre_subscription, stubed_validate, app
):
    # Given
    application_id = 35
    error = BeneficiaryIsADuplicate("Some reason")
    stubed_validate.side_effect = error
    pre_subscription = BeneficiaryPreSubscription(
        application_id=application_id,
        postal_code=f"{application_id:02d}123",
        **PRE_SUBSCRIPTION_BASE_DATA,
    )

    # When
    create_beneficiary_from_application.execute(application_id)

    # Then
    mocked_send_rejection_email_to_beneficiary_pre_subscription.assert_called_once_with(
        beneficiary_pre_subscription=pre_subscription,
        beneficiary_is_eligible=True,
    )


BASE_APPLICATION_ID = 35
BASE_JOUVE_CONTENT = {
    "id": BASE_APPLICATION_ID,
    "firstName": "first_name",
    "lastName": "last_name",
    "email": "some@email.com",
    "activity": "some activity",
    "address": "some address",
    "city": "some city",
    "gender": "M",
    "bodyPieceNumber": "id-piece-number",
    "birthDate": "10/25/2003",
    "phoneNumber": "+33607080900",
    "postalCode": "77100",
    "posteCodeCtrl": "OK",
    "serviceCodeCtrl": "OK",
    "birthLocationCtrl": "OK",
    "creatorCtrl": "OK",
    "bodyBirthDateLevel": "100",
    "bodyNameLevel": "100",
}


@pytest.mark.parametrize(
    "fraud_strict_detection_parameter",
    [{"serviceCodeCtrl": "KO"}, {"posteCodeCtrl": "KO"}, {"birthLocationCtrl": "KO"}],
)
@patch("pcapi.connectors.beneficiaries.jouve_backend.BeneficiaryJouveBackend._get_application_content")
@pytest.mark.usefixtures("db_session")
def test_cannot_save_beneficiary_when_fraud_is_detected(
    mocked_get_content,
    fraud_strict_detection_parameter,
    app,
):
    # Given
    mocked_get_content.return_value = BASE_JOUVE_CONTENT | {
        "bodyNameLevel": 30,
    }
    # updates mocked return value from parametrized test
    mocked_get_content.return_value.update(fraud_strict_detection_parameter)

    # When
    create_beneficiary_from_application.execute(BASE_APPLICATION_ID)

    # Then
    fraud_strict_detection_cause = list(fraud_strict_detection_parameter.keys())[0]
    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.detail == f"Fraud controls triggered: {fraud_strict_detection_cause}, bodyNameLevel"

    assert len(mails_testing.outbox) == 0


@patch("pcapi.connectors.beneficiaries.jouve_backend.BeneficiaryJouveBackend._get_application_content")
@pytest.mark.usefixtures("db_session")
def test_doesnt_save_beneficiary_when_suspicious(
    mocked_get_content,
    app,
):
    # Given
    mocked_get_content.return_value = BASE_JOUVE_CONTENT | {"bodyBirthDateLevel": "20"}

    # When
    create_beneficiary_from_application.execute(BASE_APPLICATION_ID)

    # Then
    assert BeneficiaryImport.query.count() == 0

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2905960


@patch("pcapi.connectors.beneficiaries.jouve_backend.BeneficiaryJouveBackend._get_application_content")
@pytest.mark.usefixtures("db_session")
def test_id_piece_number_no_duplicate(
    mocked_get_content,
    app,
):
    # Given
    ID_PIECE_NUMBER = "id-piece-number"
    subscribing_user = UserFactory(
        isBeneficiary=False,
        dateOfBirth=datetime.now() - relativedelta(years=18, day=5),
        email=BASE_JOUVE_CONTENT["email"],
        idPieceNumber=None,
    )
    mocked_get_content.return_value = BASE_JOUVE_CONTENT | {"bodyPieceNumber": ID_PIECE_NUMBER}

    # When
    create_beneficiary_from_application.execute(BASE_APPLICATION_ID)

    # Then
    beneficiary_import = BeneficiaryImport.query.filter(BeneficiaryImport.beneficiary == subscribing_user).first()
    assert beneficiary_import.currentStatus == ImportStatus.CREATED

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2016025

    db.session.refresh(subscribing_user)
    assert subscribing_user.idPieceNumber == ID_PIECE_NUMBER


@patch("pcapi.connectors.beneficiaries.jouve_backend.BeneficiaryJouveBackend._get_application_content")
@pytest.mark.usefixtures("db_session")
def test_id_piece_number_duplicate(
    mocked_get_content,
    app,
):
    # Given
    ID_PIECE_NUMBER = "duplicated-id-piece-number"
    subscribing_user = UserFactory(
        isBeneficiary=False,
        dateOfBirth=datetime.now() - relativedelta(years=18, day=5),
        email=BASE_JOUVE_CONTENT["email"],
    )
    UserFactory(idPieceNumber=ID_PIECE_NUMBER)
    mocked_get_content.return_value = BASE_JOUVE_CONTENT | {"bodyPieceNumber": ID_PIECE_NUMBER}

    # When
    create_beneficiary_from_application.execute(BASE_APPLICATION_ID)

    # Then
    beneficiary_import = BeneficiaryImport.query.filter(BeneficiaryImport.beneficiary == subscribing_user).first()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.detail == f"Fraud controls triggered: id piece number n°{ID_PIECE_NUMBER} already taken"
    assert not subscribing_user.isBeneficiary

    assert len(mails_testing.outbox) == 0
