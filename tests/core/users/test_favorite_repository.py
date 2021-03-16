from datetime import datetime

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories
from pcapi.core.users.repository import find_favorites_domain_by_beneficiary
from pcapi.domain.favorite.favorite import FavoriteDomain


class FindByBeneficiaryTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_a_list_of_beneficiary_favorites(self, app):
        # given
        beneficiary = factories.UserFactory()
        venue = offers_factories.VenueFactory()
        offer_1 = offers_factories.ThingOfferFactory(venue=venue)
        mediation_1 = offers_factories.MediationFactory(offer=offer_1)
        factories.FavoriteFactory(mediation=mediation_1, offer=offer_1, user=beneficiary)
        offer_2 = offers_factories.ThingOfferFactory(venue=venue)
        factories.FavoriteFactory(offer=offer_2, user=beneficiary)

        # when
        favorites = find_favorites_domain_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 2
        assert isinstance(favorites[0], FavoriteDomain)
        assert isinstance(favorites[1], FavoriteDomain)

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_favorites_of_other_beneficiary(self, app):
        # given
        beneficiary = factories.UserFactory()
        other_beneficiary = factories.UserFactory()
        offer = offers_factories.ThingOfferFactory()
        mediation = offers_factories.MediationFactory(offer=offer)
        factories.FavoriteFactory(mediation=mediation, offer=offer, user=other_beneficiary)

        # when
        favorites = find_favorites_domain_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_return_booking_when_favorite_offer_is_booked(self, app):
        # given
        beneficiary = factories.UserFactory()
        venue = offers_factories.VenueFactory()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer, price=0)
        booking = bookings_factories.BookingFactory(stock=stock, user=beneficiary)
        mediation = offers_factories.MediationFactory(offer=offer)
        favorite = factories.FavoriteFactory(mediation=mediation, offer=offer, user=beneficiary)

        # when
        favorites = find_favorites_domain_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 1
        favorite = favorites[0]
        assert favorite.is_booked is True
        assert favorite.booking_identifier == booking.id
        assert favorite.booked_stock_identifier == stock.id
        assert favorite.booking_quantity == booking.quantity

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_booking_when_favorite_offer_booking_is_cancelled(self, app):
        # given
        beneficiary = factories.UserFactory()
        venue = offers_factories.VenueFactory()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer, price=0)
        bookings_factories.BookingFactory(
            stock=stock, user=beneficiary, isCancelled=True, cancellationDate=datetime.now()
        )
        mediation = offers_factories.MediationFactory(offer=offer)
        favorite = factories.FavoriteFactory(mediation=mediation, offer=offer, user=beneficiary)

        # when
        favorites = find_favorites_domain_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 1
        favorite = favorites[0]
        assert favorite.is_booked is False
