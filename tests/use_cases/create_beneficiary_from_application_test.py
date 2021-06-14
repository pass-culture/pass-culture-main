from datetime import datetime
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.testing import override_features
from pcapi.core.users import api as users_api
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_exceptions import BeneficiaryIsADuplicate
from pcapi.model_creators.generic_creators import create_user
from pcapi.models import BeneficiaryImport
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.db import db
from pcapi.models.deposit import Deposit
from pcapi.notifications.push import testing as push_testing
from pcapi.repository import repository
from pcapi.use_cases.create_beneficiary_from_application import create_beneficiary_from_application


APPLICATION_ID = 35

JOUVE_CONTENT = {
    "activity": "Apprenti",
    "address": "3 rue de Valois",
    "birthDateTxt": "22/05/1995",
    "bodyBirthDateCtrl": "OK",
    "bodyBirthDateLevel": 100,
    "bodyFirstNameCtrl": "OK",
    "bodyFirstNameLevel": 100,
    "bodyNameLevel": 80,
    "bodyNameCtrl": "OK",
    "bodyPieceNumber": "id-piece-number",
    "bodyPieceNumberCtrl": "OK",
    "bodyPieceNumberLevel": 100,
    "city": "Paris",
    "creatorCtrl": "OK",
    "email": "rennes@example.org",
    "gender": "F",
    "id": APPLICATION_ID,
    "initialNumberCtrl": "OK",
    "initialSizeCtrl": "OK",
    "firstName": "Thomas",
    "lastName": "DURAND",
    "phoneNumber": "0123456789",
    "postalCode": "35123",
}


@override_features(FORCE_PHONE_VALIDATION=False)
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content", return_value=JOUVE_CONTENT)
@patch("pcapi.domain.password.random_token")
@freeze_time("2013-05-15 09:00:00")
@pytest.mark.usefixtures("db_session")
def test_saved_a_beneficiary_from_application(stubed_random_token, app):
    # Given
    stubed_random_token.return_value = "token"

    # When
    create_beneficiary_from_application.execute(APPLICATION_ID)

    # Then
    beneficiary = User.query.one()
    assert beneficiary.activity == "Apprenti"
    assert beneficiary.address == "3 rue de Valois"
    assert beneficiary.isBeneficiary is True
    assert beneficiary.city == "Paris"
    assert beneficiary.civility == "Mme"
    assert beneficiary.dateOfBirth == datetime(1995, 5, 22)
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
    assert beneficiary_import.applicationId == APPLICATION_ID
    assert beneficiary_import.beneficiary == beneficiary

    assert len(beneficiary.tokens) == 1
    assert beneficiary.tokens[0].type == TokenType.RESET_PASSWORD

    assert len(mails_testing.outbox) == 1

    assert push_testing.requests == [
        {
            "user_id": beneficiary.id,
            "attribute_values": {
                "u.credit": 30000,
                "u.departement_code": "35",
                "date(u.date_of_birth)": "1995-05-22T00:00:00",
                "u.postal_code": "35123",
                "date(u.date_created)": beneficiary.dateCreated.strftime("%Y-%m-%dT%H:%M:%S"),
                "u.marketing_push_subscription": True,
                "u.is_beneficiary": True,
                "date(u.deposit_expiration_date)": "2015-05-15T09:00:00",
            },
        }
    ]


@override_features(FORCE_PHONE_VALIDATION=False)
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content", return_value=JOUVE_CONTENT)
@freeze_time("2013-05-15 09:00:00")
@pytest.mark.usefixtures("db_session")
def test_application_for_native_app_user(app):
    # Given
    users_api.create_account(
        email=JOUVE_CONTENT["email"],
        password="123456789",
        birthdate=datetime(1995, 4, 15),
        is_email_validated=True,
        send_activation_mail=False,
        marketing_email_subscription=False,
        phone_number="0607080900",
    )
    push_testing.reset_requests()

    # When
    create_beneficiary_from_application.execute(APPLICATION_ID)

    # Then
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
    assert beneficiary_import.applicationId == APPLICATION_ID
    assert beneficiary_import.beneficiary == beneficiary
    assert beneficiary.notificationSubscriptions == {"marketing_push": True, "marketing_email": False}

    assert push_testing.requests == [
        {
            "user_id": beneficiary.id,
            "attribute_values": {
                "u.credit": 30000,
                "date(u.date_of_birth)": "1995-05-22T00:00:00",
                "u.departement_code": "35",
                "u.postal_code": "35123",
                "date(u.date_created)": beneficiary.dateCreated.strftime("%Y-%m-%dT%H:%M:%S"),
                "u.marketing_push_subscription": True,
                "u.is_beneficiary": True,
                "date(u.deposit_expiration_date)": "2015-05-15T09:00:00",
            },
        }
    ]


