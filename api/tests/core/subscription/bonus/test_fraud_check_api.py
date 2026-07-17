import datetime
from unittest.mock import patch

import pytest

from pcapi.core.subscription.bonus import fraud_check_api
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.utils import countries as countries_utils


class QuotientFamilialTest:
    @pytest.mark.settings(BONUS_CREDIT_DELAY=0)
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_quotient_familial_bonus_task.delay")
    def test_create_qf_fraud_check_without_delay_setting(self, mocked_apply_for_qf_task):
        user = users_factories.BeneficiaryFactory()

        fraud_check = fraud_check_api.create_qf_bonus_credit_fraud_check(
            user,
            last_name="dupont",
            first_names=["alexis"],
            birth_date=datetime.date(1982, 12, 7),
            gender=users_models.GenderEnum.F,
            birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
            birth_city_cog_code="08480",
            origin="test",
        )

        mocked_apply_for_qf_task.assert_called_once()
        mocked_apply_for_qf_task.assert_called_with({"fraud_check_id": fraud_check.id})

    @pytest.mark.settings(BONUS_CREDIT_DELAY=0)
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_quotient_familial_bonus_task.delay")
    def test_create_qf_fraud_check_without_delay_setting_override(self, mocked_apply_for_qf_task):
        user = users_factories.BeneficiaryFactory()

        fraud_check_api.create_qf_bonus_credit_fraud_check(
            user,
            last_name="dupont",
            first_names=["alexis"],
            birth_date=datetime.date(1982, 12, 7),
            gender=users_models.GenderEnum.F,
            birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
            birth_city_cog_code="08480",
            origin="test",
            publish_task=False,
        )

        mocked_apply_for_qf_task.assert_not_called()

    @pytest.mark.settings(BONUS_CREDIT_DELAY=1)
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_quotient_familial_bonus_task.delay")
    def test_create_qf_fraud_check_with_delay_setting(self, mocked_apply_for_qf_task):
        user = users_factories.BeneficiaryFactory()

        fraud_check_api.create_qf_bonus_credit_fraud_check(
            user,
            last_name="dupont",
            first_names=["alexis"],
            birth_date=datetime.date(1982, 12, 7),
            gender=users_models.GenderEnum.F,
            birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
            birth_city_cog_code="08480",
            origin="test",
        )

        mocked_apply_for_qf_task.assert_not_called()

    @pytest.mark.settings(BONUS_CREDIT_DELAY=1)
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_quotient_familial_bonus_task.delay")
    def test_qf_fraud_check_with_delay_setting_override(self, mocked_apply_for_qf_task):
        user = users_factories.BeneficiaryFactory()

        fraud_check = fraud_check_api.create_qf_bonus_credit_fraud_check(
            user,
            last_name="dupont",
            first_names=["alexis"],
            birth_date=datetime.date(1982, 12, 7),
            gender=users_models.GenderEnum.F,
            birth_country_cog_code=countries_utils.FRANCE_INSEE_CODE,
            birth_city_cog_code="08480",
            origin="test",
            publish_task=True,
        )

        mocked_apply_for_qf_task.assert_called_once()
        mocked_apply_for_qf_task.assert_called_with({"fraud_check_id": fraud_check.id})


class DisabilityAllowanceTest:
    @pytest.mark.settings(BONUS_CREDIT_DELAY=0)
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_adult_disability_bonus_task.delay")
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_disabled_child_education_bonus_task.delay")
    def test_create_disability_fraud_check_without_delay_setting(
        self, mocked_apply_for_aeeh_task, mocked_apply_for_aah_task
    ):
        user = users_factories.BeneficiaryFactory()

        aah_fraud_check, aeeh_fraud_check = fraud_check_api.create_disability_bonus_credit_fraud_checks(
            user,
            origin="test",
        )

        mocked_apply_for_aah_task.assert_called_once()
        mocked_apply_for_aah_task.assert_called_with({"fraud_check_id": aah_fraud_check.id})

        mocked_apply_for_aeeh_task.assert_called_once()
        mocked_apply_for_aeeh_task.assert_called_with({"fraud_check_id": aeeh_fraud_check.id})

    @pytest.mark.settings(BONUS_CREDIT_DELAY=0)
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_adult_disability_bonus_task.delay")
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_disabled_child_education_bonus_task.delay")
    def test_create_disability_fraud_check_without_delay_setting_override(
        self, mocked_apply_for_aeeh_task, mocked_apply_for_aah_task
    ):
        user = users_factories.BeneficiaryFactory()

        fraud_check_api.create_disability_bonus_credit_fraud_checks(user, origin="test", publish_task=False)

        mocked_apply_for_aah_task.assert_not_called()
        mocked_apply_for_aeeh_task.assert_not_called()

    @pytest.mark.settings(BONUS_CREDIT_DELAY=1)
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_adult_disability_bonus_task.delay")
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_disabled_child_education_bonus_task.delay")
    def test_create_disability_fraud_check_with_delay_setting(
        self, mocked_apply_for_aeeh_task, mocked_apply_for_aah_task
    ):
        user = users_factories.BeneficiaryFactory()

        fraud_check_api.create_disability_bonus_credit_fraud_checks(user, origin="test", publish_task=False)

        mocked_apply_for_aah_task.assert_not_called()
        mocked_apply_for_aeeh_task.assert_not_called()

    @pytest.mark.settings(BONUS_CREDIT_DELAY=1)
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_adult_disability_bonus_task.delay")
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_disabled_child_education_bonus_task.delay")
    def test_create_disability_fraud_check_with_delay_setting_override(
        self, mocked_apply_for_aeeh_task, mocked_apply_for_aah_task
    ):
        user = users_factories.BeneficiaryFactory()

        aah_fraud_check, aeeh_fraud_check = fraud_check_api.create_disability_bonus_credit_fraud_checks(
            user, origin="test", publish_task=True
        )

        mocked_apply_for_aah_task.assert_called_once()
        mocked_apply_for_aah_task.assert_called_with({"fraud_check_id": aah_fraud_check.id})

        mocked_apply_for_aeeh_task.assert_called_once()
        mocked_apply_for_aeeh_task.assert_called_with({"fraud_check_id": aeeh_fraud_check.id})
