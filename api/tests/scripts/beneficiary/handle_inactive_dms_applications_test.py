import datetime
from unittest.mock import patch

import freezegun
import pytest

from pcapi.connectors.dms import api as api_dms
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.testing import override_settings
from pcapi.scripts.subscription.dms.handle_inactive_dms_applications import _has_inactivity_delay_expired
from pcapi.scripts.subscription.dms.handle_inactive_dms_applications import _is_never_eligible_applicant
from pcapi.scripts.subscription.dms.handle_inactive_dms_applications import handle_inactive_dms_applications

from tests.scripts.beneficiary.fixture import make_parsed_graphql_application


@pytest.mark.usefixtures("db_session")
class HandleInactiveApplicationTest:
    @patch.object(api_dms.DMSGraphQLClient, "mark_without_continuation")
    @patch.object(api_dms.DMSGraphQLClient, "make_on_going")
    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    @freezegun.freeze_time("2022-04-27")
    @override_settings(DMS_ENROLLMENT_INSTRUCTOR="SomeInstructorId")
    def test_mark_without_continuation(self, dms_applications_mock, make_on_going_mock, mark_without_continuation_mock):
        active_application = make_parsed_graphql_application(
            application_number=1, state="en_construction", last_modification_date="2022-04-01T00:00:00+02:00"
        )
        inactive_application = make_parsed_graphql_application(
            application_number=2, state="en_construction", last_modification_date="2021-11-11T00:00:00+02:00"
        )
        active_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.DMS,
            thirdPartyId=str(active_application.number),
            status=fraud_models.FraudCheckStatus.STARTED,
            resultContent=fraud_factories.DMSContentFactory(email=active_application.profile.email),
        )
        inactive_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.DMS,
            thirdPartyId=str(inactive_application.number),
            status=fraud_models.FraudCheckStatus.STARTED,
            resultContent=fraud_factories.DMSContentFactory(email=inactive_application.profile.email),
        )

        dms_applications_mock.return_value = [active_application, inactive_application]

        handle_inactive_dms_applications(1)

        make_on_going_mock.assert_called_once_with(
            inactive_application.id, "SomeInstructorId", disable_notification=True
        )
        mark_without_continuation_mock.assert_called_once_with(
            inactive_application.id,
            "SomeInstructorId",
            motivation="Aucune activité n'a eu lieu sur votre dossier depuis plus de 90 jours. Si vous souhaitez le soumettre à nouveau, vous pouvez contacter le support à l'adresse support@example.com",
        )
        assert active_fraud_check.status == fraud_models.FraudCheckStatus.STARTED
        assert inactive_fraud_check.status == fraud_models.FraudCheckStatus.CANCELED

    @patch.object(api_dms.DMSGraphQLClient, "mark_without_continuation")
    @patch.object(api_dms.DMSGraphQLClient, "make_on_going")
    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    @freezegun.freeze_time("2022-04-27")
    def test_mark_without_continuation_skip_never_eligible(
        self, dms_applications_mock, make_on_going_mock, mark_without_continuation_mock
    ):
        inactive_application = make_parsed_graphql_application(
            application_number=2,
            state="en_construction",
            last_modification_date="2021-11-11T00:00:00+02:00",
            birth_date=datetime.datetime(2002, 1, 1),
            postal_code="12400",
        )

        inactive_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.DMS,
            thirdPartyId=str(inactive_application.number),
            status=fraud_models.FraudCheckStatus.STARTED,
        )

        dms_applications_mock.return_value = [inactive_application]

        handle_inactive_dms_applications(1, with_never_eligible_applicant_rule=True)

        make_on_going_mock.assert_not_called()
        mark_without_continuation_mock.assert_not_called()

        assert inactive_fraud_check.status == fraud_models.FraudCheckStatus.STARTED

    @patch.object(api_dms.DMSGraphQLClient, "mark_without_continuation")
    @patch.object(api_dms.DMSGraphQLClient, "make_on_going")
    @patch.object(api_dms.DMSGraphQLClient, "get_applications_with_details")
    @freezegun.freeze_time("2022-04-27")
    @override_settings(DMS_ENROLLMENT_INSTRUCTOR="SomeInstructorId")
    def test_duplicated_application_can_be_cancelled(
        self, dms_applications_mock, make_on_going_mock, mark_without_continuation_mock
    ):
        old_email = "lucille.ellingson@example.com"
        new_email = "lucy.ellingson@example.com"
        inactive_application = make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            last_modification_date="2021-11-11T00:00:00+02:00",
            email=new_email,
        )

        active_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.DMS,
            thirdPartyId=str(inactive_application.number),
            status=fraud_models.FraudCheckStatus.STARTED,
            resultContent=fraud_factories.DMSContentFactory(email=old_email),
        )
        inactive_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.DMS,
            thirdPartyId=str(inactive_application.number),
            status=fraud_models.FraudCheckStatus.STARTED,
            resultContent=fraud_factories.DMSContentFactory(email=new_email),
        )

        dms_applications_mock.return_value = [inactive_application]

        # When
        handle_inactive_dms_applications(1)

        # Then
        make_on_going_mock.assert_called_once_with(
            inactive_application.id, "SomeInstructorId", disable_notification=True
        )
        mark_without_continuation_mock.assert_called_once_with(
            inactive_application.id,
            "SomeInstructorId",
            motivation="Aucune activité n'a eu lieu sur votre dossier depuis plus de 90 jours. Si vous souhaitez le soumettre à nouveau, vous pouvez contacter le support à l'adresse support@example.com",
        )
        assert active_fraud_check.status == fraud_models.FraudCheckStatus.STARTED
        assert inactive_fraud_check.status == fraud_models.FraudCheckStatus.CANCELED


