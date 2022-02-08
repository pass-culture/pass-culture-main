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


class OrphanDmsApplicationTest:
    def test_default_values_on_creation(self):
        orphan = fraud_factories.OrphanDmsFraudCheckFactory(process_id=1, application_id=2)
        assert orphan.email is None
