import copy
import datetime
import decimal
import logging
from unittest.mock import call
from unittest.mock import patch

import pytest
import requests_mock
import sentry_sdk
from dateutil.relativedelta import relativedelta

import pcapi.connectors.api_particulier as api_particulier
import pcapi.core.external.batch.testing as push_testing
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.mails.testing as mails_testing
import pcapi.core.subscription.bonus.api as bonus_api
import pcapi.core.subscription.bonus.schemas as bonus_schemas
import pcapi.core.subscription.factories as subscription_factories
import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.core.external.batch import models as batch_models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.utils.sentry import before_send

import tests.core.subscription.bonus.bonus_fixtures as bonus_fixtures


@pytest.mark.usefixtures("db_session")
class QuotientFamilialApplicationTest:
    @patch("pcapi.core.external.attributes.api.update_external_user")
    def test_apply_for_quotient_familial_bonus(self, update_external_user_mock, caplog):
        eighteen_years_ago = datetime.date.today() - relativedelta(years=18)
        with_18_child_quotient_familial = copy.deepcopy(bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)
        with_18_child_quotient_familial["data"]["enfants"][0]["date_naissance"] = eighteen_years_ago.isoformat()
        user = _build_user_from_fixture(with_18_child_quotient_familial)
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent={
                "custodian": {
                    "last_name": "LEFEBVRE",
                    "first_names": ["ALEIXS", "GRÉÔME", "JEAN-PHILIPPE"],
                    "birth_date": datetime.date(1982, 12, 27),
                    "gender": users_models.GenderEnum.M.value,
                    "birth_country_cog_code": "99243",
                    "birth_city_cog_code": "08480",
                },
                "quotient_familial": None,
            },
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=with_18_child_quotient_familial)

            with caplog.at_level(logging.INFO):
                bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        bonus_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
        ]
        assert not bonus_fraud_checks

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]
        # Ensure that a Batch notification is triggered
        assert push_testing.requests == [
            {
                "can_be_asynchronously_retried": True,
                "user_id": user.id,
                "event_name": batch_models.BatchEvent.HAS_RECEIVED_BONUS.value,
                "event_payload": {"has_received_bonus": True},
            }
        ]
        update_external_user_mock.assert_called_once_with(user)

        assert len(mails_testing.outbox) == 1
        out_mail = mails_testing.outbox[0]
        assert out_mail["template"] == TransactionalEmail.BONUS_GRANTED.value.__dict__

        for log_record in caplog.records:
            assert not log_record.extra.get("url")

    @patch("pcapi.core.external.attributes.api.update_external_user")
    def test_apply_for_quotient_familial_bonus_as_householder(self, update_external_user_mock):
        eighteen_years_ago = datetime.date.today() - relativedelta(years=18)
        without_child_quotient_familial = copy.deepcopy(bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)
        without_child_quotient_familial["data"]["enfants"] = []
        without_child_quotient_familial["data"]["allocataires"][0]["date_naissance"] = eighteen_years_ago.isoformat()
        householder_data = without_child_quotient_familial["data"]["allocataires"][0]
        last_name = householder_data["nom_naissance"]
        first_names = householder_data["prenoms"]
        birth_date = datetime.date.fromisoformat(householder_data["date_naissance"])
        user = users_factories.BeneficiaryFactory(
            lastName=last_name, firstName=first_names, validatedBirthDate=birth_date
        )
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent={
                "custodian": {
                    "last_name": householder_data["nom_naissance"],
                    "first_names": householder_data["prenoms"].split(),
                    "birth_date": householder_data["date_naissance"],
                    "gender": users_models.GenderEnum.M.value,
                    "birth_country_cog_code": "99243",
                    "birth_city_cog_code": "08480",
                },
                "quotient_familial": None,
            },
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=without_child_quotient_familial)

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        bonus_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
        ]
        assert not bonus_fraud_checks

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]
        # Ensure that a Batch notification is triggered
        assert push_testing.requests == [
            {
                "can_be_asynchronously_retried": True,
                "user_id": user.id,
                "event_name": batch_models.BatchEvent.HAS_RECEIVED_BONUS.value,
                "event_payload": {"has_received_bonus": True},
            }
        ]
        update_external_user_mock.assert_called_once_with(user)

        assert len(mails_testing.outbox) == 1
        out_mail = mails_testing.outbox[0]
        assert out_mail["template"] == TransactionalEmail.BONUS_GRANTED.value.__dict__

    def test_minimum_quotient_familial_retained(self):
        eighteen_years_ago = datetime.date.today() - relativedelta(years=18)
        with_18_child_quotient_familial = copy.deepcopy(bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)
        with_18_child_quotient_familial["data"]["enfants"][0]["date_naissance"] = eighteen_years_ago.isoformat()
        user = _build_user_from_fixture(with_18_child_quotient_familial)
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )
        high_quotient_familial = copy.deepcopy(with_18_child_quotient_familial)
        high_quotient_familial["data"]["quotient_familial"]["valeur"] = 9_999_999

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=high_quotient_familial)
            mock.get(
                f"{api_particulier.QUOTIENT_FAMILIAL_ENDPOINT}?mois={user.birth_date.month}",
                json=with_18_child_quotient_familial,
            )

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        bonus_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
        ]
        assert not bonus_fraud_checks

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]
        assert user.recreditAmountToShow == decimal.Decimal("50")

    @patch("pcapi.connectors.api_particulier.get_quotient_familial")
    def test_get_quotient_familial_calls(self, mocked_get_quotient_familial):
        custodian = subscription_factories.BonusCreditPersonFactory()
        fraud_check = subscription_factories.QFBonusCreditFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory.build(
                custodian=custodian
            ).model_dump(),
        )
        birth_date = fraud_check.user.validatedBirthDate
        mocked_get_quotient_familial.return_value = bonus_fixtures.QF_DESERIALIZED_RESPONSE

        bonus_api.apply_for_quotient_familial_bonus(fraud_check)

        assert len(mocked_get_quotient_familial.mock_calls) == 12
        mocked_get_quotient_familial.assert_has_calls(
            [
                call(custodian, birth_date + relativedelta(years=17) + relativedelta(months=offset))
                for offset in range(12)
            ],
            any_order=True,
        )

    def test_application_not_found(self, caplog):
        user = users_factories.BeneficiaryFactory()
        custodian = subscription_factories.BonusCreditPersonFactory()
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                custodian=custodian, quotient_familial=None
            ).model_dump(),
        )

        with requests_mock.Mocker() as mock:
            mock.get(
                api_particulier.QUOTIENT_FAMILIAL_ENDPOINT,
                status_code=404,
                json=bonus_fixtures.APPLICATION_NOT_FOUND_FIXTURE,
            )

            with caplog.at_level(logging.INFO):
                bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.APPLICATION_NOT_FOUND]
        assert bonus_fraud_check.source_data() == bonus_schemas.QuotientFamilialBonusCreditContent(
            custodian=custodian,
            quotient_familial=None,
            householders=None,
            children=None,
            http_status_code=404,
            error_code="37003",
        )
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

        for log_record in caplog.records:
            assert not log_record.extra.get("url")

    def test_person_not_found(self, caplog):
        user = users_factories.BeneficiaryFactory()
        custodian = subscription_factories.BonusCreditPersonFactory()
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                custodian=custodian, quotient_familial=None
            ).model_dump(),
        )

        with requests_mock.Mocker() as mock:
            mock.get(
                api_particulier.QUOTIENT_FAMILIAL_ENDPOINT,
                status_code=422,
                json=bonus_fixtures.PERSON_NOT_FOUND_FIXTURE,
            )

            with caplog.at_level(logging.INFO):
                bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.PERSON_NOT_FOUND]
        assert bonus_fraud_check.source_data() == bonus_schemas.QuotientFamilialBonusCreditContent(
            custodian=custodian,
            quotient_familial=None,
            householders=None,
            children=None,
            http_status_code=422,
            error_code="00355",
        )
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

        for log_record in caplog.records:
            assert not log_record.extra.get("url")

    def test_user_not_in_tax_household(self):
        user = users_factories.BeneficiaryFactory()
        custodian = subscription_factories.BonusCreditPersonFactory()
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                custodian=custodian, quotient_familial=None
            ).model_dump(),
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD]
        assert bonus_fraud_check.source_data().quotient_familial is not None

        householder_data = bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE["data"]["allocataires"][0]
        assert bonus_fraud_check.source_data() == bonus_schemas.QuotientFamilialBonusCreditContent(
            custodian=custodian,
            quotient_familial=bonus_schemas.QuotientFamilialContent(
                provider="CNAF",
                value=700,
                year=2023,
                month=6,
                computation_year=2024,
                computation_month=12,
            ),
            householders=[
                bonus_schemas.BonusCreditPerson(
                    last_name=householder_data["nom_naissance"],
                    common_name=None,
                    first_names=householder_data["prenoms"].split(),
                    birth_date=householder_data["date_naissance"],
                    gender=users_models.GenderEnum.M,
                )
            ],
            children=[
                bonus_schemas.BonusCreditPerson(
                    last_name="LEFEBVRE",
                    common_name=None,
                    first_names=["LEO"],
                    birth_date=datetime.date(1990, 4, 20),
                    gender=users_models.GenderEnum.M,
                )
            ],
            http_status_code=200,
        )

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

    def test_user_quotient_familial_too_high(self):
        eighteen_years_ago = datetime.date.today() - relativedelta(years=18)
        high_quotient_familial = copy.deepcopy(bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)
        high_quotient_familial["data"]["enfants"][0]["date_naissance"] = eighteen_years_ago.isoformat()
        high_quotient_familial["data"]["quotient_familial"]["valeur"] = 9_999_999
        user = _build_user_from_fixture(high_quotient_familial)
        custodian = subscription_factories.BonusCreditPersonFactory()
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory(
                custodian=custodian, quotient_familial=None
            ).model_dump(),
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=high_quotient_familial)

            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH]
        assert bonus_fraud_check.source_data().quotient_familial == bonus_schemas.QuotientFamilialContent(
            provider="CNAF", value=9_999_999, year=2023, month=6, computation_year=2024, computation_month=12
        )

        householder_data = high_quotient_familial["data"]["allocataires"][0]
        assert bonus_fraud_check.source_data() == bonus_schemas.QuotientFamilialBonusCreditContent(
            custodian=custodian,
            quotient_familial=bonus_schemas.QuotientFamilialContent(
                provider="CNAF",
                value=9_999_999,
                year=2023,
                month=6,
                computation_year=2024,
                computation_month=12,
            ),
            householders=[
                bonus_schemas.BonusCreditPerson(
                    last_name=householder_data["nom_naissance"],
                    common_name=None,
                    first_names=householder_data["prenoms"].split(),
                    birth_date=householder_data["date_naissance"],
                    gender=users_models.GenderEnum.M,
                )
            ],
            children=[
                bonus_schemas.BonusCreditPerson(
                    last_name="LEFEBVRE",
                    common_name=None,
                    first_names=["LEO"],
                    birth_date=eighteen_years_ago,
                    gender=users_models.GenderEnum.M,
                )
            ],
            http_status_code=200,
        )

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

    def test_bonus_fraud_checks_deletion_when_granted(self):
        eighteen_years_ago = datetime.date.today() - relativedelta(years=18)
        with_18_child_quotient_familial = copy.deepcopy(bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)
        with_18_child_quotient_familial["data"]["enfants"][0]["date_naissance"] = eighteen_years_ago.isoformat()
        user = _build_user_from_fixture(with_18_child_quotient_familial)
        qf_bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.KO,
            resultContent=subscription_factories.AdultDisabilityBonusCreditContentFactory().model_dump(),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.DisabledChildEducationBonusCreditContentFactory().model_dump(),
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, json=with_18_child_quotient_familial)

            bonus_api.apply_for_quotient_familial_bonus(qf_bonus_fraud_check)

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

        bonus_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
        ]
        assert not bonus_fraud_checks

    @pytest.mark.settings(ENABLE_PARTICULIER_API_MOCK=0)
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
            mock.get(api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, status_code=500, json={})

            with sentry_sdk.Hub(client):
                try:
                    bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)
                except api_particulier.ParticulierApiUnavailable as exc:
                    sentry_sdk.capture_exception(exc)

        assert len(captured_events) == 1
        event = captured_events[-1]
        stacktrace_frames = event["exception"]["values"][0]["stacktrace"]["frames"]

        test_frame = stacktrace_frames[0]
        assert any(value not in [None, "[REDACTED]"] for value in test_frame["vars"].values())

        for frame in stacktrace_frames[1:]:
            assert all(value == "[REDACTED]" for value in frame["vars"].values())

    def test_touch_fraud_check_despite_error(self):
        twelve_hours_ago = datetime.datetime.now(tz=None) - relativedelta(hours=12)
        bonus_fraud_check = subscription_factories.QFBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, updatedAt=twelve_hours_ago
        )

        with requests_mock.Mocker() as mock:
            mock.get(
                api_particulier.QUOTIENT_FAMILIAL_ENDPOINT, status_code=502, json=bonus_fixtures.DATA_PROVIDER_ERROR
            )

            with pytest.raises(api_particulier.ParticulierApiException):
                bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

        assert bonus_fraud_check.updatedAt > twelve_hours_ago

    @patch("pcapi.core.finance.deposit_api.recredit_bonus_credit")
    def test_has_already_received_bonus_credit(self, mock_recredit):
        eighteen_years_ago = datetime.date.today() - relativedelta(years=18)
        with_18_child_quotient_familial = copy.deepcopy(bonus_fixtures.QUOTIENT_FAMILIAL_FIXTURE)
        with_18_child_quotient_familial["data"]["enfants"][0]["date_naissance"] = eighteen_years_ago.isoformat()
        user = _build_user_from_fixture(with_18_child_quotient_familial)
        finance_factories.RecreditFactory(deposit=user.deposit, recreditType=finance_models.RecreditType.BONUS_CREDIT)
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        with requests_mock.Mocker() as mock:
            bonus_api.apply_for_quotient_familial_bonus(bonus_fraud_check)

            assert mock.call_count == 0

        mock_recredit.assert_not_called()
        assert len(push_testing.requests) == 0
        assert len(mails_testing.outbox) == 0


