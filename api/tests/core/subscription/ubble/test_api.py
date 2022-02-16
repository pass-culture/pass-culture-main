import datetime
import json

from dateutil.relativedelta import relativedelta
import freezegun
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.fraud.ubble import models as ubble_fraud_models
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db

from tests.core.subscription.test_factories import IdentificationState
from tests.core.subscription.test_factories import UbbleIdentificationIncludedDocumentsFactory
from tests.core.subscription.test_factories import UbbleIdentificationIncludedReferenceDataChecksFactory
from tests.core.subscription.test_factories import UbbleIdentificationResponseFactory
from tests.test_utils import json_default


@pytest.mark.usefixtures("db_session")
class UbbleWorkflowTest:
    def test_start_ubble_workflow(self, ubble_mock):
        user = users_factories.UserFactory()
        redirect_url = ubble_subscription_api.start_ubble_workflow(user, redirect_url="https://example.com")
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

        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check, ubble_response.data.attributes.status)

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
            ubble_subscription_api.update_ubble_workflow(fraud_check, ubble_response.data.attributes.status)
            message = subscription_models.SubscriptionMessage.query.one()
            assert message.userMessage == "Ton document d'identité est en cours de vérification."
            assert message.popOverIcon == subscription_models.PopOverIcon.CLOCK

    def test_ubble_workflow_rejected_add_inapp_message(self, ubble_mocker):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.now() - relativedelta(years=18, months=1))
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
            ubble_subscription_api.update_ubble_workflow(fraud_check, ubble_response.data.attributes.status)
            message = subscription_models.SubscriptionMessage.query.one()
            assert (
                message.userMessage
                == "Ton dossier a été bloqué : Les informations que tu as renseignées ne correspondent pas à celles de ta pièce d'identité. Tu peux contacter le support pour plus d'informations."
            )
            assert (
                message.callToActionLink
                == subscription_messages.MAILTO_SUPPORT + subscription_messages.MAILTO_SUPPORT_PARAMS.format(id=user.id)
            )
            assert message.callToActionIcon == subscription_models.CallToActionIcon.EMAIL
            assert message.callToActionTitle == "Contacter le support"

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
            ubble_subscription_api.update_ubble_workflow(fraud_check, ubble_response.data.attributes.status)

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
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2002, month=5, day=4))
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
            ubble_subscription_api.update_ubble_workflow(fraud_check, ubble_response.data.attributes.status)

        fraud_checks = user.beneficiaryFraudChecks
        assert len(fraud_checks) == 2

        assert fraud_checks[0].type == fraud_models.FraudCheckType.UBBLE
        assert fraud_checks[0].status == fraud_models.FraudCheckStatus.CANCELED
        assert fraud_checks[0].eligibilityType == users_models.EligibilityType.AGE18
        assert fraud_checks[0].thirdPartyId == f"deprecated-{ubble_identification}"

        assert fraud_checks[1].type == fraud_models.FraudCheckType.UBBLE
        assert fraud_checks[1].status == fraud_models.FraudCheckStatus.KO
        assert fraud_checks[1].eligibilityType is None
        assert fraud_checks[1].thirdPartyId == ubble_identification
        assert fraud_models.FraudReasonCode.AGE_TOO_OLD in fraud_checks[1].reasonCodes

        assert user.age == 19
        assert not ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)

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
            ubble_subscription_api.update_ubble_workflow(fraud_check, ubble_response.data.attributes.status)

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
            ubble_subscription_api.update_ubble_workflow(fraud_check, ubble_response.data.attributes.status)

        db.session.refresh(user)
        assert user.dateOfBirth == datetime.datetime(year=2002, month=5, day=6)


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
