import datetime

import pytest
import time_machine

from pcapi import settings
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.educonnect import api as educonnect_subscription_api


@pytest.mark.usefixtures("db_session")
class SubscriptionMessageTest:
    def test_ok(self):
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT, status=fraud_models.FraudCheckStatus.OK
        )
        assert educonnect_subscription_api.get_educonnect_subscription_message(fraud_check) is None

    @time_machine.travel("2022-09-05")
    def test_not_eligible(self):
        birth_date = datetime.date(1991, 4, 6)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.KO,
            resultContent=fraud_factories.EduconnectContentFactory(birth_date=birth_date),
            reasonCodes=[fraud_models.FraudReasonCode.AGE_NOT_VALID],
        )
        assert educonnect_subscription_api.get_educonnect_subscription_message(
            fraud_check
        ) == subscription_models.SubscriptionMessage(
            user_message="Ton dossier a été refusé. La date de naissance sur ton compte Éduconnect (06/04/1991) indique que tu n'as pas entre 15 et 17 ans.",
            call_to_action=subscription_models.CallToActionMessage(
                title="Réessayer la vérification de mon identité",
                link=f"{settings.WEBAPP_V2_URL}/verification-identite",
                icon=subscription_models.CallToActionIcon.RETRY,
            ),
            updated_at=fraud_check.updatedAt,
        )

    @time_machine.travel("2022-09-05")
    def test_ko_other_reason(self):
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.KO,
            reasonCodes=[fraud_models.FraudReasonCode.INE_NOT_WHITELISTED],
        )
        assert educonnect_subscription_api.get_educonnect_subscription_message(
            fraud_check
        ) == subscription_models.SubscriptionMessage(
            user_message="La vérification de ton identité a échoué. Tu peux réessayer.",
            call_to_action=subscription_models.CallToActionMessage(
                title="Réessayer la vérification de mon identité",
                link=f"{settings.WEBAPP_V2_URL}/verification-identite",
                icon=subscription_models.CallToActionIcon.RETRY,
            ),
            updated_at=fraud_check.updatedAt,
        )
