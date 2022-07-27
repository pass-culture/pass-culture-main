import datetime

from dateutil.relativedelta import relativedelta
import factory

from pcapi.core.categories.subcategories import COLLECTIVE_SUBCATEGORIES
from pcapi.core.educational import models
from pcapi.core.educational import utils
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import BaseFactory
from pcapi.models.offer_mixin import OfferValidationStatus


ADAGE_STARTING_EDUCATIONAL_YEAR = 2014


class EducationalDomainFactory(BaseFactory):
    class Meta:
        model = models.EducationalDomain

    name = "Architecture"


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
    students = [models.StudentLevels.GENERAL2]
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

    @factory.post_generation
    def educational_domains(
        self,
        create: bool,
        extracted: list[models.EducationalDomain] | None = None,
    ) -> None:
        if not create or not extracted:
            return

        if extracted:
            domains = []
            for domain in extracted:
                domains.append(domain)
            self.domains = domains


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
    students = [models.StudentLevels.GENERAL2]
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

    @factory.post_generation
    def educational_domains(
        self,
        create: bool,
        extracted: list[models.EducationalDomain] | None = None,
    ) -> None:
        if not create or not extracted:
            self.domains = [EducationalDomainFactory(name="Danse", collectiveOfferTemplates=[self])]

        if extracted:
            domains = []
            for domain in extracted:
                domains.append(domain)
            self.domains = domains


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
    ministry = models.Ministry.EDUCATION_NATIONALE.name


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
    status = models.EducationalBookingStatus.REFUSED


class CollectiveBookingFactory(BaseFactory):
    class Meta:
        model = models.CollectiveBooking

    collectiveStock = factory.SubFactory(CollectiveStockFactory)
    dateCreated = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=2))
    offerer = factory.SelfAttribute("collectiveStock.collectiveOffer.venue.managingOfferer")
    venue = factory.SelfAttribute("collectiveStock.collectiveOffer.venue")
    cancellationLimitDate = factory.LazyAttribute(
        lambda self: utils.compute_educational_booking_cancellation_limit_date(
            self.collectiveStock.beginningDatetime, self.dateCreated
        )
    )
    confirmationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1))
    educationalInstitution = factory.SubFactory(EducationalInstitutionFactory)
    educationalYear = factory.SubFactory(EducationalYearFactory)
    educationalRedactor = factory.SubFactory(EducationalRedactorFactory)
    confirmationDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1))


class CancelledCollectiveBookingFactory(CollectiveBookingFactory):
    status = models.CollectiveBookingStatus.CANCELLED
    cancellationDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(hours=1))
    cancellationReason = factory.Iterator(models.CollectiveBookingCancellationReasons)


class PendingCollectiveBookingFactory(CollectiveBookingFactory):
    cancellationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() + datetime.timedelta(days=10))
    confirmationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() + datetime.timedelta(days=10))
    status = models.CollectiveBookingStatus.PENDING


class UsedCollectiveBookingFactory(CollectiveBookingFactory):
    status = models.CollectiveBookingStatus.USED
    dateUsed = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=5))
    dateCreated = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=20))
    confirmationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=12))
    confirmationDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=6))


class ReimbursedCollectiveBookingFactory(UsedCollectiveBookingFactory):
    status = models.CollectiveBookingStatus.REIMBURSED
    reimbursementDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1))


class ConfirmedCollectiveBookingFactory(CollectiveBookingFactory):
    status = models.CollectiveBookingStatus.CONFIRMED
    cancellationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1))
    confirmationDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1))
    confirmationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() + datetime.timedelta(days=1))
