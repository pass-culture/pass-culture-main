import factory

from pcapi.core.artist.factories import ArtistFactory
from pcapi.core.factories import BaseFactory
from pcapi.core.favorites import models
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.users.factories import UserFactory


class FavoriteOfferFactory(BaseFactory):
    class Meta:
        model = models.FavoriteOffer

    offer = factory.SubFactory(OfferFactory)
    user = factory.SubFactory(UserFactory)


class FavoriteArtistFactory(BaseFactory):
    class Meta:
        model = models.FavoriteArtist

    artist = factory.SubFactory(ArtistFactory)
    user = factory.SubFactory(UserFactory)
