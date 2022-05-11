import datetime
from unittest.mock import patch

import pytest

from pcapi.connectors.dms import api as api_dms
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.scripts.subscription.handle_deleted_dms_applications import get_latest_deleted_application_datetime

from tests.scripts.beneficiary.fixture import make_graphql_deleted_applications


class HandleDeletedDmsApplicationsTest:
    @pytest.mark.usefixtures("db_session")
    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_get_latest_deleted_application_datetime(self, execute_query):
        procedure_id = 1
        latest_deletion_date = datetime.datetime(2020, 1, 1)

        dms_content_with_deletion_date = fraud_factories.DMSContentFactory(
            deletion_datetime=latest_deletion_date, procedure_id=procedure_id
        )
        dms_content_before_deletion_date = fraud_factories.DMSContentFactory(
            deletion_datetime=latest_deletion_date - datetime.timedelta(days=1), procedure_id=procedure_id
        )

        # fraud_check_deleted_last
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="8888",
            status=fraud_models.FraudCheckStatus.CANCELED,
            type=fraud_models.FraudCheckType.DMS,
            resultContent=dms_content_with_deletion_date,
        )
        # fraud_check_deleted_before_last
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="8889",
            status=fraud_models.FraudCheckStatus.CANCELED,
            type=fraud_models.FraudCheckType.DMS,
            resultContent=dms_content_before_deletion_date,
        )
        # fraud_check_with_empty_result_content
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="8890",
            status=fraud_models.FraudCheckStatus.CANCELED,
            type=fraud_models.FraudCheckType.DMS,
            resultContent=None,
        )

        execute_query.return_value = make_graphql_deleted_applications(procedure_id, [8888, 8889, 8890])

        assert get_latest_deleted_application_datetime(procedure_id) == latest_deletion_date
