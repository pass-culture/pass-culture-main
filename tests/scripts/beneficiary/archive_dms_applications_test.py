import logging
from unittest.mock import patch

import pytest

from pcapi.connectors.api_demarches_simplifiees import DMSGraphQLClient
from pcapi.core.users import factories as users_factories
from pcapi.models import ImportStatus
from pcapi.scripts.beneficiary import archive_dms_applications

from tests.scripts.beneficiary.fixture import make_graphql_application


@pytest.mark.usefixtures("db_session")
class ArchiveDMSApplicationsTest:

    PROCEDURE_ID = 123

    @patch.object(DMSGraphQLClient, "get_applications_with_details")
    @patch.object(DMSGraphQLClient, "archive_application")
    def test_archive_applications(self, dms_archive, dms_applications):
        application_id = 42
        user = users_factories.BeneficiaryGrant18Factory()
        beneficiary_import = users_factories.BeneficiaryImportFactory(
            sourceId=self.PROCEDURE_ID, applicationId=application_id, beneficiary=user
        )
        users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport=beneficiary_import, status=ImportStatus.CREATED
        )
        dms_applications.return_value = [make_graphql_application(application_id, "closed", email=user.email)]

        archive_dms_applications.archive_applications(self.PROCEDURE_ID, dry_run=False)
        assert dms_archive.call_count == 1

    @patch.object(DMSGraphQLClient, "get_applications_with_details")
    @patch.object(DMSGraphQLClient, "archive_application")
    def test_archive_applications_dry_run(self, dms_archive, dms_applications):
        application_id = 42
        user = users_factories.BeneficiaryGrant18Factory()
        beneficiary_import = users_factories.BeneficiaryImportFactory(
            sourceId=self.PROCEDURE_ID, applicationId=application_id, beneficiary=user
        )
        users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport=beneficiary_import, status=ImportStatus.CREATED
        )
        dms_applications.return_value = [make_graphql_application(application_id, "closed", email=user.email)]

        archive_dms_applications.archive_applications(self.PROCEDURE_ID, dry_run=True)

        assert dms_archive.call_count == 0

    @patch.object(DMSGraphQLClient, "get_applications_with_details")
    @patch.object(DMSGraphQLClient, "archive_application")
    def test_archive_applications_only_archive_beneficiary(self, dms_archive, dms_applications, caplog):
        caplog.set_level(logging.INFO)
        application_id = 42
        user_to_archive = users_factories.BeneficiaryGrant18Factory()
        beneficiary_import = users_factories.BeneficiaryImportFactory(
            sourceId=self.PROCEDURE_ID, applicationId=application_id, beneficiary=user_to_archive
        )
        users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport=beneficiary_import, status=ImportStatus.CREATED
        )
        user_to_not_archive = users_factories.UserFactory()
        application_to_archive = make_graphql_application(application_id, "closed", email=user_to_archive.email)
        dms_applications.return_value = [
            make_graphql_application(20, "closed", email=user_to_not_archive.email),
            application_to_archive,
        ]
        archive_dms_applications.archive_applications(self.PROCEDURE_ID, dry_run=False)
        assert dms_archive.call_count == 1
        assert dms_archive.call_args == [(application_to_archive["id"], "SomeRandomId")]

        assert (
            caplog.messages[0]
            == f"Archiving application {application_id} on procedure {self.PROCEDURE_ID} for user_id {user_to_archive.id}"
        )
        assert caplog.messages[1] == "script ran : total applications : 2 to archive applications : 1"