@freeze_time("2013-05-15 09:00:00")
@override_features(FORCE_PHONE_VALIDATION=False)
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
def test_application_for_native_app_user_with_load_smoothing(_get_raw_content, app, db_session):
    # Given
    application_id = 35
    user = UserFactory(
        dateOfBirth=datetime(2003, 10, 25),
        phoneNumber="0607080900",
        isBeneficiary=False,
        address="an address",
        city="Nantes",
        postalCode="44300",
        activity="Apprenti",
        hasCompletedIdCheck=True,
    )
    push_testing.reset_requests()
    _get_raw_content.return_value = {
        "id": BASE_APPLICATION_ID,
        "firstName": "first_name",
        "lastName": "last_name",
        "email": user.email,
        "activity": "Étudiant",
        "address": "",
        "city": "",
        "gender": "M",
        "bodyPieceNumber": "id-piece-number",
        "birthDateTxt": "25/10/2003",
        "postalCode": "",
        "phoneNumber": "0102030405",
        "posteCodeCtrl": "OK",
        "serviceCodeCtrl": "OK",
        "birthLocationCtrl": "OK",
        "creatorCtrl": "OK",
        "bodyBirthDateLevel": "100",
        "bodyNameLevel": "100",
    }

    # When
    create_beneficiary_from_application.execute(application_id)

    # Then
    beneficiary = User.query.one()

    # the fake Jouve backend returns a default phone number. Since a User
    # alredy exists, the phone number should not be updated during the import process
    assert beneficiary.phoneNumber == "0607080900"
    assert beneficiary.address == "an address"
    assert beneficiary.activity == "Apprenti"
    assert beneficiary.postalCode == "44300"

    deposit = Deposit.query.one()
    assert deposit.amount == 300
    assert deposit.source == "dossier jouve [35]"
    assert deposit.userId == beneficiary.id

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.CREATED
    assert beneficiary_import.applicationId == application_id
    assert beneficiary_import.beneficiary == beneficiary
    assert beneficiary.notificationSubscriptions == {"marketing_push": True, "marketing_email": True}

    assert push_testing.requests == [
        {
            "user_id": beneficiary.id,
            "attribute_values": {
                "u.credit": 30000,
                "u.departement_code": "75",
                "date(u.date_of_birth)": "2003-10-25T00:00:00",
                "u.postal_code": "44300",
                "date(u.date_created)": beneficiary.dateCreated.strftime("%Y-%m-%dT%H:%M:%S"),
                "u.marketing_push_subscription": True,
                "u.is_beneficiary": True,
                "date(u.deposit_expiration_date)": "2015-05-15T09:00:00",
            },
        }
    ]
    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2016025


@override_features(FORCE_PHONE_VALIDATION=False)
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content", return_value=JOUVE_CONTENT)
@pytest.mark.usefixtures("db_session")
def test_cannot_save_beneficiary_if_email_is_already_taken(app):
    # Given
    email = "rennes@example.org"
    user = create_user(email=email, idx=4)
    repository.save(user)

    # When
    create_beneficiary_from_application.execute(APPLICATION_ID)

    # Then
    user = User.query.one()
    assert user.id == 4

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.applicationId == APPLICATION_ID
    assert beneficiary_import.beneficiary == user
    assert beneficiary_import.detail == f"Email {email} is already taken."

    assert push_testing.requests == []


