import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription.dms.api import get_already_processed_applications_ids


class GetAlreadyProcessedApplicationIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_already_processed_application_ids(self):
        content = fraud_factories.DMSContentFactory(application_id=8888, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=8888,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )

        # Orphan application
        fraud_factories.OrphanDmsFraudCheckFactory(application_id=9999, process_id=123)
        fraud_factories.OrphanDmsFraudCheckFactory(application_id=9991, process_id=321)

        # Different procedure
        content = fraud_factories.DMSContentFactory(application_id=1111, procedure_id=2)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=1111,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )

        # No Content
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=2222,
            resultContent=None,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.ERROR,
        )

        application_ids = get_already_processed_applications_ids(123)
        assert application_ids == {8888, 9999, 2222}

    @pytest.mark.usefixtures("db_session")
    def test_already_processed_application_ids_with_all_fraud_checks_status(self):
        content = fraud_factories.DMSContentFactory(application_id=1111, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=1111,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.KO,
        )
        content = fraud_factories.DMSContentFactory(application_id=2222, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=2222,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )
        content = fraud_factories.DMSContentFactory(application_id=3333, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=3333,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.STARTED,
        )
        content = fraud_factories.DMSContentFactory(application_id=4444, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=4444,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
        )
        content = fraud_factories.DMSContentFactory(application_id=5555, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=5555,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.PENDING,
        )
        content = fraud_factories.DMSContentFactory(application_id=6666, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=6666,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.CANCELED,
        )
        content = fraud_factories.DMSContentFactory(application_id=7777, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=7777,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.ERROR,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=8888,
            resultContent=None,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.ERROR,
        )

        application_ids = get_already_processed_applications_ids(123)

        assert application_ids == {1111, 2222, 4444, 6666, 7777, 8888}
