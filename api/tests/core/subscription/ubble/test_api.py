import datetime
from io import BytesIO
import json
import pathlib
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import freezegun
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.exceptions import IncompatibleFraudCheckStatus
from pcapi.core.fraud.factories import BeneficiaryFraudCheckFactory
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.fraud.ubble import models as ubble_fraud_models
from pcapi.core.fraud.ubble.models import UbbleContent
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.exceptions import BeneficiaryFraudCheckMissingException
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.subscription.ubble import exceptions as ubble_exceptions
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils import requests as requests_utils

import tests
from tests.core.subscription.test_factories import IdentificationState
from tests.core.subscription.test_factories import UbbleIdentificationIncludedDocumentsFactory
from tests.core.subscription.test_factories import UbbleIdentificationIncludedReferenceDataChecksFactory
from tests.core.subscription.test_factories import UbbleIdentificationResponseFactory
from tests.test_utils import json_default


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class UbbleWorkflowTest:
    def test_start_ubble_workflow(self, ubble_mock):
        user = users_factories.UserFactory()
        redirect_url = ubble_subscription_api.start_ubble_workflow(
            user, "Kid", "Paddle", redirect_url="https://example.com"
        )
        assert redirect_url == "https://id.ubble.ai/29d9eca4-dce6-49ed-b1b5-8bb0179493a8"

        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId is not None
        assert fraud_check.resultContent is not None
        assert fraud_check.status == fraud_models.FraudCheckStatus.STARTED

        ubble_request = ubble_mock.last_request.json()
        assert ubble_request["data"]["attributes"]["webhook"] == "http://localhost/webhooks/ubble/application_status"

    @pytest.mark.parametrize(
        "state, status, fraud_check_status",
        [
            (
                IdentificationState.INITIATED,
                ubble_fraud_models.UbbleIdentificationStatus.INITIATED,
                fraud_models.FraudCheckStatus.PENDING,
            ),
            (
                IdentificationState.PROCESSING,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSING,
                fraud_models.FraudCheckStatus.PENDING,
            ),
            (
                IdentificationState.VALID,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
                fraud_models.FraudCheckStatus.OK,
            ),
            (
                IdentificationState.INVALID,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
                fraud_models.FraudCheckStatus.KO,
            ),
            (
                IdentificationState.UNPROCESSABLE,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
                fraud_models.FraudCheckStatus.SUSPICIOUS,
            ),
            (
                IdentificationState.ABORTED,
                ubble_fraud_models.UbbleIdentificationStatus.ABORTED,
                fraud_models.FraudCheckStatus.CANCELED,
            ),
        ],
    )
    def test_update_ubble_workflow(self, ubble_mocker, state, status, fraud_check_status):
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(type=fraud_models.FraudCheckType.UBBLE, user=user)
        ubble_response = UbbleIdentificationResponseFactory(identification_state=state)
        assert user.married_name is None

        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        ubble_content = fraud_check.resultContent
        assert ubble_content["status"] == status.value
        assert fraud_check.status == fraud_check_status

    def test_ubble_workflow_processing_add_inapp_message(self, ubble_mocker):
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.PENDING, user=user
        )
        ubble_response = UbbleIdentificationResponseFactory(identification_state=IdentificationState.PROCESSING)
        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

            message = ubble_subscription_api.get_ubble_subscription_message(fraud_check, False)
            assert message.user_message == "Ton document d'identité est en cours de vérification."
            assert message.pop_over_icon == subscription_models.PopOverIcon.CLOCK

    def test_ubble_workflow_rejected_add_inapp_message(self, ubble_mocker):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=1))
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.PENDING, user=user
        )
        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.INVALID,
            included=[
                UbbleIdentificationIncludedReferenceDataChecksFactory(
                    attributes__score=0,
                ),
            ],
        )

        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)
            message = ubble_subscription_api.get_ubble_subscription_message(fraud_check, False)
            assert (
                message.user_message
                == "Ton dossier a été refusé : le prénom et le nom que tu as renseignés ne correspondent pas à ta pièce d'identité. Tu peux contacter le support pour plus d'informations."
            )
            assert (
                message.call_to_action.link
                == subscription_messages.MAILTO_SUPPORT + subscription_messages.MAILTO_SUPPORT_PARAMS.format(id=user.id)
            )
            assert message.call_to_action.icon == subscription_models.CallToActionIcon.EMAIL
            assert message.call_to_action.title == "Contacter le support"

    @freezegun.freeze_time("2020-05-05")
    def test_ubble_workflow_with_eligibility_change_17_18(self, ubble_mocker):
        # User set his birth date as if 17 years old
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2002, month=5, day=6))
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        ubble_identification = fraud_check.thirdPartyId

        # Receiving a response from the UBBLE service, saying the user is 18 years old
        document_birth_date = datetime.datetime(year=2002, month=5, day=4)
        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID,
            data__attributes__identification_id=str(ubble_identification),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=document_birth_date.date().isoformat(),
                ),
            ],
        )
        with ubble_mocker(
            ubble_identification,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        fraud_checks = sorted(user.beneficiaryFraudChecks, key=lambda fc: fc.id)

        assert len(fraud_checks) == 2
        assert fraud_checks[0].type == fraud_models.FraudCheckType.UBBLE
        assert fraud_checks[0].status == fraud_models.FraudCheckStatus.CANCELED
        assert fraud_checks[0].eligibilityType == users_models.EligibilityType.UNDERAGE
        assert fraud_checks[0].thirdPartyId != ubble_identification
        assert fraud_models.FraudReasonCode.ELIGIBILITY_CHANGED in fraud_checks[0].reasonCodes

        assert fraud_checks[1].type == fraud_models.FraudCheckType.UBBLE
        assert fraud_checks[1].status == fraud_models.FraudCheckStatus.OK
        assert fraud_checks[1].eligibilityType == users_models.EligibilityType.AGE18
        assert fraud_checks[1].thirdPartyId == ubble_identification

        db.session.refresh(user)
        assert not ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)

    @freezegun.freeze_time("2020-05-05")
    def test_ubble_workflow_with_eligibility_change_18_19(self, ubble_mocker):
        # User set his birth date as if 18 years old
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2003, month=5, day=4))
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        ubble_identification = fraud_check.thirdPartyId

        # Receiving a response from the UBBLE service, saying the user is 19 years old
        document_birth_date = datetime.datetime(year=2001, month=5, day=4)
        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID,
            data__attributes__identification_id=str(ubble_identification),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=document_birth_date.date().isoformat()
                ),
            ],
        )
        with ubble_mocker(
            ubble_identification,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        fraud_checks = user.beneficiaryFraudChecks
        assert len(fraud_checks) == 1

        assert fraud_checks[0].type == fraud_models.FraudCheckType.UBBLE
        assert fraud_checks[0].status == fraud_models.FraudCheckStatus.KO
        assert fraud_checks[0].eligibilityType == users_models.EligibilityType.AGE18
        assert fraud_checks[0].thirdPartyId == ubble_identification
        assert fraud_models.FraudReasonCode.AGE_TOO_OLD in fraud_checks[0].reasonCodes

    def test_ubble_workflow_updates_user_when_processed(self, ubble_mocker):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2002, month=5, day=6))
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.INVALID,
            data__attributes__identification_id=str(fraud_check.thirdPartyId),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=datetime.datetime(year=2002, month=5, day=4).date().isoformat()
                ),
            ],
        )

        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        db.session.refresh(user)
        assert user.dateOfBirth == datetime.datetime(year=2002, month=5, day=4)

    def test_ubble_workflow_does_not_erase_user_data(self, ubble_mocker):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2002, month=5, day=6))
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.INVALID,
            data__attributes__identification_id=str(fraud_check.thirdPartyId),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(attributes__birth_date=None),
            ],
        )

        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        db.session.refresh(user)
        assert user.dateOfBirth == datetime.datetime(year=2002, month=5, day=6)

    @freezegun.freeze_time("2019-05-05")
    def test_ubble_workflow_started_at_19_with_previous_attempt_at_18(self, ubble_mocker, db_session):
        # Given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2000, month=5, day=1))
        # User started a ubble workflow at 18 years old and was rejected
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.KO,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=datetime.datetime(year=2018, month=5, day=4),
        )
        # User started a new ubble workflow at 19 years old
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=datetime.datetime(year=2019, month=5, day=4),
        )

        # When
        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID,
            data__attributes__identification_id=str(fraud_check.thirdPartyId),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=datetime.datetime(year=2000, month=5, day=1).date().isoformat()
                ),
            ],
        )

        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        db_session.refresh(fraud_check)

        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18
        assert fraud_check.thirdPartyId == fraud_check.thirdPartyId

    @freezegun.freeze_time("2020-05-05")
    def test_ubble_workflow_started_at_20_with_previous_attempt_at_18(self, ubble_mocker, db_session):
        # Given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2000, month=5, day=1))
        # User started a ubble workflow at 18 years old and was rejected
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.KO,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=datetime.datetime(year=2018, month=5, day=4),
        )
        # User started a new ubble workflow at 19 years old
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=datetime.datetime(year=2020, month=5, day=4),
        )

        # When
        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID,
            data__attributes__identification_id=str(fraud_check.thirdPartyId),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=datetime.datetime(year=2000, month=5, day=1).date().isoformat()
                ),
            ],
        )

        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        db_session.refresh(fraud_check)

        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.status == fraud_models.FraudCheckStatus.KO
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18
        assert fraud_check.thirdPartyId == fraud_check.thirdPartyId
        assert fraud_check.reason == "L'utilisateur a dépassé l'âge maximum (20 ans)"
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.AGE_TOO_OLD]


