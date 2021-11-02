from dataclasses import asdict
from datetime import datetime
import logging
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import freezegun
import pytest

from pcapi.connectors.beneficiaries import jouve_backend
from pcapi.core.fraud import models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.payments.models import Deposit
from pcapi.core.subscription import models as subscription_models
from pcapi.core.testing import override_features
from pcapi.core.users import api as users_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import User
from pcapi.domain.beneficiary_pre_subscription.exceptions import BeneficiaryIsADuplicate
from pcapi.models import BeneficiaryImport
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.db import db
from pcapi.notifications.push import testing as push_testing
from pcapi.use_cases.create_beneficiary_from_application import create_beneficiary_from_application


pytestmark = pytest.mark.usefixtures("db_session")

APPLICATION_ID = 35
AGE18_ELIGIBLE_BIRTH_DATE = datetime.now() - relativedelta(years=18, months=4)

JOUVE_CONTENT = {
    "activity": "Apprenti",
    "address": "3 rue de Valois",
    "birthDateTxt": f"{AGE18_ELIGIBLE_BIRTH_DATE:%d/%m/%Y}",
    "birthLocationCtrl": "OK",
    "bodyBirthDateCtrl": "OK",
    "bodyBirthDateLevel": 100,
    "bodyFirstnameCtrl": "OK",
    "bodyFirstnameLevel": 100,
    "bodyNameLevel": 80,
    "bodyNameCtrl": "OK",
    "bodyPieceNumber": "140767100016",
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
def test_saved_a_beneficiary_from_application(stubed_random_token, app):
    # Given
    stubed_random_token.return_value = "token"
    users_factories.UserFactory(
        firstName=JOUVE_CONTENT["firstName"], lastName=JOUVE_CONTENT["lastName"], email=JOUVE_CONTENT["email"]
    )
    # When
    create_beneficiary_from_application.execute(APPLICATION_ID)

    # Then
    beneficiary = User.query.one()
    assert beneficiary.activity == "Apprenti"
    assert beneficiary.address == "3 rue de Valois"
    assert beneficiary.has_beneficiary_role is True
    assert beneficiary.city == "Paris"
    assert beneficiary.civility == "Mme"
    assert beneficiary.dateOfBirth.date() == AGE18_ELIGIBLE_BIRTH_DATE.date()
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

    assert len(mails_testing.outbox) == 1
    assert len(push_testing.requests) == 1


@override_features(PAUSE_JOUVE_SUBSCRIPTION=True)
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content", return_value=JOUVE_CONTENT)
def test_marked_subscription_on_hold_when_jouve_subscription_journed_is_paused(_get_raw_content, caplog):
    user = users_factories.UserFactory(
        firstName=JOUVE_CONTENT["firstName"], lastName=JOUVE_CONTENT["lastName"], email=JOUVE_CONTENT["email"]
    )
    # When
    with caplog.at_level(logging.INFO):
        create_beneficiary_from_application.execute(APPLICATION_ID)

    assert caplog.messages[0] == "User subscription is on hold"
    assert user.beneficiaryFraudResult.status == fraud_models.FraudStatus.SUBSCRIPTION_ON_HOLD

    assert len(mails_testing.outbox) == 0
    assert len(push_testing.requests) == 0


@override_features(FORCE_PHONE_VALIDATION=False)
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content", return_value=JOUVE_CONTENT)
def test_application_for_native_app_user(app):
    # Given
    users_api.create_account(
        email=JOUVE_CONTENT["email"],
        password="123456789",
        birthdate=AGE18_ELIGIBLE_BIRTH_DATE,
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

    assert len(push_testing.requests) == 1


@override_features(FORCE_PHONE_VALIDATION=False)
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
def test_application_for_native_app_user_with_load_smoothing(_get_raw_content, app, db_session):
    # Given
    application_id = 35
    user = UserFactory(
        dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
        phoneNumber="0607080900",
        address="an address",
        city="Nantes",
        postalCode="44300",
        activity="Apprenti",
        hasCompletedIdCheck=True,
    )
    push_testing.reset_requests()
    _get_raw_content.return_value = JOUVE_CONTENT | {
        "id": BASE_APPLICATION_ID,
        "firstName": "first_name",
        "lastName": "last_name",
        "email": user.email,
        "activity": "Étudiant",
        "address": "",
        "city": "",
        "gender": "M",
        "bodyPieceNumber": "140767100016",
        "birthDateTxt": f"{AGE18_ELIGIBLE_BIRTH_DATE:%d/%m/%Y}",
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

    assert len(push_testing.requests) == 1
    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2016025


@override_features(FORCE_PHONE_VALIDATION=False)
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content", return_value=JOUVE_CONTENT)
def test_cannot_save_beneficiary_if_email_is_already_taken(app):
    # Given
    email = "rennes@example.org"
    users_factories.BeneficiaryGrant18Factory(email=email, id=4)

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


@freezegun.freeze_time("2021-10-30 09:00:00")
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content", return_value=JOUVE_CONTENT)
def test_cannot_save_beneficiary_if_duplicate(app):
    # Given
    first_name = "Thomas"
    last_name = "DURAND"
    date_of_birth = AGE18_ELIGIBLE_BIRTH_DATE.replace(hour=0, minute=0, second=0, microsecond=0)

    applicant = users_factories.UserFactory(
        firstName=JOUVE_CONTENT["firstName"], lastName=JOUVE_CONTENT["lastName"], email=JOUVE_CONTENT["email"]
    )

    existing_user = users_factories.BeneficiaryGrant18Factory(
        firstName=first_name, lastName=last_name, dateOfBirth=date_of_birth
    )

    # When
    create_beneficiary_from_application.execute(APPLICATION_ID)

    # Then
    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.applicationId == APPLICATION_ID
    assert beneficiary_import.detail == f"User with id {existing_user.id} is a duplicate."
    assert beneficiary_import.beneficiary is applicant

    assert len(applicant.subscriptionMessages) == 1
    sub_msg = applicant.subscriptionMessages[0]
    assert (
        sub_msg.userMessage
        == "Ce document a déjà été analysé. Vérifie que tu n’as pas créé de compte avec une autre adresse e-mail. Consulte l’e-mail envoyé le 30/10/2021 pour plus d’informations."
    )
    assert sub_msg.callToActionIcon == subscription_models.CallToActionIcon.EMAIL


@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
def test_cannot_save_beneficiary_if_department_is_not_eligible(get_application_content, app):
    # Given
    postal_code = "984"
    get_application_content.return_value = JOUVE_CONTENT | {"postalCode": postal_code}
    applicant = users_factories.UserFactory(
        firstName=JOUVE_CONTENT["firstName"], lastName=JOUVE_CONTENT["lastName"], email=JOUVE_CONTENT["email"]
    )

    # When
    create_beneficiary_from_application.execute(APPLICATION_ID)

    # Then
    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.REJECTED
    assert beneficiary_import.applicationId == APPLICATION_ID
    assert beneficiary_import.beneficiary == applicant
    assert beneficiary_import.detail == f"Postal code {postal_code} is not eligible."


@patch("pcapi.use_cases.create_beneficiary_from_application.validate")
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
def test_calls_send_rejection_mail_with_validation_error(_get_raw_content, stubed_validate, app):
    # Given
    error = BeneficiaryIsADuplicate("Some reason")
    stubed_validate.side_effect = error
    _get_raw_content.return_value = JOUVE_CONTENT
    users_factories.UserFactory(
        firstName=JOUVE_CONTENT["firstName"], lastName=JOUVE_CONTENT["lastName"], email=JOUVE_CONTENT["email"]
    )

    # When
    create_beneficiary_from_application.execute(APPLICATION_ID)

    # Then
    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 1530996
    assert mails_testing.outbox[0].sent_data["To"] == "rennes@example.org"


@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
def test_user_pre_creation_is_required(_get_raw_content):
    _get_raw_content.return_value = JOUVE_CONTENT

    create_beneficiary_from_application.execute(APPLICATION_ID)
    beneficiary_import = BeneficiaryImport.query.one()
    assert beneficiary_import.currentStatus == ImportStatus.ERROR
    assert beneficiary_import.applicationId == APPLICATION_ID
    assert beneficiary_import.beneficiary is None
    assert beneficiary_import.statuses[-1].detail == f"Aucun utilisateur trouvé pour l'email {JOUVE_CONTENT['email']}"


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
    "birthDateTxt": f"{AGE18_ELIGIBLE_BIRTH_DATE:%d/%m/%Y}",
    "bodyBirthDateCtrl": "OK",
    "bodyPieceNumberCtrl": "OK",
    "bodyPieceNumberLevel": "100",
    "bodyNameCtrl": "OK",
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
def test_doesnt_save_beneficiary_when_suspicious(
    mocked_get_content,
    app,
):
    # Given
    mocked_get_content.return_value = BASE_JOUVE_CONTENT | {"bodyBirthDateLevel": "20"}
    users_factories.UserFactory(
        firstName=BASE_JOUVE_CONTENT["firstName"],
        lastName=BASE_JOUVE_CONTENT["lastName"],
        email=BASE_JOUVE_CONTENT["email"],
    )

    # When
    create_beneficiary_from_application.execute(BASE_APPLICATION_ID)

    # Then
    assert BeneficiaryImport.query.count() == 0

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2905960


@override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
def test_send_analysing_account_emails_with_sendinblue_when_suspicious(
    mocked_get_content,
    app,
):
    # Given
    mocked_get_content.return_value = BASE_JOUVE_CONTENT | {"bodyBirthDateLevel": "20"}
    users_factories.UserFactory(
        firstName=BASE_JOUVE_CONTENT["firstName"],
        lastName=BASE_JOUVE_CONTENT["lastName"],
        email=BASE_JOUVE_CONTENT["email"],
        dateOfBirth=datetime.now() - relativedelta(years=18, day=5),
    )

    # When
    create_beneficiary_from_application.execute(BASE_APPLICATION_ID)

    # Then
    assert BeneficiaryImport.query.count() == 0

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["template"] == asdict(TransactionalEmail.FRAUD_SUSPICION.value)
    assert mails_testing.outbox[0].sent_data["params"] == {}


@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
def test_id_piece_number_no_duplicate(
    mocked_get_content,
    app,
):
    # Given
    ID_PIECE_NUMBER = "140767100016"
    subscribing_user = UserFactory(
        isBeneficiary=False,
        dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
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
def test_id_piece_number_duplicate(
    mocked_get_content,
    app,
):
    # Given
    ID_PIECE_NUMBER = "140767100016"
    subscribing_user = UserFactory(
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
    assert not subscribing_user.has_beneficiary_role

    assert len(mails_testing.outbox) == 0


@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
def test_id_piece_number_invalid_format_avoid_duplicate(
    mocked_get_content,
    app,
):
    # Given
    ID_PIECE_NUMBER = "140767100016"
    UserFactory(
        isBeneficiary=False,
        dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
        email=BASE_JOUVE_CONTENT["email"],
    )
    UserFactory(idPieceNumber=ID_PIECE_NUMBER)
    mocked_get_content.return_value = BASE_JOUVE_CONTENT | {
        "bodyPieceNumber": ID_PIECE_NUMBER,
        "bodyPieceNumberCtrl": "KO",
    }

    # When
    create_beneficiary_from_application.execute(BASE_APPLICATION_ID)

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2905960
    assert mails_testing.outbox[0].sent_data["Mj-campaign"] == "dossier-en-analyse"


@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
@pytest.mark.parametrize("wrong_piece_number", ["NOT_APPLICABLE", "KO", ""])
def test_id_piece_number_invalid(mocked_get_content, wrong_piece_number):
    subscribing_user = UserFactory(
        isBeneficiary=False,
        dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
        email=BASE_JOUVE_CONTENT["email"],
    )
    UserFactory(idPieceNumber=wrong_piece_number)
    mocked_get_content.return_value = BASE_JOUVE_CONTENT | {"bodyPieceNumberCtrl": wrong_piece_number}

    # When
    create_beneficiary_from_application.execute(BASE_APPLICATION_ID)

    # Then
    assert len(subscribing_user.beneficiaryImports) == 0

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2905960
    assert mails_testing.outbox[0].sent_data["Mj-campaign"] == "dossier-en-analyse"


@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
@pytest.mark.parametrize("wrong_piece_number", ["NOT_APPLICABLE", "KO", ""])
def test_id_piece_number_wrong_return_control(mocked_get_content, wrong_piece_number):
    subscribing_user = UserFactory(
        isBeneficiary=False,
        dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
        email=BASE_JOUVE_CONTENT["email"],
    )
    UserFactory(idPieceNumber=wrong_piece_number)
    mocked_get_content.return_value = BASE_JOUVE_CONTENT | {"bodyPieceNumberCtrl": wrong_piece_number}

    # When
    create_beneficiary_from_application.execute(BASE_APPLICATION_ID)

    # Then
    assert len(subscribing_user.beneficiaryImports) == 0

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2905960
    assert mails_testing.outbox[0].sent_data["Mj-campaign"] == "dossier-en-analyse"


@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
@pytest.mark.parametrize(
    "id_piece_number",
    [
        "I III1",
        "I I 1JII 11IB I E",
        "",
    ],
)
def test_id_piece_number_wrong_format(mocked_get_content, id_piece_number):
    subscribing_user = UserFactory(
        isBeneficiary=False,
        dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
        email=BASE_JOUVE_CONTENT["email"],
    )
    UserFactory(idPieceNumber=id_piece_number)
    mocked_get_content.return_value = BASE_JOUVE_CONTENT | {"bodyPieceNumber": id_piece_number}

    # When
    create_beneficiary_from_application.execute(BASE_APPLICATION_ID)

    # Then
    assert len(subscribing_user.beneficiaryImports) == 0

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2905960
    assert mails_testing.outbox[0].sent_data["Mj-campaign"] == "dossier-en-analyse"


@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
def test_id_piece_number_by_pass(
    mocked_get_content,
    app,
):
    # Given
    ID_PIECE_NUMBER = "NOT_APPLICABLE"
    subscribing_user = UserFactory(
        isBeneficiary=False,
        dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
        email=BASE_JOUVE_CONTENT["email"],
    )
    UserFactory(idPieceNumber=ID_PIECE_NUMBER)
    UserFactory(idPieceNumber=None)
    mocked_get_content.return_value = BASE_JOUVE_CONTENT | {"bodyPieceNumber": ID_PIECE_NUMBER}

    # When
    create_beneficiary_from_application.execute(BASE_APPLICATION_ID, ignore_id_piece_number_field=True)

    # Then
    beneficiary_import = BeneficiaryImport.query.filter(BeneficiaryImport.beneficiary == subscribing_user).first()

    assert beneficiary_import.currentStatus == ImportStatus.CREATED
    assert subscribing_user.has_beneficiary_role
    assert not subscribing_user.idPieceNumber

    assert len(mails_testing.outbox) == 1


@patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
def test_jouve_raise_403(mocked_get_content, caplog):
    mocked_get_content.side_effect = jouve_backend.ApiJouveException(
        "Error getting API Jouve authentication token", route="/any/url/", status_code=403
    )

    create_beneficiary_from_application.execute(BASE_APPLICATION_ID)
    mocked_get_content.assert_called()
    assert caplog.messages[0] == "Error getting API Jouve authentication token"


class JouveDataValidationTest:
    @freezegun.freeze_time("2021-10-30 09:00:00")
    @patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
    @pytest.mark.parametrize(
        "jouve_field", ["birthLocationCtrl", "bodyBirthDateCtrl", "bodyNameCtrl", "bodyPieceNumberCtrl"]
    )
    @pytest.mark.parametrize("possible_value", ["KO", "NOT_APPLICABLE", "", "bodyPieceNumberCtrl"])
    def test_mandatory_jouve_fields_wrong_data(self, mocked_get_content, jouve_field, possible_value):
        UserFactory(
            isBeneficiary=False,
            dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
            email=BASE_JOUVE_CONTENT["email"],
        )
        mocked_get_content.return_value = BASE_JOUVE_CONTENT | {jouve_field: possible_value}
        create_beneficiary_from_application.execute(BASE_APPLICATION_ID, ignore_id_piece_number_field=True)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2905960
        assert mails_testing.outbox[0].sent_data["Mj-campaign"] == "dossier-en-analyse"

        assert subscription_models.SubscriptionMessage.query.count() == 1
        message = subscription_models.SubscriptionMessage.query.first()
        assert message.popOverIcon == subscription_models.PopOverIcon.CLOCK
        assert (
            message.userMessage
            == "Nous avons reçu ton dossier le 30/10/2021 et son analyse est en cours. Cela peut prendre jusqu'à 5 jours."
        )

    @patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
    @pytest.mark.parametrize("jouve_field", ["bodyBirthDateLevel", "bodyNameLevel", "bodyPieceNumberLevel"])
    @pytest.mark.parametrize("possible_value", ["", "NOT_APPLICABLE", "25"])
    def test_mandatory_jouve_fields_wrong_integer_data(self, mocked_get_content, jouve_field, possible_value):
        UserFactory(
            isBeneficiary=False,
            dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE,
            email=BASE_JOUVE_CONTENT["email"],
        )
        mocked_get_content.return_value = BASE_JOUVE_CONTENT | {jouve_field: possible_value}
        create_beneficiary_from_application.execute(BASE_APPLICATION_ID, ignore_id_piece_number_field=True)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2905960
        assert mails_testing.outbox[0].sent_data["Mj-campaign"] == "dossier-en-analyse"
