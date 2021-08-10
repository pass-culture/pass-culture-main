import datetime

import factory

from pcapi.core.testing import BaseFactory

from . import models


class EducationalInstitutionFactory(BaseFactory):
    class Meta:
        model = models.EducationalInstitution

    institutionId = factory.Sequence("{}470009E".format)


class EducationalYearFactory(BaseFactory):
    class Meta:
        model = models.EducationalYear

    adageId = factory.Sequence(lambda number: str(6 + number))
    beginningDate = factory.Sequence(
        lambda number: datetime.datetime(2020, 9, 1) + datetime.timedelta(days=365 * number)
    )
    expirationDate = factory.Sequence(
        lambda number: datetime.datetime(2021, 8, 31) + datetime.timedelta(days=365 * number)
    )


class EducationalDepositFactory(BaseFactory):
    class Meta:
        model = models.EducationalDeposit

    educationalInstitution = factory.SubFactory(EducationalInstitutionFactory)
    educationalYear = factory.SubFactory(EducationalYearFactory)
    amount = 3000
    dateCreated = datetime.datetime.now()
    isFinal = True


class EducationalRedactorFactory(BaseFactory):
    class Meta:
        model = models.EducationalRedactor

    email = factory.Sequence("reda.khteur{}@example.com".format)
    firstName = "Reda"
    lastName = "Khteur"
    civility = "M."


class EducationalBookingFactory(BaseFactory):
    class Meta:
        model = models.EducationalBooking

    confirmationLimitDate = datetime.datetime.utcnow()
    educationalInstitution = factory.SubFactory(EducationalInstitutionFactory)
    educationalYear = factory.SubFactory(EducationalYearFactory)
    educationalRedactor = factory.SubFactory(EducationalRedactorFactory)