@pytest.mark.usefixtures("db_session")
@freezegun.freeze_time("2022-11-02")
class UbbleSubscriptionItemStatusTest:
    def test_not_eligible_without_check(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2002, month=1, day=1))

        status = ubble_subscription_api.get_ubble_subscription_item_status(user, users_models.EligibilityType.AGE18, [])

        assert status == subscription_models.SubscriptionItemStatus.VOID

    def test_eligible_without_check(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2004, month=1, day=1))

        status = ubble_subscription_api.get_ubble_subscription_item_status(user, users_models.EligibilityType.AGE18, [])

        assert status == subscription_models.SubscriptionItemStatus.TODO

    def test_not_eligible_with_checks(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2002, month=1, day=1))
        check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        status = ubble_subscription_api.get_ubble_subscription_item_status(
            user, users_models.EligibilityType.AGE18, [check]
        )

        assert status == subscription_models.SubscriptionItemStatus.SUSPICIOUS

    def test_checks_ko_and_ok(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2004, month=1, day=1))
        ko_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            status=fraud_models.FraudCheckStatus.KO,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        ok_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        status = ubble_subscription_api.get_ubble_subscription_item_status(
            user, users_models.EligibilityType.AGE18, [ko_check, ok_check]
        )

        assert status == subscription_models.SubscriptionItemStatus.OK

    def test_checks_ko_retryable(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2004, month=1, day=1))
        ko_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            status=fraud_models.FraudCheckStatus.KO,
            type=fraud_models.FraudCheckType.UBBLE,
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_EXPIRED],
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        canceled_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            status=fraud_models.FraudCheckStatus.CANCELED,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        status = ubble_subscription_api.get_ubble_subscription_item_status(
            user, users_models.EligibilityType.AGE18, [ko_check, canceled_check]
        )

        assert status == subscription_models.SubscriptionItemStatus.TODO

    def test_checks_ko_retryable_too_many(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2004, month=1, day=1))
        ko_checks = fraud_factories.BeneficiaryFraudCheckFactory.create_batch(
            3,
            user=user,
            status=fraud_models.FraudCheckStatus.KO,
            type=fraud_models.FraudCheckType.UBBLE,
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_EXPIRED],
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        status = ubble_subscription_api.get_ubble_subscription_item_status(
            user, users_models.EligibilityType.AGE18, ko_checks
        )

        assert status == subscription_models.SubscriptionItemStatus.KO