@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content", return_value=JOUVE_CONTENT)
@pytest.mark.usefixtures("db_session")
def test_cannot_save_beneficiary_if_duplicate(app):
    # Given
    first_name = "Thomas"
    last_name = "DURAND"
    date_of_birth = datetime(1995, 5, 22)
    existing_user_id = 4

    user = create_user(first_name=first_name, last_name=last_name, date_of_birth=date_of_birth, idx=existing_user_id)
    repository.save(user)

    # When
    create_beneficiary_from_application.execute(APPLICATION_ID)

    # Then
    user = User.query.one()
    assert user.id == existing_user_id

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.applicationId == APPLICATION_ID
    assert beneficiary_import.beneficiary is None
    assert beneficiary_import.detail == f"User with id {existing_user_id} is a duplicate."


@pytest.mark.usefixtures("db_session")
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
@override_features(WHOLE_FRANCE_OPENING=False)
def test_cannot_save_beneficiary_if_department_is_not_eligible_legacy_behaviour(get_application_content, app):
    # Given
    postal_code = "75000"
    get_application_content.return_value = JOUVE_CONTENT | {"postalCode": postal_code}

    # When
    create_beneficiary_from_application.execute(APPLICATION_ID)

    # Then
    users_count = User.query.count()
    assert users_count == 0

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.applicationId == APPLICATION_ID
    assert beneficiary_import.beneficiary is None
    assert beneficiary_import.detail == f"Postal code {postal_code} is not eligible."


@pytest.mark.usefixtures("db_session")
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
@override_features(WHOLE_FRANCE_OPENING=True)
def test_cannot_save_beneficiary_if_department_is_not_eligible(get_application_content, app):
    # Given
    postal_code = "984"
    get_application_content.return_value = JOUVE_CONTENT | {"postalCode": postal_code}

    # When
    create_beneficiary_from_application.execute(APPLICATION_ID)

    # Then
    users_count = User.query.count()
    assert users_count == 0

    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.applicationId == APPLICATION_ID
    assert beneficiary_import.beneficiary is None
    assert beneficiary_import.detail == f"Postal code {postal_code} is not eligible."


@patch("pcapi.use_cases.create_beneficiary_from_application.validate")
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
@pytest.mark.usefixtures("db_session")
def test_calls_send_rejection_mail_with_validation_error(_get_raw_content, stubed_validate, app):
    # Given
    error = BeneficiaryIsADuplicate("Some reason")
    stubed_validate.side_effect = error
    _get_raw_content.return_value = JOUVE_CONTENT

    # When
    create_beneficiary_from_application.execute(APPLICATION_ID)

    # Then
    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 1530996
    assert mails_testing.outbox[0].sent_data["To"] == "rennes@example.org"


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
    "birthDateTxt": "25/10/2003",
    "phoneNumber": "+33607080900",
    "postalCode": "77100",
    "posteCodeCtrl": "OK",
    "serviceCodeCtrl": "OK",
    "birthLocationCtrl": "OK",
    "creatorCtrl": "OK",
    "bodyBirthDateLevel": "100",
    "bodyNameLevel": "100",
}


# TODO(xordoquy): make fraud fields configurable and reactivate this test
# @pytest.mark.parametrize(
#     "fraud_strict_detection_parameter",
#     [{"serviceCodeCtrl": "KO"}, {"posteCodeCtrl": "KO"}, {"birthLocationCtrl": "KO"}],
# )
# @patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
# @pytest.mark.usefixtures("db_session")
# def test_cannot_save_beneficiary_when_fraud_is_detected(
#     mocked_get_content,
#     fraud_strict_detection_parameter,
#     app,
# ):
#     # Given
#     mocked_get_content.return_value = BASE_JOUVE_CONTENT | {
#         "bodyNameLevel": 30,
#     }
#     # updates mocked return value from parametrized test
#     mocked_get_content.return_value.update(fraud_strict_detection_parameter)

#     # When
#     create_beneficiary_from_application.execute(BASE_APPLICATION_ID)

#     # Then
#     fraud_strict_detection_cause = list(fraud_strict_detection_parameter.keys())[0]
#     beneficiary_import = BeneficiaryImport.query.one()
#     assert beneficiary_import.currentStatus == ImportStatus.REJECTED
#     assert beneficiary_import.detail == f"Fraud controls triggered: {fraud_strict_detection_cause}, bodyNameLevel"

#     assert len(mails_testing.outbox) == 0


@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
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


@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
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


@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
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