@pytest.mark.usefixtures("db_session")
class IsNeverEligibleTest:
    @freezegun.freeze_time("2022-04-27")
    def test_19_yo_at_generalisation_from_not_test_department(self):
        inactive_application = make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            birth_date=datetime.datetime(2002, 1, 1),
            postal_code="12400",
        )
        assert _is_never_eligible_applicant(inactive_application)

    @freezegun.freeze_time("2022-04-27")
    def test_19_yo_at_generalisation_from_test_department(self):
        inactive_application = make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            birth_date=datetime.datetime(2002, 1, 1),
            postal_code="56510",
        )
        assert not _is_never_eligible_applicant(inactive_application)

    @freezegun.freeze_time("2022-04-27")
    def test_still_18_yo_after_generalisation(self):
        inactive_application = make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            birth_date=datetime.datetime(2002, 6, 1),
            postal_code="12400",
        )
        assert not _is_never_eligible_applicant(inactive_application)


class HasInactivityDelayExpiredTest:
    def test_has_inactivity_delay_expired_without_message(self):
        no_message_application = make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            last_modification_date="2022-01-01T00:00:00+02:00",
            messages=[],
        )

        assert _has_inactivity_delay_expired(no_message_application)

    @freezegun.freeze_time("2022-04-27")
    def test_has_inactivity_delay_expired_with_recent_message(self):
        no_message_application = make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            last_modification_date="2022-01-01T00:00:00+02:00",
            messages=[
                {"createdAt": "2022-04-06T00:00:00+02:00", "email": "instrouctor@example.com"},
                {"createdAt": "2020-04-06T00:00:00+02:00", "email": "instrouctor@example.com"},
            ],
        )

        assert not _has_inactivity_delay_expired(no_message_application)

    @freezegun.freeze_time("2022-04-27")
    def test_has_inactivity_delay_expired_with_old_message(self):
        no_message_application = make_parsed_graphql_application(
            application_number=1,
            state="en_construction",
            last_modification_date="2022-01-01T00:00:00+02:00",
            messages=[
                {"createdAt": "2022-01-01T00:00:00+02:00", "email": "instrouctor@example.com"},
                {"createdAt": "2020-04-06T00:00:00+02:00", "email": "instrouctor@example.com"},
            ],
        )

        assert _has_inactivity_delay_expired(no_message_application)

    @freezegun.freeze_time("2022-04-27")
    def test_has_inactivity_delay_expired_with_old_message_sent_by_user(self):
        applicant_email = "applikant@example.com"

        no_message_application = make_parsed_graphql_application(
            application_number=1,
            email=applicant_email,
            state="en_construction",
            last_modification_date="2022-01-01T00:00:00+02:00",
            messages=[
                {"createdAt": "2021-01-01T00:00:00+02:00", "email": applicant_email},
                {"createdAt": "2020-04-06T00:00:00+02:00", "email": "instrouctor@example.com"},
            ],
        )

        assert not _has_inactivity_delay_expired(no_message_application)
