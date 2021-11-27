import logging

import pytest

import pcapi.core.bookings.models as bookings_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.users.models as users_models
from pcapi.models.product import Product
from pcapi.sandboxes.scripts.save_sandbox import save_sandbox


logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("db_session")
def test_save_activation_sandbox(app):
    save_sandbox("activation")

    assert bookings_models.Booking.query.count() == 0
    assert offers_models.Mediation.query.count() == 0
    assert offers_models.Offer.query.count() == 1
    assert offerers_models.Offerer.query.count() == 1
    assert Product.query.count() == 1
    assert offers_models.Stock.query.count() == 1
    assert users_models.User.query.count() == 0
    assert offers_models.Stock.query.one().quantity == 10000