class DownloadUbbleDocumentPictureTest:
    picture_path = "https://storage.ubble.ai/FRA-I4-Front-1640326309790.png"
    ubble_content = UbbleContent(signed_image_front_url=picture_path, signed_image_back_url=None)
    fraud_check = BeneficiaryFraudCheck(userId=123, thirdPartyId="abcd")

    def test_download_ubble_document_pictures_with_expired_request(self, requests_mock, caplog):
        # Given
        requests_mock.register_uri(
            "GET",
            self.picture_path,
            status_code=403,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <Error>
                    <Code>AccessDenied</Code>
                    <Message>Request has expired</Message>
                </Error>""",
        )

        # When
        with pytest.raises(requests_utils.ExternalAPIException) as exc_info:
            ubble_subscription_api._download_and_store_ubble_picture(self.fraud_check, self.picture_path, "front")

        # Then
        assert exc_info.value.is_retryable is False

        record = caplog.records[0]
        assert record.levelname == "ERROR"
        assert record.message == "Ubble picture-download: request has expired"
        assert self.picture_path in record.extra["url"]

    def test_download_ubble_document_pictures_with_empty_file(self, requests_mock, caplog):
        # Given
        empty_file = BytesIO()

        requests_mock.register_uri(
            "GET", self.picture_path, status_code=200, headers={"content-type": "image/png"}, body=empty_file
        )

        with pytest.raises(ubble_exceptions.UbbleDownloadedFileEmpty):
            ubble_subscription_api._download_and_store_ubble_picture(self.fraud_check, self.picture_path, "front")

        # Then
        record = caplog.records[0]
        assert "Ubble picture-download: downloaded file is empty" in record.message
        assert self.picture_path in record.extra["url"]

    def test_download_ubble_document_pictures_with_unknown_error(self, requests_mock, caplog):
        # Given
        requests_mock.register_uri("GET", self.picture_path, status_code=503)

        # When
        with pytest.raises(requests_utils.ExternalAPIException) as exc_info:
            ubble_subscription_api._download_and_store_ubble_picture(self.fraud_check, self.picture_path, "front")

        # Then
        assert exc_info.value.is_retryable is True

        record = caplog.records[0]
        assert "Ubble picture-download: external error" in record.message
        assert self.picture_path in record.extra["url"]
        assert record.extra["status_code"] == 503

    @patch("pcapi.connectors.beneficiaries.outscale.boto3.client")
    def test_download_ubble_document_pictures_successfully(self, mock_s3_client, requests_mock):
        # Given
        with open(f"{IMAGES_DIR}/carte_identite_front.png", "rb") as img:
            identity_file_picture = BytesIO(img.read())

        requests_mock.register_uri(
            "GET", self.picture_path, status_code=200, headers={"content-type": "image/png"}, body=identity_file_picture
        )

        # When
        ubble_subscription_api._download_and_store_ubble_picture(self.fraud_check, self.picture_path, "front")

        assert mock_s3_client.return_value.upload_file.call_count == 1


@pytest.mark.usefixtures("db_session")
class ArchiveUbbleUserIdPicturesTest:
    front_picture_url = "https://storage.ubble.ai/front-picture.png?response-content-type=image%2Fpng"
    back_picture_url = "https://storage.ubble.ai/back-picture.png?response-content-type=image%2Fpng"

    def test_archive_ubble_user_id_pictures_with_unknown_fraud_check(self):
        # Given
        unknown_fraud_check_id = "unknown_fraud_check_id"

        # When
        with pytest.raises(BeneficiaryFraudCheckMissingException) as error:
            ubble_subscription_api.archive_ubble_user_id_pictures(unknown_fraud_check_id)

        # Then
        assert f"No validated Identity fraudCheck found with identification_id {unknown_fraud_check_id}" in str(
            error.value
        )

    def test_archive_ubble_user_id_pictures_fraud_check_is_not_ok(self, ubble_mocker, requests_mock):
        # Given
        fraud_check = BeneficiaryFraudCheckFactory(status=FraudCheckStatus.KO, type=FraudCheckType.UBBLE)

        # When
        with pytest.raises(IncompatibleFraudCheckStatus) as error:
            ubble_subscription_api.archive_ubble_user_id_pictures(fraud_check.thirdPartyId)

        # Then
        assert (
            f"Fraud check status FraudCheckStatus.KO is incompatible with pictures archives for identification_id {fraud_check.thirdPartyId}"
            in str(error.value)
        )

    def test_archive_ubble_user_id_pictures_no_file_saved(self, ubble_mocker, requests_mock):
        # Given
        fraud_check = BeneficiaryFraudCheckFactory(status=FraudCheckStatus.OK, type=FraudCheckType.UBBLE)

        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID,
            data__attributes__identification_id=str(fraud_check.thirdPartyId),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__signed_image_front_url=self.front_picture_url,
                    attributes__signed_image_back_url=self.back_picture_url,
                ),
            ],
        )

        requests_mock.register_uri("GET", self.front_picture_url, status_code=403)
        requests_mock.register_uri("GET", self.back_picture_url, status_code=403)

        # When
        with pytest.raises(requests_utils.ExternalAPIException) as exc_info:
            with ubble_mocker(
                fraud_check.thirdPartyId,
                json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
                mocker=requests_mock,
            ):
                ubble_subscription_api.archive_ubble_user_id_pictures(fraud_check.thirdPartyId)

        # Then
        assert exc_info.value.is_retryable is False
        db.session.refresh(fraud_check)
        assert fraud_check.idPicturesStored is False

    @patch("pcapi.connectors.beneficiaries.outscale.boto3.client")
    def test_archive_ubble_user_id_pictures_only_front_saved(self, mock_s3_client, ubble_mocker, requests_mock):
        # Given
        fraud_check = BeneficiaryFraudCheckFactory(status=FraudCheckStatus.OK, type=FraudCheckType.UBBLE)

        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID,
            data__attributes__identification_id=str(fraud_check.thirdPartyId),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__signed_image_front_url=self.front_picture_url,
                    attributes__signed_image_back_url=self.back_picture_url,
                ),
            ],
        )
        with open(f"{IMAGES_DIR}/carte_identite_front.png", "rb") as img:
            identity_file_picture_front = BytesIO(img.read())

        requests_mock.register_uri(
            "GET",
            self.front_picture_url,
            status_code=200,
            headers={"content-type": "image/png"},
            body=identity_file_picture_front,
        )
        requests_mock.register_uri("GET", self.back_picture_url, status_code=503)

        # When
        with pytest.raises(requests_utils.ExternalAPIException) as exc_info:
            with ubble_mocker(
                fraud_check.thirdPartyId,
                json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
                mocker=requests_mock,
            ):
                ubble_subscription_api.archive_ubble_user_id_pictures(fraud_check.thirdPartyId)

        # Then
        assert exc_info.value.is_retryable is True
        assert fraud_check.idPicturesStored is False
        assert mock_s3_client.return_value.upload_file.call_count == 1

    @patch("pcapi.connectors.beneficiaries.outscale.boto3.client")
    def test_archive_ubble_user_id_pictures_both_files_saved(self, mock_s3_client, ubble_mocker, requests_mock):
        # Given
        fraud_check = BeneficiaryFraudCheckFactory(status=FraudCheckStatus.OK, type=FraudCheckType.UBBLE)

        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID,
            data__attributes__identification_id=str(fraud_check.thirdPartyId),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__signed_image_front_url=self.front_picture_url,
                    attributes__signed_image_back_url=self.back_picture_url,
                ),
            ],
        )

        with open(f"{IMAGES_DIR}/carte_identite_front.png", "rb") as img_front:
            identity_file_picture_front = BytesIO(img_front.read())
        with open(f"{IMAGES_DIR}/carte_identite_back.png", "rb") as img_back:
            identity_file_picture_back = BytesIO(img_back.read())

        requests_mock.register_uri(
            "GET",
            self.front_picture_url,
            status_code=200,
            headers={"content-type": "image/png"},
            body=identity_file_picture_front,
        )
        requests_mock.register_uri(
            "GET",
            self.back_picture_url,
            status_code=200,
            headers={"content-type": "image/png"},
            body=identity_file_picture_back,
        )

        expected_id_pictures_stored = True

        # When
        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
            mocker=requests_mock,
        ):
            ubble_subscription_api.archive_ubble_user_id_pictures(fraud_check.thirdPartyId)

        # Then
        db.session.refresh(fraud_check)
        assert fraud_check.idPicturesStored is expected_id_pictures_stored
        assert mock_s3_client.return_value.upload_file.call_count == 2

    @patch("pcapi.connectors.beneficiaries.outscale.boto3.client")
    def test_archive_ubble_user_id_pictures_all_expected_files_saved(self, mock_s3_client, ubble_mocker, requests_mock):
        # Given
        fraud_check = BeneficiaryFraudCheckFactory(status=FraudCheckStatus.OK, type=FraudCheckType.UBBLE)

        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID,
            data__attributes__identification_id=str(fraud_check.thirdPartyId),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__signed_image_front_url=self.front_picture_url,
                    attributes__signed_image_back_url=None,
                    attributes__document_type="Passport",
                ),
            ],
        )

        with open(f"{IMAGES_DIR}/carte_identite_front.png", "rb") as img_front:
            identity_file_picture_front = BytesIO(img_front.read())

        requests_mock.register_uri(
            "GET",
            self.front_picture_url,
            status_code=200,
            headers={"content-type": "image/png"},
            body=identity_file_picture_front,
        )

        expected_id_pictures_stored = True

        # When
        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
            mocker=requests_mock,
        ):
            ubble_subscription_api.archive_ubble_user_id_pictures(fraud_check.thirdPartyId)

        # Then
        db.session.refresh(fraud_check)
        assert fraud_check.idPicturesStored is expected_id_pictures_stored
        assert mock_s3_client.return_value.upload_file.call_count == 1


@pytest.mark.usefixtures("db_session")
class SubscriptionMessageTest:
    def test_started(self):
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE, status=FraudCheckStatus.STARTED
        )
        assert ubble_subscription_api.get_ubble_subscription_message(fraud_check, False) is None

    def test_pending(self):
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE, status=FraudCheckStatus.PENDING
        )
        assert ubble_subscription_api.get_ubble_subscription_message(
            fraud_check, False
        ) == subscription_models.SubscriptionMessage(
            user_message="Ton document d'identité est en cours de vérification.",
            call_to_action=None,
            pop_over_icon=subscription_models.PopOverIcon.CLOCK,
        )

    def test_ok(self):
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE, status=FraudCheckStatus.OK
        )
        assert ubble_subscription_api.get_ubble_subscription_message(fraud_check, False) is None

    @pytest.mark.parametrize(
        "reason_codes,expected_message",
        [
            (
                [fraud_models.FraudReasonCode.ID_CHECK_EXPIRED],
                "Ton document d'identité est expiré. Réessaye avec un passeport ou une carte d'identité française en cours de validité.",
            ),
            (
                [fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC],
                "Le document que tu as présenté n’est pas accepté car il s’agit d’une photo ou d’une copie de l’original. Réessaye avec un document original en cours de validité.",
            ),
            (
                [fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED],
                "Ton document d'identité ne te permet pas de bénéficier du pass Culture. Réessaye avec un passeport ou une carte d'identité française en cours de validité.",
            ),
            (
                [fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE],
                "Nous n'arrivons pas à lire ton document. Réessaye avec un passeport ou une carte d'identité française en cours de validité dans un lieu bien éclairé.",
            ),
            (
                None,
                "La vérification de ton identité a échoué. Tu peux réessayer.",
            ),
        ],
    )
    def test_retryable(self, reason_codes, expected_message):
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=FraudCheckStatus.SUSPICIOUS,
            reasonCodes=reason_codes,
        )
        assert ubble_subscription_api.get_ubble_subscription_message(
            fraud_check, True
        ) == subscription_models.SubscriptionMessage(
            user_message=expected_message,
            call_to_action=subscription_models.CallToActionMessage(
                title="Réessayer la vérification de mon identité",
                link="passculture://verification-identite/identification",
                icon=subscription_models.CallToActionIcon.RETRY,
            ),
            pop_over_icon=None,
        )

    def test_not_retryable_ask_support(self):
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.DUPLICATE_USER],
        )
        assert ubble_subscription_api.get_ubble_subscription_message(
            fraud_check, False
        ) == subscription_models.SubscriptionMessage(
            user_message="Ton dossier a été refusé : il y a déjà un compte à ton nom sur le pass Culture. Tu peux contacter le support pour plus d'informations.",
            call_to_action=subscription_models.CallToActionMessage(
                title="Contacter le support",
                link=f"mailto:support@example.com?subject=%23{fraud_check.user.id}+-+Mon+inscription+sur+le+pass+Culture+est+bloqu%C3%A9e",
                icon=subscription_models.CallToActionIcon.EMAIL,
            ),
            pop_over_icon=None,
        )

    @pytest.mark.parametrize(
        "reason_codes,expected_message",
        [
            (
                [fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED],
                "Ton document d'identité ne te permet pas de bénéficier du pass Culture. Rends-toi sur le site Démarches-Simplifiées pour renouveler ta demande.",
            ),
            (
                [fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER],
                "Ton dossier a été refusé. Rends-toi sur le site Démarches-Simplifiées pour renouveler ta demande.",
            ),
            (
                None,
                "Désolé, la vérification de ton identité n'a pas pu aboutir. Rends-toi sur le site Démarches-Simplifiées pour renouveler ta demande.",
            ),
        ],
    )
    def test_not_retryable_go_dms(self, reason_codes, expected_message):
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=FraudCheckStatus.SUSPICIOUS,
            reasonCodes=reason_codes,
        )
        assert ubble_subscription_api.get_ubble_subscription_message(
            fraud_check, False
        ) == subscription_models.SubscriptionMessage(
            user_message=expected_message,
            call_to_action=subscription_models.CallToActionMessage(
                title="Accéder au site Démarches-Simplifiées",
                link="passculture://verification-identite/demarches-simplifiees",
                icon=subscription_models.CallToActionIcon.EXTERNAL,
            ),
            pop_over_icon=None,
        )

    def test_not_eligible(self):
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.AGE_TOO_OLD],
        )
        assert ubble_subscription_api.get_ubble_subscription_message(
            fraud_check, False
        ) == subscription_models.SubscriptionMessage(
            user_message="Ton dossier a été refusé : tu ne peux pas bénéficier du pass Culture. Il est réservé aux jeunes de 15 à 18 ans.",
            call_to_action=None,
            pop_over_icon=subscription_models.PopOverIcon.ERROR,
        )
