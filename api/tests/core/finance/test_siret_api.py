import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.finance import siret_api
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories

from tests.conftest import clean_database


class DeleteSiretTest:
    @clean_database
    def test_basics(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        dependent_venue = offerers_factories.VenueFactory(pricing_point=venue)
        initial_statuses = set(models.PricingStatus) - {models.PricingStatus.PENDING}
        for status in initial_statuses:
            factories.PricingFactory(pricingPoint=venue, status=status)
        assert models.Pricing.query.count() == 5

        siret_api.remove_siret(venue, comment="no SIRET because reasons", apply_changes=True)

        assert venue.siret is None
        assert venue.comment == "no SIRET because reasons"
        assert venue.current_pricing_point_id is None
        assert dependent_venue.current_pricing_point_id is None
        assert models.Pricing.query.count() == 4
        left_statuses = {status for status, in models.Pricing.query.with_entities(models.Pricing.status)}
        assert left_statuses == initial_statuses - {models.PricingStatus.VALIDATED}

    @clean_database
    def test_dry_run(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")

        siret_api.remove_siret(venue, comment="xxx", apply_changes=False)

        assert venue.siret is not None
        assert venue.comment is None

    @clean_database
    def test_revenue_check(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        user = users_factories.RichBeneficiaryFactory()
        bookings_factories.UsedBookingFactory(
            amount=10_000,
            user=user,
            stock__offer__venue=venue,
        )

        with pytest.raises(siret_api.CheckError) as err:
            siret_api.remove_siret(venue, comment="xxx", apply_changes=True)
        assert "Venue has an unexpectedly high yearly revenue" in str(err.value)
        assert venue.siret is not None

        siret_api.remove_siret(
            venue,
            comment="xxx",
            apply_changes=True,
            override_revenue_check=True,  # <-- override check
        )
        assert venue.siret is None

    @clean_database
    def test_refuse_if_pricing_point_has_pending_pricings(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        factories.PricingFactory(pricingPoint=venue, status=models.PricingStatus.PENDING)

        with pytest.raises(siret_api.CheckError) as err:
            siret_api.remove_siret(venue, comment="xxx", apply_changes=True)
        assert str(err.value) == "Venue has pending pricings"
