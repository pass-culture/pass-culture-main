import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
import pcapi.core.history.factories as history_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.db_utils import clean_e2e_data
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class CleanE2eDataTest:
    def test_deletes_user_with_no_related_data(self) -> None:
        user = users_factories.ProFactory()
        db.session.flush()
        user_id = user.id

        clean_e2e_data(user_id)

        assert db.session.query(users_models.User).filter_by(id=user_id).count() == 0

    def test_deletes_user_and_offerer_chain(self) -> None:
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer)
        db.session.flush()

        user_id = user.id
        offerer_id = offerer.id
        venue_id = venue.id
        offer_id = offer.id
        stock_id = stock.id

        clean_e2e_data(user_id)

        assert db.session.query(users_models.User).filter_by(id=user_id).count() == 0
        assert db.session.query(offerers_models.Offerer).filter_by(id=offerer_id).count() == 0
        assert db.session.query(offerers_models.Venue).filter_by(id=venue_id).count() == 0
        assert db.session.query(offers_models.Offer).filter_by(id=offer_id).count() == 0
        assert db.session.query(offers_models.Stock).filter_by(id=stock_id).count() == 0

    def test_deletes_bookings_through_offer_chain(self) -> None:
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        stock = offers_factories.StockFactory(offer__venue=venue)
        booking = bookings_factories.BookingFactory(stock=stock)
        db.session.flush()

        user_id = user.id
        booking_id = booking.id

        clean_e2e_data(user_id)

        assert db.session.query(bookings_models.Booking).filter_by(id=booking_id).count() == 0

    def test_deletes_action_history(self) -> None:
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        action = history_factories.ActionHistoryFactory(
            user=user,
            offerer=offerer,
        )
        db.session.flush()

        user_id = user.id
        action_id = action.id

        clean_e2e_data(user_id)

        from pcapi.core.history import models as history_models

        assert db.session.query(history_models.ActionHistory).filter_by(id=action_id).count() == 0

    def test_preserves_unrelated_user_data(self) -> None:
        target_user = users_factories.ProFactory()
        other_user = users_factories.ProFactory()
        other_offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=other_user, offerer=other_offerer)
        db.session.flush()

        target_user_id = target_user.id
        other_user_id = other_user.id
        other_offerer_id = other_offerer.id

        clean_e2e_data(target_user_id)

        assert db.session.query(users_models.User).filter_by(id=other_user_id).count() == 1
        assert db.session.query(offerers_models.Offerer).filter_by(id=other_offerer_id).count() == 1

    def test_raises_on_invalid_environment(self) -> None:
        with pytest.raises(ValueError, match="You cannot do this on this environment"):
            with pytest.MonkeyPatch.context() as monkeypatch:
                monkeypatch.setattr("pcapi.db_utils.settings.ENV", "production")
                clean_e2e_data(1)
