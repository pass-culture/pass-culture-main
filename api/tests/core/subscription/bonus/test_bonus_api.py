import copy
import datetime
import decimal
from unittest.mock import patch

import pytest
import requests_mock
import sentry_sdk

import pcapi.connectors.api_particulier as api_particulier
import pcapi.core.finance.models as finance_models
import pcapi.core.mails.testing as mails_testing
import pcapi.core.subscription.bonus.api as bonus_api
import pcapi.core.subscription.bonus.constants as bonus_constants
import pcapi.core.subscription.bonus.schemas as bonus_schemas
import pcapi.core.subscription.factories as subscription_factories
import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
import pcapi.notifications.push.testing as push_testing
import pcapi.notifications.push.trigger_events as trigger_events
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils.sentry import before_send

import tests.core.subscription.bonus.bonus_fixtures as bonus_fixtures


@pytest.mark.usefixtures("db_session")
class GetQuotientFamilialTest:
    @patch("pcapi.core.external.attributes.api.update_external_user")
    def test_apply_for_quotient_familial_bonus(self, update_external_user_mock):
        user = _build_user_from_fixture(bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent={
                "custodian": {
                    "last_name": "LEFEBVRE",
                    "first_names": ["ALEIXS", "GRÉÔME", "JEAN-PHILIPPE"],
                    "birth_date": datetime.date(1982, 12, 27),
                    "gender": users_models.GenderEnum.F.value,
                    "birth_country_cog_code": "99243",
                    "birth_city_cog_code": "08480",
                },
                "quotient_familial": None,
            },
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert bonus_fraud_check.source_data() == bonus_schemas.QuotientFamilialBonusCreditContent(
            custodian=bonus_schemas.QuotientFamilialCustodian(
                last_name="LEFEBVRE",
                common_name=None,
                first_names=["ALEIXS", "GRÉÔME", "JEAN-PHILIPPE"],
                birth_date=datetime.date(1982, 12, 27),
                gender=users_models.GenderEnum.F,
                birth_country_cog_code="99243",
                birth_city_cog_code="08480",
            ),
            quotient_familial=bonus_schemas.QuotientFamilialContent(
                provider="CNAF",
                value=bonus_constants.QUOTIENT_FAMILIAL_THRESHOLD,
                year=2023,
                month=6,
                computation_year=2024,
                computation_month=12,
            ),
            children=[
                bonus_schemas.QuotientFamilialChild(
                    last_name="LEFEBVRE",
                    common_name=None,
                    first_names=["LEO"],
                    birth_date=datetime.date(1990, 4, 20),
                    gender=users_models.GenderEnum.M,
                )
            ],
        )
        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]
        # Ensure that a Batch notification is triggered
        assert push_testing.requests == [
            {
                "can_be_asynchronously_retried": True,
                "user_id": user.id,
                "event_name": trigger_events.BatchEvent.HAS_RECEIVED_BONUS.value,
                "event_payload": {"has_received_bonus": True},
            }
        ]
        update_external_user_mock.assert_called_once_with(user)

        assert len(mails_testing.outbox) == 1
        out_mail = mails_testing.outbox[0]
        assert out_mail["template"] == TransactionalEmail.BONUS_GRANTED.value.__dict__

    def test_minimum_quotient_familial_retained(self):
        user = _build_user_from_fixture(bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )
        high_quotient_familial = copy.deepcopy(bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)
        high_quotient_familial["data"]["quotient_familial"]["valeur"] = 9_999_999

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=high_quotient_familial)
            mock.get(
                f"{api_particulier.QUOTIENT_FAMILIAL_ENDPOINT}?mois={user.birth_date.month}",
                json=bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE,
            )

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert (
            bonus_fraud_check.source_data().quotient_familial.value
            == bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE["data"]["quotient_familial"]["valeur"]
        )
        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]
        assert user.recreditAmountToShow == decimal.Decimal("50")

    def test_custodian_not_found(self):
        user = users_factories.BeneficiaryFactory()
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                quotient_familial=None
            ).model_dump(),
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, status_code=404)

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.CUSTODIAN_NOT_FOUND]
        assert bonus_fraud_check.source_data().quotient_familial is None
        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]
        assert len(push_testing.requests) == 2
        push_request1, push_request2 = push_testing.requests
        assert {push_request1["batch_api"], push_request2["batch_api"]} == {"ANDROID", "IOS"}
        assert push_request1["attribute_values"]["u.bonification_status"] == "ko"
        assert push_request2["attribute_values"]["u.bonification_status"] == "ko"

        assert len(mails_testing.outbox) == 1
        out_mail = mails_testing.outbox[0]
        assert out_mail["template"] == TransactionalEmail.BONUS_DECLINED.value.__dict__

    def test_user_not_in_tax_household(self):
        user = users_factories.BeneficiaryFactory()
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                quotient_familial=None
            ).model_dump(),
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD]
        assert bonus_fraud_check.source_data().quotient_familial is not None
        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

        assert len(mails_testing.outbox) == 1
        out_mail = mails_testing.outbox[0]
        assert out_mail["template"] == TransactionalEmail.BONUS_DECLINED.value.__dict__

    def test_user_quotient_familial_too_high(self):
        child_data = bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE["data"]["enfants"][0]
        last_name = child_data["nom_naissance"]
        first_names = child_data["prenoms"]
        birth_date = datetime.date.fromisoformat(child_data["date_naissance"])
        user = users_factories.BeneficiaryFactory(
            lastName=last_name, firstName=first_names, validatedBirthDate=birth_date
        )
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )
        high_quotient_familial = copy.deepcopy(bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)
        high_quotient_familial["data"]["quotient_familial"]["valeur"] = 9_999_999

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=high_quotient_familial)

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH]
        assert bonus_fraud_check.source_data().quotient_familial == bonus_schemas.QuotientFamilialContent(
            provider="CNAF", value=9_999_999, year=2023, month=6, computation_year=2024, computation_month=12
        )
        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

        assert len(mails_testing.outbox) == 1
        out_mail = mails_testing.outbox[0]
        assert out_mail["template"] == TransactionalEmail.BONUS_DECLINED.value.__dict__

    def test_sentry_error_filtered(self):
        captured_events = []

        def mock_transport(event):
            nonlocal captured_events

            captured_events.append(event)

        client = sentry_sdk.Client(
            dsn="http://public@sentry.local/1", before_send=before_send, transport=mock_transport
        )

        user = users_factories.BeneficiaryFactory()
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent={
                "custodian": {
                    "last_name": "LEFEBVRE",
                    "first_names": ["ALEIXS", "GRÉÔME", "JEAN-PHILIPPE"],
                    "birth_date": datetime.date(1982, 12, 27),
                    "gender": users_models.GenderEnum.F.value,
                    "birth_country_cog_code": "99243",
                    "birth_city_cog_code": "08480",
                },
                "quotient_familial": None,
            },
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, status_code=500)

            with sentry_sdk.Hub(client):
                try:
                    bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)
                except api_particulier.ParticulierApiUnavailable as exc:
                    sentry_sdk.capture_exception(exc)

        assert len(captured_events) == 1
        event = captured_events[0]
        stacktrace_frames = event["exception"]["values"][0]["stacktrace"]["frames"]
        assert stacktrace_frames[1]["vars"]["quotient_familial_response"] == "[REDACTED]"
        assert stacktrace_frames[1]["vars"]["source_data"] == "[REDACTED]"

        assert stacktrace_frames[2]["vars"]["all_quotient_familial_responses"] == "[REDACTED]"
        assert stacktrace_frames[2]["vars"]["custodian"] == "[REDACTED]"

        assert stacktrace_frames[3]["vars"]["custodian"] == "[REDACTED]"
        assert stacktrace_frames[3]["vars"]["query_params"] == {
            "anneeDateNaissance": "[REDACTED]",
            "codeCogInseeCommuneNaissance": "[REDACTED]",
            "codeCogInseePaysNaissance": "[REDACTED]",
            "jourDateNaissance": "[REDACTED]",
            "moisDateNaissance": "[REDACTED]",
            "nomNaissance": "[REDACTED]",
            "nomUsage": "[REDACTED]",
            "prenoms[]": "[REDACTED]",
            "recipient": "[REDACTED]",
            "sexeEtatCivil": "[REDACTED]",
        }


def _build_user_from_fixture(quotient_familial_json_response: dict) -> users_models.User:
    child_data = quotient_familial_json_response["data"]["enfants"][0]
    last_name = child_data["nom_naissance"]
    first_names = child_data["prenoms"]
    birth_date = datetime.date.fromisoformat(child_data["date_naissance"])
    return users_factories.BeneficiaryFactory(lastName=last_name, firstName=first_names, validatedBirthDate=birth_date)
