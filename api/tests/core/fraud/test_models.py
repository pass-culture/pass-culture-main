import pytest

from pcapi.core.fraud import factories as fraud_factories


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

        datetime = content.get_registration_datetime()
        assert not datetime.tzinfo
