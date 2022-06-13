import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.scripts.force_19yo_dms_import import force_19yo_dms_import


@pytest.mark.usefixtures("db_session")
class User19YearOldActivationTest:
    def test_user_should_be_activated(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=19, months=4),
            dateCreated=datetime.datetime.utcnow() - relativedelta(months=5),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            status=fraud_models.FraudCheckStatus.OK,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.KO,
            reasonCodes=[fraud_models.FraudReasonCode.NOT_ELIGIBLE],
        )

        force_19yo_dms_import(dry_run=False)

        assert user.has_beneficiary_role
        assert user.has_active_deposit

    def test_user_required_to_validate_user_profiling(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=19, months=4),
            dateCreated=datetime.datetime.utcnow() - relativedelta(months=5),
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            status=fraud_models.FraudCheckStatus.OK,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.KO,
            reasonCodes=[fraud_models.FraudReasonCode.NOT_ELIGIBLE],
        )

        force_19yo_dms_import(dry_run=False)
        # TODO : a 19yo user which has applied at 18 year old might be able to activate his account
        assert subscription_api.get_next_subscription_step(user) == None

    def test_user_should_not_be_activated_dry_run(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=19, months=4),
            dateCreated=datetime.datetime.utcnow() - relativedelta(months=5),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.KO,
            reasonCodes=[fraud_models.FraudReasonCode.NOT_ELIGIBLE],
        )

        assert not user.has_beneficiary_role
        assert not user.has_active_deposit

    def test_user_should_not_be_activated(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=19, months=4),
            dateCreated=datetime.datetime.utcnow() - relativedelta(months=5),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.KO,
            reasonCodes=[fraud_models.FraudReasonCode.NOT_ELIGIBLE],
        )

        force_19yo_dms_import()
        assert not user.has_beneficiary_role
        assert not user.has_active_deposit
