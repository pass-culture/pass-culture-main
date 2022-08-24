import factory

from pcapi.core import testing

from . import models


class LatestDmsImportFactory(testing.BaseFactory):
    class Meta:
        model = models.LatestDmsImport

    isProcessing = False
    latestImportDatetime = factory.Faker("date_time")
