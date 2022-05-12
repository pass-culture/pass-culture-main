import datetime

import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud.models import _parse_jouve_date


class GetRegistrationDatetimeTest:
    @pytest.mark.parametrize(
        "factory_class",
        [
            fraud_factories.UbbleContentFactory,
            fraud_factories.DMSContentFactory,
            fraud_factories.JouveContentFactory,
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
