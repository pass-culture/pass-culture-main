import pytest

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.sandboxes.scripts.creators.industrial import save_industrial_sandbox

from tests.conftest import clean_database


@pytest.mark.skip("This is a very long-running test used to help working on the sandbox")
class SaveIndustrialSandboxTest:
    @clean_database
    def test_creations(self, clear_tests_invoices_bucket, css_font_http_request_mock):
        save_industrial_sandbox()

        # Yes, this is mostly ridiculous. But we like to keep these
        # magic numbers here. Developers update them from time to
        # time, acting as if the numbers made sense. "The number of
        # stocks in the sandbox? 1336, obviously, why are you asking?"
        assert offerers_models.Offerer.query.count() == 62
        assert offerers_models.Venue.query.count() == 78
        assert offers_models.Offer.query.count() == 328
        assert offers_models.Stock.query.count() == 1336
        assert 200 <= bookings_models.Booking.query.count() <= 300
        assert finance_models.Invoice.query.count() == 3
        assert finance_models.Cashflow.query.count() == 4
        assert educational_models.EducationalInstitution.query.count() == 27
        assert (
            finance_models.Pricing.query.filter(
                finance_models.Pricing.status != finance_models.PricingStatus.INVOICED
            ).count()
        ) == 60  # FIXME (dbaty, 2022-09-14): should probably be 0
