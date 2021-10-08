import datetime

from dateutil.relativedelta import relativedelta
import factory

from pcapi.core.testing import BaseFactory

from . import models
from .models import EducationalBookingStatus


ADAGE_STARTING_EDUCATIONAL_YEAR = 2014


class EducationalInstitutionFactory(BaseFactory):
    class Meta:
        model = models.EducationalInstitution

    institutionId = factory.Sequence("{}470009E".format)


class EducationalYearFactory(BaseFactory):
    class Meta:
        model = models.EducationalYear

    adageId = factory.Sequence(lambda number: str(_get_current_educational_year_adage_id() + number))
    beginningDate = factory.Sequence(
        lambda number: datetime.datetime(_get_current_educational_year(), 9, 1) + relativedelta(years=number)
    )
    expirationDate = factory.Sequence(
        lambda number: datetime.datetime(_get_current_educational_year() + 1, 8, 31) + relativedelta(years=number)
    )


def _get_current_educational_year() -> int:
    current_date = datetime.datetime.utcnow()
    current_year = current_date.year
    current_month = current_date.month
    current_educational_year = current_year

    if 1 <= current_month < 9:
        current_educational_year = current_year - 1

    return current_educational_year


def _get_current_educational_year_adage_id() -> int:
    return _get_current_educational_year() - ADAGE_STARTING_EDUCATIONAL_YEAR


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


class UsedEducationalBookingFactory(EducationalBookingFactory):
    status = EducationalBookingStatus.USED_BY_INSTITUTE


class PendingEducationalBookingFactory(EducationalBookingFactory):
    status = None
    confirmationLimitDate = datetime.datetime.utcnow() + datetime.timedelta(days=15)
