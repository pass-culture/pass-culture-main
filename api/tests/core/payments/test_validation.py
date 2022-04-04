import datetime

import pytest

from pcapi.core.categories import subcategories
from pcapi.core.payments import exceptions
from pcapi.core.payments import factories
from pcapi.core.payments import models
from pcapi.core.payments import validation


class CustomReimbursementRuleValidationTest:
    def _make_rule(self, **kwargs):
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        kwargs.setdefault("offererId", 1)
        kwargs.setdefault("rate", 0.8)
        kwargs.setdefault("subcategories", [])
        kwargs.setdefault("timespan", (tomorrow, None))
        return models.CustomReimbursementRule(**kwargs)

    def test_check_subcategories(self):
        rule = self._make_rule(subcategories=[])
        validation.validate_reimbursement_rule(rule)  # should not raise

        rule.subcategories = [subcategories.SALON.id]
        validation.validate_reimbursement_rule(rule)  # should not raise

        rule.subcategories = "CYCLIMSE"
        with pytest.raises(exceptions.UnknownSubcategoryForReimbursementRule) as exc:
            validation.validate_reimbursement_rule(rule)
            assert str(exc) == """"CYCLIMSE n'est pas une sous-catégorie valide."""

    def test_check_start_date(self):
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)

        rule = self._make_rule(timespan=(tomorrow, None))
        validation.validate_reimbursement_rule(rule)  # should not raise

        rule = self._make_rule(timespan=(today, None))
        with pytest.raises(exceptions.WrongDateForReimbursementRule):
            validation.validate_reimbursement_rule(rule)

    def test_check_end_date(self):
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)
        two_days_from_now = today + datetime.timedelta(days=2)

        rule = self._make_rule(timespan=(tomorrow, None))
        validation.validate_reimbursement_rule(rule)  # should not raise

        rule = self._make_rule(timespan=(tomorrow, two_days_from_now))
        validation.validate_reimbursement_rule(rule)  # should not raise

        rule = self._make_rule(timespan=(tomorrow, tomorrow))
        with pytest.raises(exceptions.WrongDateForReimbursementRule):
            validation.validate_reimbursement_rule(rule)

    @pytest.mark.usefixtures("db_session")
    def test_check_no_conflict_if_timespans_do_not_overlap(self):
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)
        timespan1 = (yesterday, today)
        timespan2 = (tomorrow, None)
        rule1 = factories.CustomReimbursementRuleFactory(timespan=timespan1)
        rule2 = self._make_rule(offererId=rule1.offererId, timespan=timespan2)
        validation.validate_reimbursement_rule(rule2)  # should not raise

    @pytest.mark.usefixtures("db_session")
    def test_check_no_conflict_if_different_subcategories(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        timespan = (tomorrow, None)
        rule1 = factories.CustomReimbursementRuleFactory(timespan=timespan, subcategories=["SALON"])
        rule2 = self._make_rule(offererId=rule1.offererId, timespan=timespan, subcategories=["VOD"])
        validation.validate_reimbursement_rule(rule2)  # should not raise

    @pytest.mark.usefixtures("db_session")
    def test_check_no_conflicts_with_itself(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        rule = factories.CustomReimbursementRuleFactory(timespan=(tomorrow, None))
        validation.validate_reimbursement_rule(rule)

    @pytest.mark.usefixtures("db_session")
    def test_check_conflicts_if_subcategories_overlap(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        timespan = (tomorrow, None)
        rule1 = factories.CustomReimbursementRuleFactory(timespan=timespan, subcategories=["SALON"])
        rule2 = self._make_rule(offererId=rule1.offererId, timespan=timespan, subcategories=["VOD", "SALON"])
        with pytest.raises(exceptions.ConflictingReimbursementRule):
            validation.validate_reimbursement_rule(rule2)

    @pytest.mark.usefixtures("db_session")
    def test_check_conflicts_if_existing_rule_on_all_subcategories(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        timespan = (tomorrow, None)
        rule1 = factories.CustomReimbursementRuleFactory(timespan=(tomorrow, None), subcategories=[])
        rule2 = self._make_rule(offererId=rule1.offererId, timespan=timespan, subcategories=["VOD"])
        with pytest.raises(exceptions.ConflictingReimbursementRule):
            validation.validate_reimbursement_rule(rule2)
