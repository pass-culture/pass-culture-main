from pcapi.core.testing import BaseFactory
from pcapi.models.allocine_pivot import AllocinePivot


class AllocinePivotFactory(BaseFactory):
    class Meta:
        model = AllocinePivot

    siret = "12345678912345"
    theaterId = "XXXXXXXXXXXXXXXXXX=="
    internalId = "PXXXXX"
