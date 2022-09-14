import pytest

from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.sandboxes.scripts.creators.industrial import save_industrial_sandbox

from tests.conftest import clean_database


@pytest.mark.skip("This is a very long-running test used to help working on the sandbox")
class SaveIndustrialSandboxTest:
    @clean_database
    def test_creations(self, clear_tests_invoices_bucket):
        save_industrial_sandbox()

        assert offerers_models.Offerer.query.count() == 32
        assert offerers_models.Venue.query.count() == 46
        assert finance_models.BusinessUnit.query.count() == 46
        assert offers_models.Offer.query.count() == 127
        assert offers_models.Stock.query.count() == 128
        assert 170 <= bookings_models.Booking.query.count() <= 200
        assert finance_models.Invoice.query.count() == 8
        assert finance_models.Cashflow.query.count() == 9
        assert (
            finance_models.Pricing.query.filter(
                finance_models.Pricing.status != finance_models.PricingStatus.INVOICED
            ).count()
        ) == 12  # FIXME (dbaty, 2022-09-14): should probably be 0
