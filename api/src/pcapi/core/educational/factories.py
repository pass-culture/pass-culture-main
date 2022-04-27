import datetime

from dateutil.relativedelta import relativedelta
import factory

from pcapi.core.categories.subcategories import COLLECTIVE_SUBCATEGORIES
from pcapi.core.educational import api
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import BaseFactory
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus

from . import models
from .models import EducationalBookingStatus
from .models import Ministry
from .models import StudentLevels


ADAGE_STARTING_EDUCATIONAL_YEAR = 2014


class CollectiveOfferFactory(BaseFactory):
    class Meta:
        model = models.CollectiveOffer

    subcategoryId = factory.Iterator(COLLECTIVE_SUBCATEGORIES)
    name = factory.Sequence("CollectiveOffer {}".format)
    description = factory.Sequence("A passionate description of collectiveoffer {}".format)
    venue = factory.SubFactory(offerers_factories.VenueFactory)
    audioDisabilityCompliant = False
    mentalDisabilityCompliant = False
    motorDisabilityCompliant = False
    visualDisabilityCompliant = False
    dateCreated = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=5))
    students = [StudentLevels.GENERAL2]
    contactEmail = "collectiveofferfactory+contact@example.com"
    bookingEmail = "collectiveofferfactory+booking@example.com"
    contactPhone = "+33199006328"
    offerVenue = {
        "addressType": "other",
        "otherAddress": "1 rue des polissons, Paris 75017",
        "venueId": "",
    }

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        if kwargs.get("isActive") is None:
            kwargs["isActive"] = kwargs.get("validation") not in (
                OfferValidationStatus.REJECTED,
                OfferValidationStatus.PENDING,
            )

        return super()._create(model_class, *args, **kwargs)


class CollectiveOfferTemplateFactory(BaseFactory):
    class Meta:
        model = models.CollectiveOfferTemplate

    subcategoryId = factory.Iterator(COLLECTIVE_SUBCATEGORIES)
    name = factory.Sequence("CollectiveOffer {}".format)
    description = factory.Sequence("A passionate description of collectiveoffer {}".format)
    venue = factory.SubFactory(offerers_factories.VenueFactory)
    audioDisabilityCompliant = False
    mentalDisabilityCompliant = False
    motorDisabilityCompliant = False
    visualDisabilityCompliant = False

    dateCreated = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=5))
    students = [StudentLevels.GENERAL2]
    contactEmail = "collectiveofferfactory+contact@example.com"
    contactPhone = "+33199006328"
    offerVenue = {
        "addressType": "other",
        "otherAddress": "1 rue des polissons, Paris 75017",
        "venueId": "",
    }

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        if kwargs.get("isActive") is None:
            kwargs["isActive"] = kwargs.get("validation") not in (
                OfferValidationStatus.REJECTED,
                OfferValidationStatus.PENDING,
            )

        return super()._create(model_class, *args, **kwargs)


class CollectiveStockFactory(BaseFactory):
    class Meta:
        model = models.CollectiveStock

    collectiveOffer = factory.SubFactory(CollectiveOfferFactory)
    beginningDatetime = factory.LazyFunction(lambda: datetime.datetime.utcnow() + datetime.timedelta(days=1))
    bookingLimitDatetime = factory.LazyAttribute(lambda stock: stock.beginningDatetime - datetime.timedelta(minutes=60))
    dateCreated = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=3))
    dateModified = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1))
    numberOfTickets = 25
    price = 100


class EducationalInstitutionFactory(BaseFactory):
    class Meta:
        model = models.EducationalInstitution

    institutionId = factory.Sequence("{}470009E".format)
    name = factory.Sequence("Collège de la tour{}".format)
    city = "Paris"
    postalCode = "75000"
    email = "contact+collegelatour@example.com"
    phoneNumber = None


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
    isFinal = True
    ministry = Ministry.EDUCATION_NATIONALE.name


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


class PendingEducationalBookingFactory(EducationalBookingFactory):
    status = None
    confirmationLimitDate = datetime.datetime.utcnow() + datetime.timedelta(days=15)


class RefusedEducationalBookingFactory(EducationalBookingFactory):
    status = EducationalBookingStatus.REFUSED


class CollectiveBookingFactory(BaseFactory):
    class Meta:
        model = models.CollectiveBooking

    collectiveStock = factory.SubFactory(CollectiveStockFactory)
    dateCreated = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=2))
    venue = factory.SubFactory(offerers_factories.VenueFactory)
    offerer = factory.SubFactory(offerers_factories.OffererFactory)
    cancellationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1))
    confirmationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1))
    educationalInstitution = factory.SubFactory(EducationalInstitutionFactory)
    educationalYear = factory.SubFactory(EducationalYearFactory)
    educationalRedactor = factory.SubFactory(EducationalRedactorFactory)
    collectiveStock = factory.SubFactory(CollectiveStockFactory)
    confirmationDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1))

    @factory.post_generation
    def cancellation_limit_date(self, create, extracted, **kwargs):  # type: ignore [no-untyped-def]
        if extracted:
            self.cancellationLimitDate = extracted
        else:
            self.cancellationLimitDate = api.compute_educational_booking_cancellation_limit_date(
                self.collectiveStock.beginningDatetime, self.dateCreated
            )
        db.session.add(self)
        db.session.commit()

    @factory.post_generation
    def cancellation_date(self, create, extracted, **kwargs):  # type: ignore [no-untyped-def]
        # the public.save_cancellation_date() psql trigger overrides the extracted cancellationDate
        if extracted:
            self.cancellationDate = extracted
            db.session.add(self)
            db.session.flush()

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        kwargs["venue"] = kwargs["collectiveStock"].collectiveOffer.venue
        kwargs["offerer"] = kwargs["collectiveStock"].collectiveOffer.venue.managingOfferer
        return super()._create(model_class, *args, **kwargs)


class CancelledCollectiveBookingFactory(CollectiveBookingFactory):
    status = models.CollectiveBookingStatus.CANCELLED
    cancellationDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(hours=1))


class PendingCollectiveBookingFactory(CollectiveBookingFactory):
    cancellationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() + datetime.timedelta(days=10))
    confirmationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=10))
    status = models.CollectiveBookingStatus.PENDING


class UsedCollectiveBookingFactory(CollectiveBookingFactory):
    status = models.CollectiveBookingStatus.USED
    dateUsed = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=5))
    dateCreated = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=20))
    cancellationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=8))
    confirmationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=12))
    confirmationDate = None


class ReimbursedCollectiveBookingFactory(UsedCollectiveBookingFactory):
    status = models.CollectiveBookingStatus.REIMBURSED
    reimbursementDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1))
