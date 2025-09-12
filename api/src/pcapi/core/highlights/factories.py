import datetime
import uuid

import factory

from pcapi.core.factories import BaseFactory

from . import models


class HighlightFactory(BaseFactory):
    name = "Temps fort"
    description = "Ceci est un temps fort"
    highlight_timespan = factory.LazyFunction(
        lambda: [
            datetime.datetime.utcnow() - datetime.timedelta(days=10),
            datetime.datetime.utcnow() + datetime.timedelta(days=10),
        ]
    )
    availability_timespan = factory.LazyFunction(
        lambda: [
            datetime.datetime.utcnow() + datetime.timedelta(days=11),
            datetime.datetime.utcnow() + datetime.timedelta(days=12),
        ]
    )
    mediation_uuid = factory.LazyFunction(lambda: str(uuid.uuid4()))

    class Meta:
        model = models.Highlight
