from domain.favorite.favorite import Favorite

from infrastructure.repository.favorite.favorite_sql_repository import FavoriteSQLRepository

from repository import repository
import pytest
from model_creators.generic_creators import create_offerer, create_user, \
    create_venue, create_mediation, create_favorite, create_booking
from model_creators.specific_creators import create_offer_with_thing_product, create_stock_from_offer


class FindByBeneficiaryTest:
    def setup_method(self):
        self.favorite_sql_repository = FavoriteSQLRepository()

    @pytest.mark.usefixtures("db_session")
    def test_returns_a_list_of_beneficiary_favorites(self, app):
        # given
        beneficiary = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer_1 = create_offer_with_thing_product(venue=venue)
        mediation_1 = create_mediation(offer=offer_1)
        favorite_1 = create_favorite(mediation=mediation_1, offer=offer_1, user=beneficiary)
        offer_2 = create_offer_with_thing_product(venue=venue)
        favorite_2 = create_favorite(offer=offer_2, user=beneficiary)
        repository.save(favorite_1, favorite_2)

        # when
        favorites = self.favorite_sql_repository.find_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 2
        assert isinstance(favorites[0], Favorite)
        assert isinstance(favorites[1], Favorite)

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_favorites_of_other_beneficiary(self, app):
        # given
        beneficiary = create_user()
        other_beneficiary = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        mediation = create_mediation(offer=offer)
        favorite = create_favorite(mediation=mediation, offer=offer, user=other_beneficiary)
        repository.save(favorite)

        # when
        favorites = self.favorite_sql_repository.find_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_return_booking_when_favorite_offer_is_booked(self, app):
        # given
        beneficiary = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        stock = create_stock_from_offer(idx=123, offer=offer, price = 0)
        booking = create_booking(idx=321, stock=stock, venue=venue, user=beneficiary)
        mediation = create_mediation(offer=offer)
        favorite = create_favorite(mediation=mediation, offer=offer, user=beneficiary)
        repository.save(favorite, booking)

        # when
        favorites = self.favorite_sql_repository.find_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 1
        favorite = favorites[0]
        assert favorite.is_booked is True
        assert favorite.booking_identifier == booking.id
        assert favorite.booked_stock_identifier == stock.id

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_booking_when_favorite_offer_booking_is_cancelled(self, app):
        # given
        beneficiary = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        stock = create_stock_from_offer(idx=123, offer=offer, price = 0)
        booking = create_booking(idx=321, stock=stock, venue=venue, user=beneficiary, is_cancelled=True)
        mediation = create_mediation(offer=offer)
        favorite = create_favorite(mediation=mediation, offer=offer, user=beneficiary)
        repository.save(favorite, booking)

        # when
        favorites = self.favorite_sql_repository.find_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 1
        favorite = favorites[0]
        assert favorite.is_booked is False
