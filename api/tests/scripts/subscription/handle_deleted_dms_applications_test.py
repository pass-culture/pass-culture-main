import datetime
from unittest.mock import patch

import pytest

from pcapi.connectors.dms import api as api_dms
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.scripts.subscription.handle_deleted_dms_applications import get_latest_deleted_application_datetime
from pcapi.scripts.subscription.handle_deleted_dms_applications import handle_deleted_dms_applications

from tests.scripts.beneficiary.fixture import make_graphql_deleted_applications


class HandleDeletedDmsApplicationsTest:
    @pytest.mark.usefixtures("db_session")
    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_handle_deleted_dms_applications(self, execute_query):

        fraud_check_not_to_mark_as_deleted = fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="1", type=fraud_models.FraudCheckType.DMS
        )
        fraud_check_to_mark_as_deleted = fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="2", type=fraud_models.FraudCheckType.DMS
        )
        fraud_check_already_marked_as_deleted = fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="3",
            status=fraud_models.FraudCheckStatus.CANCELED,
            reason="Custom reason",
            type=fraud_models.FraudCheckType.DMS,
        )
        fraud_check_to_delete_with_empty_result_content = fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="4", type=fraud_models.FraudCheckType.DMS, resultContent=None
        )

        procedure_id = 1
        execute_query.return_value = make_graphql_deleted_applications(procedure_id, [2, 3, 4])

        handle_deleted_dms_applications(procedure_id)

        assert fraud_check_not_to_mark_as_deleted.status == fraud_models.FraudCheckStatus.PENDING
        assert fraud_check_to_mark_as_deleted.status == fraud_models.FraudCheckStatus.CANCELED
        assert fraud_check_already_marked_as_deleted.status == fraud_models.FraudCheckStatus.CANCELED
        assert fraud_check_to_delete_with_empty_result_content.status == fraud_models.FraudCheckStatus.CANCELED

        assert (
            fraud_check_to_delete_with_empty_result_content.reason
            == "Dossier supprimé sur démarches-simplifiées. Motif: user_request"
        )
        assert (
            fraud_check_to_mark_as_deleted.reason == "Dossier supprimé sur démarches-simplifiées. Motif: user_request"
        )
        assert fraud_check_already_marked_as_deleted.reason == "Custom reason"

        assert fraud_check_not_to_mark_as_deleted.resultContent.get("deletion_datetime") is None
        assert fraud_check_to_mark_as_deleted.resultContent.get("deletion_datetime") == "2021-10-01T22:00:00"
        assert fraud_check_to_delete_with_empty_result_content.resultContent is None

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