def _build_user_from_fixture(quotient_familial_json_response: dict) -> users_models.User:
    child_data = quotient_familial_json_response["data"]["enfants"][0]
    last_name = child_data["nom_naissance"]
    first_names = child_data["prenoms"]
    birth_date = datetime.date.fromisoformat(child_data["date_naissance"])
    return users_factories.BeneficiaryFactory(lastName=last_name, firstName=first_names, validatedBirthDate=birth_date)


@pytest.mark.usefixtures("db_session")
class DisabledAdultAllowanceTest:
    @patch("pcapi.core.external.attributes.api.update_external_user")
    def test_apply_for_disabled_adult_allowance_bonus(self, update_external_user_mock, caplog):
        user = users_factories.BeneficiaryFactory()
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AAH_ENDPOINT, json=bonus_fixtures.AAH_ELIGIBLE_RESPONSE)

            with caplog.at_level(logging.INFO):
                bonus_api.apply_for_adult_disability_bonus(bonus_fraud_check)

        bonus_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
        ]
        assert not bonus_fraud_checks

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]
        # Ensure that a Batch notification is triggered
        assert push_testing.requests == [
            {
                "can_be_asynchronously_retried": True,
                "user_id": user.id,
                "event_name": batch_models.BatchEvent.HAS_RECEIVED_BONUS.value,
                "event_payload": {"has_received_bonus": True},
            }
        ]
        update_external_user_mock.assert_called_once_with(user)

        assert len(mails_testing.outbox) == 1

        for log_record in caplog.records:
            assert not log_record.extra.get("url")

    def test_not_eligible_for_disabled_adult_allowance_bonus(self):
        user = users_factories.BeneficiaryFactory()
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AAH_ENDPOINT, json=bonus_fixtures.AAH_INELIGIBLE_RESPONSE)

            bonus_api.apply_for_adult_disability_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.NOT_ELIGIBLE]
        assert bonus_fraud_check.source_data().http_status_code == 200
        assert bonus_fraud_check.source_data().error_code is None

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

        assert len(push_testing.requests) == 2
        push_request1, push_request2 = push_testing.requests
        assert {push_request1["batch_api"], push_request2["batch_api"]} == {"ANDROID", "IOS"}
        assert push_request1["attribute_values"]["u.bonification_status"] == "eligible"
        assert push_request2["attribute_values"]["u.bonification_status"] == "eligible"

        assert len(mails_testing.outbox) == 0

    def test_person_not_found(self):
        user = users_factories.BeneficiaryFactory()
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AAH_ENDPOINT, status_code=422, json=bonus_fixtures.PERSON_NOT_FOUND_FIXTURE)

            bonus_api.apply_for_adult_disability_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.PERSON_NOT_FOUND]
        assert bonus_fraud_check.source_data().http_status_code == 422
        assert bonus_fraud_check.source_data().error_code == "00355"

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

        assert len(push_testing.requests) == 2
        push_request1, push_request2 = push_testing.requests
        assert {push_request1["batch_api"], push_request2["batch_api"]} == {"ANDROID", "IOS"}
        assert push_request1["attribute_values"]["u.bonification_status"] == "eligible"
        assert push_request2["attribute_values"]["u.bonification_status"] == "eligible"

        assert len(mails_testing.outbox) == 0

    def test_application_not_found(self, caplog):
        user = users_factories.BeneficiaryFactory()
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AAH_ENDPOINT, status_code=404, json=bonus_fixtures.APPLICATION_NOT_FOUND_FIXTURE)

            with caplog.at_level(logging.INFO):
                bonus_api.apply_for_adult_disability_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.APPLICATION_NOT_FOUND]
        assert bonus_fraud_check.resultContent["http_status_code"] == 404
        assert bonus_fraud_check.resultContent["error_code"] == "37003"

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

        assert len(push_testing.requests) == 2
        push_request1, push_request2 = push_testing.requests
        assert {push_request1["batch_api"], push_request2["batch_api"]} == {"ANDROID", "IOS"}
        assert push_request1["attribute_values"]["u.bonification_status"] == "eligible"
        assert push_request2["attribute_values"]["u.bonification_status"] == "eligible"

        assert len(mails_testing.outbox) == 0

        for log_record in caplog.records:
            assert not log_record.extra.get("url")

    def test_bonus_fraud_checks_deletion_when_granted(self):
        user = users_factories.BeneficiaryFactory()
        aah_bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.KO,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.DisabledChildEducationBonusCreditContentFactory().model_dump(),
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AAH_ENDPOINT, json=bonus_fixtures.AAH_ELIGIBLE_RESPONSE)

            bonus_api.apply_for_adult_disability_bonus(aah_bonus_fraud_check)

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

        bonus_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
        ]
        assert not bonus_fraud_checks

    @pytest.mark.settings(ENABLE_PARTICULIER_API_MOCK=0)
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
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AAH_ENDPOINT, status_code=500, json={})

            with sentry_sdk.Hub(client):
                try:
                    bonus_api.apply_for_adult_disability_bonus(bonus_fraud_check)
                except api_particulier.ParticulierApiUnavailable as exc:
                    sentry_sdk.capture_exception(exc)

        assert len(captured_events) == 1
        event = captured_events[-1]
        stacktrace_frames = event["exception"]["values"][0]["stacktrace"]["frames"]

        test_frame = stacktrace_frames[0]
        assert any(value not in [None, "[REDACTED]"] for value in test_frame["vars"].values())

        for frame in stacktrace_frames[1:]:
            assert all(value == "[REDACTED]" for value in frame["vars"].values())

    def test_touch_fraud_check_despite_error(self):
        twelve_hours_ago = datetime.datetime.now(tz=None) - relativedelta(hours=12)
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            updatedAt=twelve_hours_ago,
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AAH_ENDPOINT, status_code=502, json=bonus_fixtures.DATA_PROVIDER_ERROR)

            with pytest.raises(api_particulier.ParticulierApiException):
                bonus_api.apply_for_adult_disability_bonus(bonus_fraud_check)

        assert bonus_fraud_check.updatedAt > twelve_hours_ago

    @patch("pcapi.core.finance.deposit_api.recredit_bonus_credit")
    def test_has_already_received_bonus_credit(self, mock_recredit):
        user = users_factories.BeneficiaryFactory()
        finance_factories.RecreditFactory(deposit=user.deposit, recreditType=finance_models.RecreditType.BONUS_CREDIT)
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        with requests_mock.Mocker() as mock:
            bonus_api.apply_for_adult_disability_bonus(bonus_fraud_check)

            assert mock.call_count == 0

        mock_recredit.assert_not_called()
        assert len(push_testing.requests) == 0
        assert len(mails_testing.outbox) == 0


