import datetime

import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription.ubble.archive_past_identification_pictures import get_fraud_check_to_archive


class ArchivePastIdentificationPicturesTest:
    @pytest.mark.usefixtures("db_session")
    def test_get_fraud_check_to_archive(self):
        # Given
        start_date = datetime.datetime(2021, 1, 1)
        end_date = datetime.datetime(2021, 1, 31)

        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            dateCreated=datetime.datetime(2021, 1, 15),
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.UBBLE,
        )
        deprecated_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=f"{subscription_api.DEPRECATED_UBBLE_PREFIX}{fraud_check.thirdPartyId}",
            dateCreated=datetime.datetime(2021, 1, 15),
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.UBBLE,
        )

        # When
        fraud_checks_to_archive = get_fraud_check_to_archive(start_date, end_date, None)

        # Then
        assert len(fraud_checks_to_archive) == 1
        assert fraud_check in fraud_checks_to_archive
        assert deprecated_fraud_check not in fraud_checks_to_archive
