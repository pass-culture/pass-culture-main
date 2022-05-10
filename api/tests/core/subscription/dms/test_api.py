import datetime
from unittest.mock import patch

import freezegun
import pytest

from pcapi.connectors.dms import api as api_dms
from pcapi.connectors.dms import models as dms_models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models

from tests.scripts.beneficiary.fixture import make_parsed_graphql_application
from tests.scripts.beneficiary.fixture import make_single_application


@pytest.mark.usefixtures("db_session")
@freezegun.freeze_time("2022-11-02")
class DMSSubscriptionItemStatusTest:
    def test_not_eligible(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2002, month=1, day=1))

        status = dms_subscription_api.get_dms_subscription_item_status(user, users_models.EligibilityType.UNDERAGE, [])

        assert status == subscription_models.SubscriptionItemStatus.VOID

    def test_eligible(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2004, month=1, day=1))

        status = dms_subscription_api.get_dms_subscription_item_status(user, users_models.EligibilityType.AGE18, [])

        assert status == subscription_models.SubscriptionItemStatus.TODO

    def test_ko_and_ok(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2002, month=1, day=1))

        ok_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.OK
        )
        ko_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.KO
        )

        status = dms_subscription_api.get_dms_subscription_item_status(
            user, users_models.EligibilityType.UNDERAGE, [ok_check, ko_check]
        )

        assert status == subscription_models.SubscriptionItemStatus.OK

    def test_ko(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2006, month=1, day=1))

        ko_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.KO
        )
        suspicious_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.SUSPICIOUS
        )

        status = dms_subscription_api.get_dms_subscription_item_status(
            user, users_models.EligibilityType.UNDERAGE, [ko_check, suspicious_check]
        )

        assert status == subscription_models.SubscriptionItemStatus.KO

    def test_started(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2006, month=1, day=1))

        pending_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.STARTED
        )

        status = dms_subscription_api.get_dms_subscription_item_status(
            user, users_models.EligibilityType.UNDERAGE, [pending_check]
        )

        assert status == subscription_models.SubscriptionItemStatus.PENDING


@pytest.mark.usefixtures("db_session")
@freezegun.freeze_time("2022-11-02")
class DMSOrphanSubsriptionTest:
    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_orphan_corresponding_user(self, execute_query):
        application_id = 1234
        procedure_id = 4321
        email = "dms_orphan@example.com"

        user = users_factories.UserFactory(email=email)
        fraud_factories.OrphanDmsApplicationFactory(email=email, application_id=application_id, process_id=procedure_id)

        execute_query.return_value = make_single_application(
            application_id, dms_models.GraphQLApplicationStates.draft, email=email
        )

        dms_subscription_api.try_dms_orphan_adoption(user)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).first()
        assert fraud_check is not None

        dms_orphan = fraud_models.OrphanDmsApplication.query.filter_by(email=user.email).first()
        assert dms_orphan is None

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_orphan_corresponding_user_with_parsing_error(self, execute_query):
        application_id = 1234
        procedure_id = 4321
        email = "dms_orphan@example.com"

        user = users_factories.UserFactory(email=email)
        fraud_factories.OrphanDmsApplicationFactory(email=email, application_id=application_id, process_id=procedure_id)

        execute_query.return_value = make_single_application(
            application_id, dms_models.GraphQLApplicationStates.draft, email=email, postal_code="1234"
        )

        dms_subscription_api.try_dms_orphan_adoption(user)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).first()
        assert fraud_check is not None

        dms_orphan = fraud_models.OrphanDmsApplication.query.filter_by(email=user.email).first()
        assert dms_orphan is None


@pytest.mark.usefixtures("db_session")
class HandleDmsApplicationTest:
    @patch("pcapi.connectors.dms.api.parse_beneficiary_information_graphql")
    def test_parsing_failure(
        self,
        mocked_parse_beneficiary_information,
    ):
        user = users_factories.UserFactory()
        dms_response = make_parsed_graphql_application(
            application_id=1, state=dms_models.GraphQLApplicationStates.draft, email=user.email
        )
        mocked_parse_beneficiary_information.side_effect = [Exception()]

        with pytest.raises(Exception):
            dms_subscription_api.handle_dms_application(dms_response, 123)

        assert fraud_models.BeneficiaryFraudCheck.query.first() is None
