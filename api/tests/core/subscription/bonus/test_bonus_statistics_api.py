import logging

import pytest

import pcapi.core.subscription.models as subscription_models
from pcapi import settings
from pcapi.core.subscription.bonus import statistics_api


@pytest.mark.usefixtures("app")
class BonusAttemptCountersTest:
    def test_records_every_attempt_breakdown(self, caplog):
        statistics_api.record_bonus_attempt(
            bonus_type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            reason_codes=[subscription_models.FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH],
        )
        statistics_api.record_bonus_attempt(
            bonus_type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            reason_codes=[subscription_models.FraudReasonCode.NOT_RECIPIENT],
        )
        for i in range(settings.MIN_QUOTIENT_FAMILIAL_BONUSES_TO_PUBLISH):
            statistics_api.record_bonus_attempt(
                bonus_type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
                reason_codes=[],
                attempts_until_grant=2,
            )

        with caplog.at_level(logging.INFO):
            statistics_api.log_bonus_credit_counters()

        log_record = caplog.records[0]
        assert log_record.technical_message_id == statistics_api.COUNTERS_TECHNICAL_MESSAGE_ID

        log_extra = log_record.extra
        assert log_extra["counters"]["errors"] == {
            "qf_bonus_credit": {"quotient_familial_too_high": 1},
            "aah_bonus_credit": {"not_recipient": 1},
        }
        assert log_extra["counters"]["grants"] == {
            "qf_bonus_credit": settings.MIN_QUOTIENT_FAMILIAL_BONUSES_TO_PUBLISH,
        }

    def test_counts_the_attempts(self, caplog):
        statistics_api.record_bonus_attempt(
            bonus_type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT, reason_codes=[], attempts_until_grant=0
        )
        statistics_api.record_bonus_attempt(
            bonus_type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT, reason_codes=[], attempts_until_grant=29
        )
        for _i in range(2 * settings.MIN_QUOTIENT_FAMILIAL_PER_DISABILITY_BONUS):
            statistics_api.record_bonus_attempt(
                bonus_type=subscription_models.FraudCheckType.QF_BONUS_CREDIT, reason_codes=[], attempts_until_grant=1
            )

        with caplog.at_level(logging.INFO):
            statistics_api.log_bonus_credit_counters()

        log_record = caplog.records[0]
        assert log_record.technical_message_id == statistics_api.COUNTERS_TECHNICAL_MESSAGE_ID

        assert log_record.extra["counters"]["attempts_until_grant"] == {"0": 1, "1": 6, "29": 1}

    def test_published_counters_are_consumed(self, caplog):
        for i in range(settings.MIN_QUOTIENT_FAMILIAL_BONUSES_TO_PUBLISH):
            statistics_api.record_bonus_attempt(
                bonus_type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
                reason_codes=[],
                attempts_until_grant=2,
            )
        statistics_api.record_bonus_attempt(
            bonus_type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
            reason_codes=[subscription_models.FraudReasonCode.NOT_RECIPIENT],
        )

        with caplog.at_level(logging.INFO):
            statistics_api.log_bonus_credit_counters()

        first_log_record = caplog.records[0]
        assert first_log_record.technical_message_id == statistics_api.COUNTERS_TECHNICAL_MESSAGE_ID
        assert first_log_record.extra["counters"] != {}
        assert first_log_record.extra["counters_since"] is None

        # the attempts recorded afterwards are the only ones left to report
        for _i in range(settings.MIN_QUOTIENT_FAMILIAL_BONUSES_TO_PUBLISH):
            statistics_api.record_bonus_attempt(
                bonus_type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
                reason_codes=[],
                attempts_until_grant=2,
            )
        statistics_api.record_bonus_attempt(
            bonus_type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            reason_codes=[subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD],
        )

        with caplog.at_level(logging.INFO):
            statistics_api.log_bonus_credit_counters()

        second_log_record = caplog.records[-1]
        assert second_log_record.extra["counters"] == {
            "errors": {"qf_bonus_credit": {"not_in_tax_household": 1}},
            "grants": {"qf_bonus_credit": 3},
            "attempts_until_grant": {"2": 3},
        }
        assert second_log_record.extra["counters_since"] == first_log_record.extra["published_at"]

    def test_disability_grants_without_enough_crowd(self, caplog):
        statistics_api.record_bonus_attempt(
            bonus_type=subscription_models.FraudCheckType.AAH_BONUS_CREDIT, reason_codes=[], attempts_until_grant=0
        )
        statistics_api.record_bonus_attempt(
            bonus_type=subscription_models.FraudCheckType.AEEH_BONUS_CREDIT, reason_codes=[], attempts_until_grant=0
        )
        not_enough = 2 * settings.MIN_QUOTIENT_FAMILIAL_BONUSES_TO_PUBLISH - 1
        for _i in range(not_enough):
            statistics_api.record_bonus_attempt(
                bonus_type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
                reason_codes=[],
                attempts_until_grant=1,
            )

        with caplog.at_level(logging.INFO):
            statistics_api.log_bonus_credit_counters()

        log_record = caplog.records[-1]
        assert log_record.message == "Quotient Familial crowd is not thick enough"
        assert log_record.extra.get("counters") is None

    def test_withheld_counters_are_kept_until_a_crowd_joins_them(self, caplog):
        self.test_disability_grants_without_enough_crowd(caplog)

        # last quotient familial needed to pass crowd threshold
        statistics_api.record_bonus_attempt(
            bonus_type=subscription_models.FraudCheckType.QF_BONUS_CREDIT,
            reason_codes=[],
            attempts_until_grant=1,
        )

        with caplog.at_level(logging.INFO):
            statistics_api.log_bonus_credit_counters()

        log_record = caplog.records[-1]
        assert log_record.extra["counters"] == {
            "attempts_until_grant": {"0": 2, "1": 6},
            "errors": {},
            "grants": {"aah_bonus_credit": 1, "aeeh_bonus_credit": 1, "qf_bonus_credit": 6},
        }

    def test_nothing_is_logged(self, caplog):
        with caplog.at_level(logging.INFO):
            statistics_api.log_bonus_credit_counters()

        assert caplog.messages == ["No bonus credit statistics to report"]


class FirstApplicationDelaysTest:
    def test_delays_are_logged_as_a_histogram(self, caplog):
        for seconds in (30, 60, 400, 3 * 60 * 60, 30 * 24 * 60 * 60):
            statistics_api.record_first_bonus_attempt(seconds)

        with caplog.at_level(logging.INFO):
            statistics_api.log_first_bonus_credit_attempt_delays()

        log_record = caplog.records[-1]
        assert log_record.extra["first_attempt_delays"] == {"0": 3, "3600": 1, "2419200": 1}
