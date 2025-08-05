import datetime

import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription.dms import repository
from pcapi.core.subscription.dms import repository as dms_repository


@pytest.mark.usefixtures("db_session")
class RepositoryUnitTest:
    def test_get_orphan_dms_application_by_application_id(self):
        fraud_factories.OrphanDmsApplicationFactory(application_id=88)
        assert repository.get_orphan_dms_application_by_application_id(88) is not None
        assert repository.get_orphan_dms_application_by_application_id(99) is None

    def test_create_orphan_dms_application(self):
        repository.create_orphan_dms_application(
            application_number=88,
            procedure_number=99,
            latest_modification_datetime=datetime.datetime.utcnow(),
            email="john.stiles@example.com",
        )
        assert repository.get_orphan_dms_application_by_application_id(88) is not None


class GetAlreadyProcessedApplicationIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_already_processed_application_numbers(self):
        content = fraud_factories.DMSContentFactory(application_number=8888, procedure_number=123)
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
        content = fraud_factories.DMSContentFactory(application_number=1111, procedure_number=2)
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

        application_numbers = dms_repository.get_already_processed_applications_ids(123)
        assert application_numbers == {8888, 9999, 2222}

    @pytest.mark.usefixtures("db_session")
    def test_already_processed_application_numbers_with_all_fraud_checks_status(self):
        content = fraud_factories.DMSContentFactory(application_number=1111, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=1111,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.KO,
        )
        content = fraud_factories.DMSContentFactory(application_number=2222, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=2222,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )
        content = fraud_factories.DMSContentFactory(application_number=3333, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=3333,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.STARTED,
        )
        content = fraud_factories.DMSContentFactory(application_number=4444, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=4444,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
        )
        content = fraud_factories.DMSContentFactory(application_number=5555, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=5555,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.PENDING,
        )
        content = fraud_factories.DMSContentFactory(application_number=6666, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=6666,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.CANCELED,
        )
        content = fraud_factories.DMSContentFactory(application_number=7777, procedure_number=123)
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

        application_numbers = dms_repository.get_already_processed_applications_ids(123)

        assert application_numbers == {1111, 2222, 4444, 6666, 7777, 8888}
