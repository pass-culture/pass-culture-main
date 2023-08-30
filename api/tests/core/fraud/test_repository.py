import datetime

import pytest

from pcapi.core.fraud import repository
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.factories as users_factories



class RepositoryTest:
    def should_find_ko_reviews(self):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudReviewFactory(user=user, review=fraud_models.FraudReviewStatus.KO)

        assert repository.has_admin_ko_review(user)

    def should_override_ko_with_ok_review(self):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudReviewFactory(
            user=user, review=fraud_models.FraudReviewStatus.KO, dateReviewed=datetime.datetime(2020, 1, 1)
        )
        fraud_factories.BeneficiaryFraudReviewFactory(
            user=user, review=fraud_models.FraudReviewStatus.OK, dateReviewed=datetime.datetime(2020, 1, 2)
        )

        assert not repository.has_admin_ko_review(user)

    def should_use_latest_review(self):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudReviewFactory(
            user=user, review=fraud_models.FraudReviewStatus.OK, dateReviewed=datetime.datetime(2020, 1, 1)
        )
        fraud_factories.BeneficiaryFraudReviewFactory(
            user=user, review=fraud_models.FraudReviewStatus.KO, dateReviewed=datetime.datetime(2020, 1, 2)
        )

        assert repository.has_admin_ko_review(user)
