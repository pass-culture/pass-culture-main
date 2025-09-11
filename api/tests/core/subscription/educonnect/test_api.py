import datetime

import pytest
import time_machine

from pcapi import settings
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.educonnect import api as educonnect_subscription_api


@pytest.mark.usefixtures("db_session")
class SubscriptionMessageTest:
    def test_ok(self):
        fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.EDUCONNECT, status=subscription_models.FraudCheckStatus.OK
        )
        assert educonnect_subscription_api.get_educonnect_subscription_message(fraud_check) is None

    @time_machine.travel("2022-09-05")
    def test_not_eligible(self):
        birth_date = datetime.date(1991, 4, 6)
        fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.KO,
            resultContent=subscription_factories.EduconnectContentFactory(birth_date=birth_date),
            reasonCodes=[subscription_models.FraudReasonCode.AGE_NOT_VALID],
        )
        assert educonnect_subscription_api.get_educonnect_subscription_message(
            fraud_check
        ) == subscription_schemas.SubscriptionMessage(
            user_message="Ton dossier a été refusé. La date de naissance sur ton compte Éduconnect (06/04/1991) indique que tu n'as pas entre 15 et 17 ans.",
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Réessayer la vérification de mon identité",
                link=f"{settings.WEBAPP_V2_URL}/verification-identite",
                icon=subscription_schemas.CallToActionIcon.RETRY,
            ),
            updated_at=fraud_check.updatedAt,
        )

    @time_machine.travel("2022-09-05")
    def test_ko_other_reason(self):
        fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=[subscription_models.FraudReasonCode.INE_NOT_WHITELISTED],
        )
        assert educonnect_subscription_api.get_educonnect_subscription_message(
            fraud_check
        ) == subscription_schemas.SubscriptionMessage(
            user_message="La vérification de ton identité a échoué. Tu peux réessayer.",
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Réessayer la vérification de mon identité",
                link=f"{settings.WEBAPP_V2_URL}/verification-identite",
                icon=subscription_schemas.CallToActionIcon.RETRY,
            ),
            updated_at=fraud_check.updatedAt,
        )