@pytest.mark.usefixtures("db_session")
class DisabledChildEducationAllowanceTest:
    @pytest.mark.parametrize(
        "aeeh_response",
        [bonus_fixtures.AEEH_ELIGIBLE_RESPONSE, bonus_fixtures.AEEH_OPENING_RIGHTS_RESPONSE],
    )
    @patch("pcapi.core.external.attributes.api.update_external_user")
    def test_apply_for_disabled_child_education_allowance_bonus(self, update_external_user_mock, aeeh_response, caplog):
        user = users_factories.BeneficiaryFactory()

        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AEEH_ENDPOINT, json=aeeh_response)

            with caplog.at_level(logging.INFO):
                bonus_api.apply_for_disabled_child_education_bonus(bonus_fraud_check)

        bonus_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
        ]
        assert not bonus_fraud_checks

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]
        # Ensure that a Batch notification is triggered
        assert push_testing.requests == [
            {
                "can_be_asynchronously_retried": True,
                "user_id": user.id,
                "event_name": batch_models.BatchEvent.HAS_RECEIVED_BONUS.value,
                "event_payload": {"has_received_bonus": True},
            }
        ]
        update_external_user_mock.assert_called_once_with(user)

        assert len(mails_testing.outbox) == 1

        for log_record in caplog.records:
            assert not log_record.extra.get("url")

    def test_not_eligible_for_disabled_child_education_allowance_bonus(self):
        user = users_factories.BeneficiaryFactory()

        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AEEH_ENDPOINT, json=bonus_fixtures.AEEH_INELIGIBLE_RESPONSE)

            bonus_api.apply_for_disabled_child_education_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.NOT_ELIGIBLE]
        assert bonus_fraud_check.source_data().http_status_code == 200
        assert bonus_fraud_check.source_data().error_code is None

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

        assert len(push_testing.requests) == 2
        push_request1, push_request2 = push_testing.requests
        assert {push_request1["batch_api"], push_request2["batch_api"]} == {"ANDROID", "IOS"}
        assert push_request1["attribute_values"]["u.bonification_status"] == "eligible"
        assert push_request2["attribute_values"]["u.bonification_status"] == "eligible"

        assert len(mails_testing.outbox) == 0

    def test_person_not_found(self, caplog):
        user = users_factories.BeneficiaryFactory()

        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AEEH_ENDPOINT, status_code=422, json=bonus_fixtures.PERSON_NOT_FOUND_FIXTURE)

            with caplog.at_level(logging.INFO):
                bonus_api.apply_for_disabled_child_education_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.PERSON_NOT_FOUND]
        assert bonus_fraud_check.source_data().http_status_code == 422
        assert bonus_fraud_check.source_data().error_code == "00355"

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

        assert len(push_testing.requests) == 2
        push_request1, push_request2 = push_testing.requests
        assert {push_request1["batch_api"], push_request2["batch_api"]} == {"ANDROID", "IOS"}
        assert push_request1["attribute_values"]["u.bonification_status"] == "eligible"
        assert push_request2["attribute_values"]["u.bonification_status"] == "eligible"

        assert len(mails_testing.outbox) == 0

        for log_record in caplog.records:
            assert not log_record.extra.get("url")

    def test_application_not_found(self, caplog):
        user = users_factories.BeneficiaryFactory()

        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AEEH_ENDPOINT, status_code=404, json=bonus_fixtures.APPLICATION_NOT_FOUND_FIXTURE)

            with caplog.at_level(logging.INFO):
                bonus_api.apply_for_disabled_child_education_bonus(bonus_fraud_check)

        assert bonus_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert bonus_fraud_check.reasonCodes == [subscription_models.FraudReasonCode.APPLICATION_NOT_FOUND]
        assert bonus_fraud_check.resultContent["http_status_code"] == 404
        assert bonus_fraud_check.resultContent["error_code"] == "37003"

        assert finance_models.RecreditType.BONUS_CREDIT not in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

        assert len(push_testing.requests) == 2
        push_request1, push_request2 = push_testing.requests
        assert {push_request1["batch_api"], push_request2["batch_api"]} == {"ANDROID", "IOS"}
        assert push_request1["attribute_values"]["u.bonification_status"] == "eligible"
        assert push_request2["attribute_values"]["u.bonification_status"] == "eligible"

        assert len(mails_testing.outbox) == 0

        for log_record in caplog.records:
            assert not log_record.extra.get("url")

    def test_bonus_fraud_checks_deletion_when_granted(self):
        user = users_factories.BeneficiaryFactory()
        aeeh_bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.DisabledChildEducationBonusCreditContentFactory().model_dump(),
        )
        subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.KO,
            resultContent=subscription_factories.QuotientFamilialBonusCreditContentFactory().model_dump(),
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AEEH_ENDPOINT, json=bonus_fixtures.AEEH_ELIGIBLE_RESPONSE)

            bonus_api.apply_for_disabled_child_education_bonus(aeeh_bonus_fraud_check)

        assert finance_models.RecreditType.BONUS_CREDIT in [
            recredit.recreditType for recredit in user.deposit.recredits
        ]

        bonus_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
        ]
        assert not bonus_fraud_checks

    @pytest.mark.settings(ENABLE_PARTICULIER_API_MOCK=0)
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
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AEEH_ENDPOINT, status_code=500, json={})

            with sentry_sdk.Hub(client):
                try:
                    bonus_api.apply_for_disabled_child_education_bonus(bonus_fraud_check)
                except api_particulier.ParticulierApiUnavailable as exc:
                    sentry_sdk.capture_exception(exc)

        assert len(captured_events) == 1
        event = captured_events[-1]
        stacktrace_frames = event["exception"]["values"][0]["stacktrace"]["frames"]

        test_frame = stacktrace_frames[0]
        assert any(value not in [None, "[REDACTED]"] for value in test_frame["vars"].values())

        for frame in stacktrace_frames[1:]:
            assert all(value == "[REDACTED]" for value in frame["vars"].values())

    def test_touch_fraud_check_despite_error(self):
        twelve_hours_ago = datetime.datetime.now(tz=None) - relativedelta(hours=12)
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
            updatedAt=twelve_hours_ago,
        )

        with requests_mock.Mocker() as mock:
            mock.get(api_particulier.AEEH_ENDPOINT, status_code=502, json=bonus_fixtures.DATA_PROVIDER_ERROR)

            with pytest.raises(api_particulier.ParticulierApiException):
                bonus_api.apply_for_disabled_child_education_bonus(bonus_fraud_check)

        assert bonus_fraud_check.updatedAt > twelve_hours_ago

    @patch("pcapi.core.finance.deposit_api.recredit_bonus_credit")
    def test_has_already_received_bonus_credit(self, mock_recredit):
        user = users_factories.BeneficiaryFactory()
        finance_factories.RecreditFactory(deposit=user.deposit, recreditType=finance_models.RecreditType.BONUS_CREDIT)
        bonus_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory.create(
            user=user,
            type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        with requests_mock.Mocker() as mock:
            bonus_api.apply_for_adult_disability_bonus(bonus_fraud_check)

            assert mock.call_count == 0

        mock_recredit.assert_not_called()
        assert len(push_testing.requests) == 0
        assert len(mails_testing.outbox) == 0
