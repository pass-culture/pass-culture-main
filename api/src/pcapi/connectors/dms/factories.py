import factory

from pcapi.core.factories import BaseFactory

from . import models


class LatestDmsImportFactory(BaseFactory):
    class Meta:
        model = models.LatestDmsImport

    isProcessing = False
    latestImportDatetime = factory.Faker("date_time")
