import datetime
from unittest.mock import call
from unittest.mock import patch

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.connectors import api_particulier
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import tasks
from pcapi.models import db
from pcapi.utils import date as date_utils

from tests.core.subscription.bonus import bonus_fixtures


pytestmark = pytest.mark.usefixtures("db_session")


class QuotientFamilialBonusTaskTest:
    @patch("pcapi.connectors.api_particulier.get_quotient_familial")
    def test_apply_for_quotient_familial_bonus_task(self, mocked_get_quotient_familial):
        custodian = subscription_factories.BonusCreditPersonFactory.create()
        fraud_check = subscription_factories.QFBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory.build(
                custodian=custodian
            ).model_dump(),
        )
        fraud_check_id = fraud_check.id
        birth_date = fraud_check.user.validatedBirthDate
        mocked_get_quotient_familial.return_value = bonus_fixtures.QF_DESERIALIZED_RESPONSE

        payload = tasks.BonusTaskPayload(fraud_check_id=fraud_check_id)
        tasks.apply_for_quotient_familial_bonus_task.delay(payload.model_dump(mode="json"))

        assert len(mocked_get_quotient_familial.mock_calls) == 12
        mocked_get_quotient_familial.assert_called_with(
            custodian, birth_date + relativedelta(years=17) + relativedelta(months=11)
        )

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).get(fraud_check_id)
        assert fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD]

    @patch("pcapi.connectors.api_particulier.get_quotient_familial")
    def test_replan_fraud_check_on_exception(self, mocked_get_quotient_familial):
        fraud_check = subscription_factories.QFBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        mocked_get_quotient_familial.side_effect = RuntimeError

        payload = tasks.BonusTaskPayload(fraud_check_id=fraud_check.id)
        tasks.apply_for_quotient_familial_bonus_task.delay(payload.model_dump(mode="json"))

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).get(fraud_check.id)
        assert fraud_check.status == subscription_models.FraudCheckStatus.STARTED
        assert (
            datetime.datetime.fromisoformat(fraud_check.resultContent["next_retry_at"]) > date_utils.get_naive_utc_now()
        )


class AdultDisabilityBonusTaskTest:
    @patch("pcapi.connectors.api_particulier.get_disabled_adult_allowance")
    def test_apply_for_adult_disability_bonus_task(self, mocked_disabled_adult_allowance):
        person = subscription_factories.BonusCreditPersonFactory.create()
        fraud_check = subscription_factories.AAHBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory.build(
                person=person
            ).model_dump(),
        )
        fraud_check_id = fraud_check.id
        mocked_disabled_adult_allowance.return_value = api_particulier.DisabledAdultAllowanceResponse.model_validate(
            bonus_fixtures.AAH_NOT_RECIPIENT_RESPONSE
        )

        payload = tasks.BonusTaskPayload(fraud_check_id=fraud_check_id)
        tasks.apply_for_adult_disability_bonus_task.delay(payload.model_dump(mode="json"))

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).get(fraud_check_id)
        assert fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.NOT_RECIPIENT]

    @patch("pcapi.connectors.api_particulier.get_disabled_adult_allowance")
    def test_replan_fraud_check_on_exception(self, mocked_disabled_adult_allowance):
        fraud_check = subscription_factories.AAHBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        mocked_disabled_adult_allowance.side_effect = RuntimeError

        payload = tasks.BonusTaskPayload(fraud_check_id=fraud_check.id)
        tasks.apply_for_adult_disability_bonus_task.delay(payload.model_dump(mode="json"))

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).get(fraud_check.id)
        assert fraud_check.status == subscription_models.FraudCheckStatus.STARTED
        assert (
            datetime.datetime.fromisoformat(fraud_check.resultContent["next_retry_at"]) > date_utils.get_naive_utc_now()
        )


class DisabledChildEducationBonusTaskTest:
    @patch("pcapi.connectors.api_particulier.get_disabled_child_education_allowance")
    def test_apply_for_disabled_child_education_allowance(self, mocked_disabled_child_education_allowance):
        person = subscription_factories.BonusCreditPersonFactory.create()
        fraud_check = subscription_factories.AEEHBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.DisabledChildEducationBonusCreditContentFactory.build(
                person=person
            ).model_dump(),
        )
        fraud_check_id = fraud_check.id
        mocked_disabled_child_education_allowance.return_value = (
            api_particulier.DisabledChildEducationAllowanceResponse.model_validate(
                bonus_fixtures.AEEH_NOT_RECIPIENT_RESPONSE
            )
        )

        payload = tasks.BonusTaskPayload(fraud_check_id=fraud_check_id)
        tasks.apply_for_disabled_child_education_bonus_task.delay(payload.model_dump(mode="json"))

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).get(fraud_check_id)
        assert fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.NOT_RECIPIENT]

    @patch("pcapi.connectors.api_particulier.get_disabled_child_education_allowance")
    def test_replan_fraud_check_on_exception(self, mocked_disabled_child_education_allowance):
        fraud_check = subscription_factories.AEEHBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        mocked_disabled_child_education_allowance.side_effect = RuntimeError

        payload = tasks.BonusTaskPayload(fraud_check_id=fraud_check.id)
        tasks.apply_for_disabled_child_education_bonus_task.delay(payload.model_dump(mode="json"))

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).get(fraud_check.id)
        assert fraud_check.status == subscription_models.FraudCheckStatus.STARTED
        assert (
            datetime.datetime.fromisoformat(fraud_check.resultContent["next_retry_at"]) > date_utils.get_naive_utc_now()
        )


