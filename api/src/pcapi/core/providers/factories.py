from pcapi.core.providers.models import AllocinePivot
from pcapi.core.testing import BaseFactory


class AllocinePivotFactory(BaseFactory):
    class Meta:
        model = AllocinePivot

    siret = "12345678912345"
    theaterId = "XXXXXXXXXXXXXXXXXX=="
    internalId = "PXXXXX"
