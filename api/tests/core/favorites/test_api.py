import pytest

from pcapi.core.favorites import api
from pcapi.core.favorites import exceptions
from pcapi.core.favorites import factories
from pcapi.core.favorites.models import FavoriteOffer
from pcapi.core.offerers.factories import OffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.users.factories import UserFactory
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.validation_status_mixin import ValidationStatus


pytestmark = pytest.mark.usefixtures("db_session")


class FavoriteOffersApiTest:
    def test_get_favorite_offer(self):
        user = UserFactory()
        offer = OfferFactory()
        favorite = factories.FavoriteOfferFactory(
            user=user,
            offer=offer,
        )

        favs_from_db = api.get_favorite_offers_for(user)

        assert len(favs_from_db) == 1
        assert favs_from_db[0].favorite.offer.id == favorite.offer.id

    def test_add_valid_offer_as_favorite(self):
        user = UserFactory()
        offer = OfferFactory()

        api.set_offer_as_favorite(user, offer.id)

        assert db.session.query(FavoriteOffer).count() == 1

    @pytest.mark.settings(MAX_FAVORITES=1)
    def test_should_raise_exception_if_max_favorites_is_reached(self):
        user = UserFactory()
        offer = OfferFactory()
        offer2 = OfferFactory()

        factories.FavoriteOfferFactory(
            user=user,
            offer=offer,
        )

        with pytest.raises(exceptions.MaxFavoritesReached):
            api.set_offer_as_favorite(user, offer2.id)

    def test_should_raise_exception_if_item_is_already_a_favorite(self):
        user = UserFactory()
        offer = OfferFactory()

        factories.FavoriteOfferFactory(
            user=user,
            offer=offer,
        )

        with pytest.raises(exceptions.AlreadyAsFavorite):
            api.set_offer_as_favorite(user, offer.id)

    def test_should_raise_exception_if_offer_is_invalid(self):
        user = UserFactory()
        offerer = OffererFactory(isActive=False, validationStatus=ValidationStatus.REJECTED)
        venue = VenueFactory(managingOfferer=offerer)
        offer = OfferFactory(venue=venue)
        offer2 = OfferFactory(validation=OfferValidationStatus.REJECTED)

        factories.FavoriteOfferFactory(
            user=user,
            offer=offer,
        )

        with pytest.raises(exceptions.InactiveOffer):
            api.set_offer_as_favorite(user, offer.id)

        with pytest.raises(exceptions.InactiveOffer):
            api.set_offer_as_favorite(user, offer2.id)

    def test_should_delete_a_user_favorite(self):
        user = UserFactory()
        offer = OfferFactory()

        favorite = factories.FavoriteOfferFactory(
            user=user,
            offer=offer,
        )

        api.delete_favorite_offer(user, favorite.id)

        assert db.session.query(FavoriteOffer).count() == 0

    def test_should_raise_an_exception_on_invalide_favorite_delete_request(self):
        user = UserFactory()
        user2 = UserFactory()
        offer = OfferFactory()

        favorite = factories.FavoriteOfferFactory(
            user=user,
            offer=offer,
        )

        with pytest.raises(exceptions.FavoriteNotFound):
            api.delete_favorite_offer(user2, favorite.id)

        assert db.session.query(FavoriteOffer).count() == 1
