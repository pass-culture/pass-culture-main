import pytest

from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.dms import repository as dms_repository
from pcapi.utils import date as date_utils


@pytest.mark.usefixtures("db_session")
class RepositoryUnitTest:
    def test_get_orphan_dms_application_by_application_id(self):
        subscription_factories.OrphanDmsApplicationFactory(application_id=88)
        assert dms_repository.get_orphan_dms_application_by_application_id(88) is not None
        assert dms_repository.get_orphan_dms_application_by_application_id(99) is None

    def test_create_orphan_dms_application(self):
        dms_repository.create_orphan_dms_application(
            application_number=88,
            procedure_number=99,
            latest_modification_datetime=date_utils.get_naive_utc_now(),
            email="john.stiles@example.com",
        )
        assert dms_repository.get_orphan_dms_application_by_application_id(88) is not None


class GetAlreadyProcessedApplicationIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_already_processed_application_numbers(self):
        content = subscription_factories.DMSContentFactory(application_number=8888, procedure_number=123)
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=8888,
            resultContent=content,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.OK,
        )

        # Orphan application
        subscription_factories.OrphanDmsFraudCheckFactory(application_id=9999, process_id=123)
        subscription_factories.OrphanDmsFraudCheckFactory(application_id=9991, process_id=321)

        # Different procedure
        content = subscription_factories.DMSContentFactory(application_number=1111, procedure_number=2)
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=1111,
            resultContent=content,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.OK,
        )

        # No Content
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=2222,
            resultContent=None,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.ERROR,
        )

        application_numbers = dms_repository.get_already_processed_applications_ids(123)
        assert application_numbers == {8888, 9999, 2222}

    @pytest.mark.usefixtures("db_session")
    def test_already_processed_application_numbers_with_all_fraud_checks_status(self):
        content = subscription_factories.DMSContentFactory(application_number=1111, procedure_number=123)
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=1111,
            resultContent=content,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.KO,
        )
        content = subscription_factories.DMSContentFactory(application_number=2222, procedure_number=123)
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=2222,
            resultContent=content,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.OK,
        )
        content = subscription_factories.DMSContentFactory(application_number=3333, procedure_number=123)
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=3333,
            resultContent=content,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        content = subscription_factories.DMSContentFactory(application_number=4444, procedure_number=123)
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=4444,
            resultContent=content,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
        )
        content = subscription_factories.DMSContentFactory(application_number=5555, procedure_number=123)
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=5555,
            resultContent=content,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.PENDING,
        )
        content = subscription_factories.DMSContentFactory(application_number=6666, procedure_number=123)
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=6666,
            resultContent=content,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.CANCELED,
        )
        content = subscription_factories.DMSContentFactory(application_number=7777, procedure_number=123)
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=7777,
            resultContent=content,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.ERROR,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=8888,
            resultContent=None,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.ERROR,
        )

        application_numbers = dms_repository.get_already_processed_applications_ids(123)

        assert application_numbers == {1111, 2222, 4444, 6666, 7777, 8888}
