import factory

from pcapi.core.factories import BaseFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.utils import date as date_utils

from . import models


class CulturalOutreachFactory(BaseFactory[models.CulturalOutreach]):
    class Meta:
        model = models.CulturalOutreach

    offer = factory.SubFactory(OfferFactory)
    status = models.CulturalOutreachStatus.PENDING


class ClaimedCulturalOutreachFactory(CulturalOutreachFactory):
    claimedDatetime = factory.LazyFunction(date_utils.get_naive_utc_now)
