import factory

from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories
from pcapi.utils import crypto

from . import models


class UserOffererFactory(BaseFactory):
    class Meta:
        model = models.UserOfferer

    user = factory.SubFactory(users_factories.ProFactory)
    offerer = factory.SubFactory(OffererFactory)


class VirtualVenueTypeFactory(BaseFactory):
    class Meta:
        model = models.VenueType

    label = "Offre numérique"


class VenueTypeFactory(BaseFactory):
    class Meta:
        model = models.VenueType
        sqlalchemy_get_or_create = ("label",)

    label = "Librairie"


class VenueLabelFactory(BaseFactory):
    class Meta:
        model = models.VenueLabel

    label = "Cinéma d'art et d'essai"


class VenueContactFactory(BaseFactory):
    class Meta:
        model = models.VenueContact

    venue = factory.SubFactory(VenueFactory)
    email = "contact@venue.com"
    website = "https://my@website.com"
    phone_number = "+33102030405"
    social_medias = {"instagram": "http://instagram.com/@venue"}


DEFAULT_PREFIX = "development_prefix"
DEFAULT_SECRET = "clearSecret"
DEFAULT_CLEAR_API_KEY = f"{DEFAULT_PREFIX}_{DEFAULT_SECRET}"


class ApiKeyFactory(BaseFactory):
    class Meta:
        model = models.ApiKey

    offerer = factory.SubFactory(OffererFactory)
    prefix = DEFAULT_PREFIX

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        kwargs["secret"] = crypto.hash_password(kwargs.get("secret", DEFAULT_SECRET))
        return super()._create(model_class, *args, **kwargs)
