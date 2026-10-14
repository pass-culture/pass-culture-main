import pytest

import pcapi.core.artist.factories as artist_factories
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.discoveries.models as discoveries_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import factories as users_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class Returns204Test:
    def test_when_user_is_logged_in_and_regular_offer(self, client):
        booking = bookings_factories.BookingFactory(token="ABCDEF")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

        response = client.with_session_auth("pro@example.com").patch(f"/bookings/use/token/{booking.token}")

        assert response.status_code == 204
        booking = db.session.query(Booking).one()
        assert booking.status is BookingStatus.USED

    def test_validation_creates_discoveries_for_work_and_offer_artists_idempotently(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.OfferFactory()
        work = discoveries_models.Work(title="A film", media_type=discoveries_models.WorkMediaType.FILM, offer=offer)
        artists = artist_factories.ArtistFactory.create_batch(2)
        db.session.add_all([work, *artists])
        db.session.flush()
        for artist in artists:
            artist_factories.ArtistOfferLinkFactory(offer_id=offer.id, artist_id=artist.id)
        first_booking = bookings_factories.BookingFactory(stock__offer=offer, user=user, token="DISC01")
        second_booking = bookings_factories.BookingFactory(stock__offer=offer, user=user, token="DISC02")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offer.venue.managingOfferer)

        response = client.with_session_auth(pro_user.email).patch(f"/bookings/use/token/{first_booking.token}")

        assert response.status_code == 204
        discoveries = db.session.query(discoveries_models.Discovery).filter_by(user_id=user.id).all()
        assert len(discoveries) == 3
        assert {discovery.work_id for discovery in discoveries if discovery.work_id is not None} == {work.id}
        assert {discovery.artist_id for discovery in discoveries if discovery.artist_id is not None} == {
            artist.id for artist in artists
        }
        assert all(discovery.offer_origin_id == offer.id for discovery in discoveries)

        response = client.with_session_auth(pro_user.email).patch(f"/bookings/use/token/{second_booking.token}")

        assert response.status_code == 204
        assert db.session.query(discoveries_models.Discovery).filter_by(user_id=user.id).count() == 3

    def test_validation_without_work_creates_artist_discoveries_only(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.OfferFactory()
        assert offer.work is None
        assert offer.product is None or offer.product.work is None
        artists = artist_factories.ArtistFactory.create_batch(2)
        db.session.add_all(artists)
        db.session.flush()
        for artist in artists:
            artist_factories.ArtistOfferLinkFactory(offer_id=offer.id, artist_id=artist.id)
        booking = bookings_factories.BookingFactory(stock__offer=offer, user=user, token="DISC03")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offer.venue.managingOfferer)

        response = client.with_session_auth(pro_user.email).patch(f"/bookings/use/token/{booking.token}")

        assert response.status_code == 204
        discoveries = db.session.query(discoveries_models.Discovery).filter_by(user_id=user.id).all()
        assert len(discoveries) == 2
        assert all(discovery.work_id is None for discovery in discoveries)
        assert {discovery.artist_id for discovery in discoveries} == {artist.id for artist in artists}

    def test_when_user_is_logged_in_expect_booking_with_token_in_lower_case_to_be_used(self, client):
        booking = bookings_factories.BookingFactory(token="ABCDEF")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

        response = client.with_session_auth("pro@example.com").patch(f"/bookings/use/token/{booking.token}")

        assert response.status_code == 204
        booking = db.session.query(Booking).one()
        assert booking.status is BookingStatus.USED


class Returns401Test:
    def test_when_user_not_logged_in(self, client):
        response = client.patch("/bookings/use/token/TOKEN")
        assert response.status_code == 401


class Returns403Test:
    def test_when_offerer_is_closed(self, client):
        offerer = offerers_factories.ClosedOffererFactory()
        booking = bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer)
        pro_user = offerers_factories.UserOffererFactory(offerer=offerer).user

        response = client.with_session_auth(pro_user.email).patch(f"/bookings/use/token/{booking.token}")

        assert response.status_code == 403
        assert response.json["booking"] == ["Vous ne pouvez plus valider de contremarque sur une structure fermée"]
        booking = db.session.get(Booking, booking.id)
        assert booking.status == BookingStatus.CONFIRMED

    def test_error_if_venue_is_closed(self, client):
        venue = offerers_factories.VenueFactory(state=offerers_models.VenueState.CLOSED)
        booking = bookings_factories.BookingFactory(token="ABCDEF", stock__offer__venue=venue)
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=venue.managingOfferer)

        response = client.with_session_auth("pro@example.com").patch(f"/bookings/use/token/{booking.token}")
        assert response.status_code == 403


class Returns404Test:
    def test_when_user_is_not_attached_to_linked_offerer(self, client):
        booking = bookings_factories.BookingFactory()
        another_pro_user = offerers_factories.UserOffererFactory().user

        response = client.with_session_auth(another_pro_user.email).patch(f"/bookings/use/token/{booking.token}")

        assert response.status_code == 404
        assert response.json["global"] == [
            "La contremarque n'existe pas, ou vous n'avez pas les droits nécessaires pour y accéder."
        ]
        booking = db.session.get(Booking, booking.id)
        assert booking.status == BookingStatus.CONFIRMED

    def test_missing_token(self, client):
        response = client.patch("/bookings/use/token/")
        assert response.status_code == 404

    def test_unknown_token(self, client):
        pro_user = users_factories.ProFactory()
        response = client.with_session_auth(pro_user.email).patch("/bookings/use/token/UNKNOWN")
        assert response.status_code == 404
        assert response.json["global"] == [
            "La contremarque n'existe pas, ou vous n'avez pas les droits nécessaires pour y accéder."
        ]


class Returns410Test:
    def test_when_user_is_logged_in_and_booking_has_been_cancelled_already(self, client):
        booking = bookings_factories.CancelledBookingFactory()
        user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=booking.offerer)

        response = client.with_session_auth(user.email).patch(f"/bookings/use/token/{booking.token}")

        assert response.status_code == 410
        assert response.json["booking_cancelled"] == ["Cette réservation a été annulée"]
        booking = db.session.get(Booking, booking.id)
        assert booking.status == BookingStatus.CANCELLED
