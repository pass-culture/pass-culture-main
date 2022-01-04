import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import factories as users_factories
from pcapi.scripts.force_19yo_dms_import import force_19yo_dms_import


@pytest.mark.usefixtures("db_session")
class User19YearOldActivationTest:
    def test_user_should_be_activated(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.now() - relativedelta(years=19, months=4),
            dateCreated=datetime.datetime.now() - relativedelta(months=5),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.KO,
            reasonCodes=[fraud_models.FraudReasonCode.NOT_ELIGIBLE],
        )
        fraud_factories.BeneficiaryFraudResultFactory(
            user=user,
            status=fraud_models.FraudStatus.KO,
            reason_codes=[fraud_models.FraudReasonCode.NOT_ELIGIBLE],
        )

        force_19yo_dms_import(dry_run=False)

        assert user.has_beneficiary_role
        assert user.has_active_deposit

    def test_user_should_not_be_activated_dry_run(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.now() - relativedelta(years=19, months=4),
            dateCreated=datetime.datetime.now() - relativedelta(months=5),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.KO,
            reasonCodes=[fraud_models.FraudReasonCode.NOT_ELIGIBLE],
        )
        fraud_factories.BeneficiaryFraudResultFactory(
            user=user,
            status=fraud_models.FraudStatus.KO,
            reason_codes=[fraud_models.FraudReasonCode.NOT_ELIGIBLE],
        )

        assert not user.has_beneficiary_role
        assert not user.has_active_deposit

    def test_user_should_not_be_activated(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.now() - relativedelta(years=19, months=4),
            dateCreated=datetime.datetime.now() - relativedelta(months=5),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.KO,
            reasonCodes=[fraud_models.FraudReasonCode.NOT_ELIGIBLE],
        )
        fraud_factories.BeneficiaryFraudResultFactory(
            user=user,
            status=fraud_models.FraudStatus.KO,
            reason_codes=[fraud_models.FraudReasonCode.NOT_ELIGIBLE],
        )

        force_19yo_dms_import()
        assert not user.has_beneficiary_role
        assert not user.has_active_deposit