class RecoverStartedBonusCreditApplicationsTest:
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_quotient_familial_bonus_task.delay")
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_adult_disability_bonus_task.delay")
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_disabled_child_education_bonus_task.delay")
    def test_recover_started_bonus_credit_applications_full_page(
        self, mocked_apply_for_aeeh_task, mocked_apply_for_aah_task, mocked_apply_for_qf_task
    ):
        twelve_hours_ago = datetime.datetime.now(tz=None) - relativedelta(hours=12)
        started_fraud_check_1 = subscription_factories.QFBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, resultContent={"next_retry_at": twelve_hours_ago}
        )
        started_fraud_check_2 = subscription_factories.QFBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, resultContent={"next_retry_at": twelve_hours_ago}
        )
        aah_fraud_check = subscription_factories.AAHBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, resultContent={"next_retry_at": twelve_hours_ago}
        )
        aeeh_fraud_check = subscription_factories.AEEHBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, resultContent={"next_retry_at": twelve_hours_ago}
        )

        tasks.recover_started_bonus_credit_applications(
            cutoff_time=twelve_hours_ago + relativedelta(minutes=1), page_size=12 + 12 + 1 + 1
        )

        mocked_apply_for_qf_task.assert_has_calls(
            [
                call(payload={"fraud_check_id": started_fraud_check_1.id}),
                call(payload={"fraud_check_id": started_fraud_check_2.id}),
            ],
            any_order=True,
        )
        mocked_apply_for_aah_task.assert_has_calls([call(payload={"fraud_check_id": aah_fraud_check.id})])
        mocked_apply_for_aeeh_task.assert_has_calls([call(payload={"fraud_check_id": aeeh_fraud_check.id})])

    @patch("pcapi.core.subscription.bonus.tasks.apply_for_quotient_familial_bonus_task.delay")
    def test_recover_started_bonus_credit_applications_for_a_user(self, mocked_apply_for_qf_task):
        twelve_hours_ago = datetime.datetime.now(tz=None) - relativedelta(hours=12)
        started_fraud_check_1 = subscription_factories.QFBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, resultContent={"next_retry_at": twelve_hours_ago}
        )
        _started_fraud_check_2 = subscription_factories.QFBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, resultContent={"next_retry_at": twelve_hours_ago}
        )

        tasks.recover_started_bonus_credit_applications(user_id=started_fraud_check_1.userId)

        mocked_apply_for_qf_task.assert_has_calls(
            [
                call(payload={"fraud_check_id": started_fraud_check_1.id}),
            ]
        )

    @patch("pcapi.core.subscription.bonus.tasks.apply_for_quotient_familial_bonus_task.delay")
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_adult_disability_bonus_task.delay")
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_disabled_child_education_bonus_task.delay")
    def test_recovery_ignores_date_planned_too_late(
        self, mocked_apply_for_aeeh_task, mocked_apply_for_aah_task, mocked_apply_for_qf_task
    ):
        cutoff_date = datetime.datetime.now(tz=None)
        too_late = cutoff_date + relativedelta(minutes=1)
        subscription_factories.QFBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, resultContent={"next_retry_at": too_late}
        )
        subscription_factories.AAHBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, resultContent={"next_retry_at": too_late}
        )
        subscription_factories.AEEHBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, resultContent={"next_retry_at": too_late}
        )

        tasks.recover_started_bonus_credit_applications(cutoff_time=cutoff_date)

        mocked_apply_for_qf_task.assert_not_called()
        mocked_apply_for_aah_task.assert_not_called()
        mocked_apply_for_aeeh_task.assert_not_called()

    @patch("pcapi.core.subscription.bonus.tasks.apply_for_quotient_familial_bonus_task.delay")
    def test_recovery_does_not_overflow_page_size(self, mocked_apply_for_qf_task):
        subscription_factories.QFBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED
        )

        tasks.recover_started_bonus_credit_applications(page_size=11)

        mocked_apply_for_qf_task.assert_not_called()
