from typing import Optional

import factory

from pcapi.core.offerers import models
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import VenueCriterion
from pcapi.core.offerers.models import VenueLabel
from pcapi.core.offerers.models import VenueType
from pcapi.core.offers.factories import CriterionFactory
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.testing import BaseFactory
from pcapi.utils import crypto


class VirtualVenueTypeFactory(BaseFactory):
    class Meta:
        model = VenueType

    label = "Offre numérique"


class VenueTypeFactory(BaseFactory):
    class Meta:
        model = VenueType
        sqlalchemy_get_or_create = ("label",)

    label = "Librairie"


class VenueLabelFactory(BaseFactory):
    class Meta:
        model = VenueLabel

    label = "Cinéma d'art et d'essai"


class VenueContactFactory(BaseFactory):
    class Meta:
        model = models.VenueContact

    venue = factory.SubFactory(VenueFactory)
    email = "contact@venue.com"
    website = "https://my@website.com"
    phone_number = "+33102030405"
    social_medias = {"instagram": "http://instagram.com/@venue"}


class VenueCriterionFactory(BaseFactory):
    class Meta:
        model = VenueCriterion

    venue = factory.SubFactory(VenueFactory)
    criterion = factory.SubFactory(CriterionFactory)


DEFAULT_PREFIX = "development_prefix"
DEFAULT_SECRET = "clearSecret"
DEFAULT_CLEAR_API_KEY = f"{DEFAULT_PREFIX}_{DEFAULT_SECRET}"


class ApiKeyFactory(BaseFactory):
    class Meta:
        model = ApiKey

    offerer = factory.SubFactory(OffererFactory)
    prefix = DEFAULT_PREFIX

    @factory.post_generation
    def hash_secret(self, create: bool, extracted: Optional[str]) -> None:
        self.secret = crypto.hash_password(extracted or DEFAULT_SECRET)
