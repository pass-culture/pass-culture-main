from unittest.mock import patch

import pytest

from pcapi.connectors.dms import api as api_dms
from pcapi.core import testing
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.scripts.subscription.dms import archive_dms_applications

from tests.scripts.beneficiary.fixture import make_parsed_graphql_application


@pytest.mark.usefixtures("db_session")
class ArchiveDMSApplicationsTest:
    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    @patch.object(api_dms.DMSGraphQLClient, "archive_application")
    @testing.override_settings(DMS_ENROLLMENT_INSTRUCTOR="SomeInstructorId")
    def test_archive_applications(self, dms_archive, dms_applications):
        to_archive_applications_id = 123
        pending_applications_id = 456
        procedure_id = 1

        content = fraud_factories.DMSContentFactory(procedure_id=procedure_id)
        fraud_factories.BeneficiaryFraudCheckFactory(
            resultContent=content,
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.DMS,
            thirdPartyId=str(to_archive_applications_id),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            resultContent=content,
            status=fraud_models.FraudCheckStatus.STARTED,
            type=fraud_models.FraudCheckType.DMS,
            thirdPartyId=str(pending_applications_id),
        )
        dms_applications.return_value = [
            make_parsed_graphql_application(
                to_archive_applications_id, "accepte", application_techid="TO_ARCHIVE_TECHID"
            ),
            make_parsed_graphql_application(pending_applications_id, "accepte", application_techid="PENDING_ID"),
        ]

        archive_dms_applications.archive_applications(procedure_id, dry_run=False)

        dms_archive.assert_called_once()
        assert dms_archive.call_args[0] == ("TO_ARCHIVE_TECHID", "SomeInstructorId")
