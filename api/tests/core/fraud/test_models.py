import datetime

import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models
from pcapi.core.fraud.models import _parse_jouve_date
from pcapi.core.mails.transactional.users import dms_subscription_emails
from pcapi.core.subscription.dms import api as dms_api
from pcapi.core.subscription.dms import dms_internal_mailing
from pcapi.core.subscription.dms import messages as dms_subscription_messages


class GetRegistrationDatetimeTest:
    @pytest.mark.parametrize(
        "factory_class",
        [
            fraud_factories.UbbleContentFactory,
            fraud_factories.DMSContentFactory,
            fraud_factories.EduconnectContentFactory,
        ],
    )
    def test_has_no_timezone(self, factory_class):
        content = factory_class()

        registration_datetime = content.get_registration_datetime()
        assert not registration_datetime.tzinfo


class OrphanDmsApplicationTest:
    def test_default_values_on_creation(self):
        orphan = fraud_factories.OrphanDmsFraudCheckFactory.build(process_id=1, application_id=2)
        assert orphan.email is None


class FraudHelperFunctionsTest:
    @pytest.mark.parametrize(
        "date",
        [
            "2020-01-01",
            "01/01/2020",
            "2020-01-01T00:00:00",
        ],
    )
    def test__parse_jouve_date_success(self, date):
        assert _parse_jouve_date(date) == datetime.datetime(2020, 1, 1, 0, 0)

    @pytest.mark.parametrize(
        "date",
        [
            "Yesteryear",
            "2020/01/01",
        ],
    )
    def test__parse_jouve_date_error(self, date):
        assert _parse_jouve_date(date) is None


class DmsErrorKeyLabelTest:
    def test_dms_mailing_labels(self):
        for key in models.DmsFieldErrorKeyEnum:
            assert dms_subscription_emails.FIELD_ERROR_LABELS.get(key) is not None

    def test_dms_api_labels(self):
        for key in models.DmsFieldErrorKeyEnum:
            assert dms_api.FIELD_ERROR_LABELS.get(key) is not None

    def test_dms_internal_mailing_labels(self):
        for key in models.DmsFieldErrorKeyEnum:
            assert dms_internal_mailing.FIELD_ERROR_LABELS.get(key) is not None

    def test_dms_subscription_messages(self):
        for key in models.DmsFieldErrorKeyEnum:
            assert dms_subscription_messages.FIELD_ERROR_LABELS.get(key) is not None
