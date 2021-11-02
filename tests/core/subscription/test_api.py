from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

from flask_jwt_extended.utils import create_access_token
from freezegun import freeze_time
import pytest

from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import BeneficiaryImport
from pcapi.models import BeneficiaryImportSources
from pcapi.models import ImportStatus


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize(
    "import_status",
    [
        ImportStatus.DRAFT,
        ImportStatus.ONGOING,
        ImportStatus.REJECTED,
    ],
)
class AttachBenerificaryImportDetailsTest:
    def test_user_application(self, import_status):
        user = users_factories.UserFactory()
        subscription_api.attach_beneficiary_import_details(
            user, 42, 21, BeneficiaryImportSources.demarches_simplifiees, "random_details", import_status
        )

        beneficiary_import = BeneficiaryImport.query.one()
        assert beneficiary_import.source == BeneficiaryImportSources.demarches_simplifiees.value
        assert beneficiary_import.beneficiary == user
        assert len(beneficiary_import.statuses) == 1

        status = beneficiary_import.statuses[0]
        assert status.detail == "random_details"
        assert status.status == import_status
        assert status.author == None

    def test_user_already_have_jouve_applications(self, import_status):
        user = users_factories.UserFactory()
        users_factories.BeneficiaryImportFactory(beneficiary=user, source=BeneficiaryImportSources.jouve.value)

        subscription_api.attach_beneficiary_import_details(
            user, 42, 21, BeneficiaryImportSources.demarches_simplifiees, "random_details", import_status
        )

        beneficiary_import = BeneficiaryImport.query.all()
        assert len(beneficiary_import) == 2

    def test_user_application_already_have_dms_statuses(self, import_status):
        user = users_factories.UserFactory()
        application_id = 42
        procedure_id = 21
        beneficiary_import = users_factories.BeneficiaryImportFactory(
            beneficiary=user,
            source=BeneficiaryImportSources.demarches_simplifiees.value,
            applicationId=application_id,
            sourceId=procedure_id,
        )
        users_factories.BeneficiaryImportStatusFactory(beneficiaryImport=beneficiary_import)

        subscription_api.attach_beneficiary_import_details(
            user,
            application_id,
            procedure_id,
            BeneficiaryImportSources.demarches_simplifiees,
            "random details",
            import_status,
        )
        beneficiary_import = BeneficiaryImport.query.one()
        assert len(beneficiary_import.statuses) == 2

    def test_user_application_already_have_another_dms_application(self, import_status):
        user = users_factories.UserFactory()
        application_id = 42
        procedure_id = 21
        beneficiary_import = users_factories.BeneficiaryImportFactory(
            beneficiary=user,
            source=BeneficiaryImportSources.demarches_simplifiees.value,
            applicationId=143,
            sourceId=procedure_id,
        )
        users_factories.BeneficiaryImportStatusFactory(beneficiaryImport=beneficiary_import)

        subscription_api.attach_beneficiary_import_details(
            user,
            application_id,
            procedure_id,
            BeneficiaryImportSources.demarches_simplifiees,
            "random details",
            import_status,
        )
        assert BeneficiaryImport.query.count() == 2


@pytest.mark.usefixtures("db_session")
class EduconnectFlowTest:
    @freeze_time("2021-10-10")
    @patch("pcapi.core.users.external.educonnect.api.get_saml_client")
    def test_educonnect_subscription(self, mock_get_educonnect_saml_client, client, app):
        user = users_factories.UserFactory()
        access_token = create_access_token(identity=user.email)
        client.auth_header = {"Authorization": f"Bearer {access_token}"}
        mock_saml_client = MagicMock()
        mock_get_educonnect_saml_client.return_value = mock_saml_client
        mock_saml_client.prepare_for_authenticate.return_value = (
            "request_id_123",
            {"headers": [("Location", "https://pr4.educonnect.phm.education.gouv.fr/idp")]},
        )

        # Get educonnect login form with saml protocol
        response = client.get("/saml/educonnect/login")
        assert response.status_code == 302
        assert response.location.startswith("https://pr4.educonnect.phm.education.gouv.fr/idp")

        prefixed_request_id = app.redis_client.keys("educonnect-saml-request-*")[0]
        request_id = prefixed_request_id[len("educonnect-saml-request-") :]

        mock_saml_response = MagicMock()
        mock_saml_client.parse_authn_request_response.return_value = mock_saml_response
        mock_saml_response.get_identity.return_value = {
            "givenName": ["Max"],
            "sn": ["SENS"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.57": [
                "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875"
            ],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.5": ["https://educonnect.education.gouv.fr/Logout"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.67": ["2006-08-18"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.73": ["2212"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.6": ["2021-10-08 11:51:33.437"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.64": ["5ba682c0fc6a05edf07cd8ed0219258f"],
        }
        mock_saml_response.in_response_to = request_id

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert (
            response.location
            == "https://webapp-v2.example.com/idcheck/validation?firstName=Max&lastName=SENS&dateOfBirth=2006-08-18&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )

        assert user.beneficiaryFraudResult.status == fraud_models.FraudStatus.OK

        beneficiary_import = BeneficiaryImport.query.filter_by(beneficiaryId=user.id).one_or_none()
        assert beneficiary_import is not None
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert user.firstName == "Max"
        assert user.lastName == "SENS"
        assert user.dateOfBirth == datetime(2006, 8, 18, 0, 0)
        assert user.ineHash == "5ba682c0fc6a05edf07cd8ed0219258f"

        profile_data = {
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activity": "Lycéen",
        }

        response = client.patch("/native/v1/beneficiary_information", profile_data)

        assert response.status_code == 204
        assert user.roles == [users_models.UserRole.UNDERAGE_BENEFICIARY]
        assert user.deposit.amount == 20
