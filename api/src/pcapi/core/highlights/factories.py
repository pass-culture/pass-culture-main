import datetime
import uuid

import factory

from pcapi.core.factories import BaseFactory
from pcapi.core.offers import factories as offers_factories
from pcapi.utils import db as db_utils

from . import models


class HighlightFactory(BaseFactory):
    name = factory.Sequence(lambda n: f"Valorisation thématique {n}")
    description = factory.Sequence(lambda n: f"Ceci est la valorisation thématique {n}")
    highlight_datespan = factory.LazyFunction(
        lambda: db_utils.make_inclusive_daterange(
            start=datetime.date.today() + datetime.timedelta(days=11),
            end=datetime.date.today() + datetime.timedelta(days=12),
        )
    )
    availability_datespan = factory.LazyFunction(
        lambda: db_utils.make_inclusive_daterange(
            start=datetime.date.today() - datetime.timedelta(days=10),
            end=datetime.date.today() + datetime.timedelta(days=10),
        )
    )
    mediation_uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))

    class Meta:
        model = models.Highlight


class HighlightRequestFactory(BaseFactory):
    offer = factory.SubFactory(offers_factories.OfferFactory, isActive=True)
    highlight = factory.SubFactory(HighlightFactory)

    class Meta:
        model = models.HighlightRequest
