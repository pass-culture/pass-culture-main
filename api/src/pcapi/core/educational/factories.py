import datetime
import re
import typing

from dateutil.relativedelta import relativedelta
import factory

from pcapi.core.categories.subcategories_v2 import COLLECTIVE_SUBCATEGORIES
from pcapi.core.educational import models
from pcapi.core.educational import utils
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
from pcapi.core.factories import BaseFactory
import pcapi.core.offerers.factories as offerers_factories
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils import db as db_utils


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
    bookingEmails = ["collectiveofferfactory+booking@example.com", "collectiveofferfactory+booking@example2.com"]
    contactPhone = "+33199006328"
    offerVenue = {
        "addressType": "other",
        "otherAddress": "1 rue des polissons, Paris 75017",
        "venueId": None,
    }
    interventionArea = ["93", "94", "95"]

    @classmethod
    def _create(
        cls,
        model_class: type[models.CollectiveOffer],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.CollectiveOffer:
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
    contactUrl = None
    contactForm = models.OfferContactFormEnum.FORM
    offerVenue = {
        "addressType": "other",
        "otherAddress": "1 rue des polissons, Paris 75017",
        "venueId": None,
    }
    interventionArea = ["2A", "2B"]
    dateRange = db_utils.make_timerange(
        start=datetime.datetime.utcnow() + datetime.timedelta(days=1),
        end=datetime.datetime.utcnow() + datetime.timedelta(days=7),
    )

    @classmethod
    def _create(
        cls,
        model_class: type[models.CollectiveOfferTemplate],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.CollectiveOfferTemplate:
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

    @factory.post_generation
    def template(
        self, create: bool, extracted: models.CollectiveOfferTemplate, **kwargs: dict
    ) -> models.CollectiveOfferTemplate | None:
        if not create:
            return None
        template = extracted
        if not template:
            return None
        self.venue = template.venue
        return CollectiveOfferTemplateFactory()


class CollectiveStockFactory(BaseFactory):
    class Meta:
        model = models.CollectiveStock

    collectiveOffer = factory.SubFactory(CollectiveOfferFactory)
    beginningDatetime = factory.LazyFunction(lambda: datetime.datetime.utcnow() + datetime.timedelta(days=1))
    startDatetime = factory.LazyAttribute(lambda o: o.beginningDatetime)
    endDatetime = factory.LazyAttribute(lambda o: o.beginningDatetime)
    bookingLimitDatetime = factory.LazyAttribute(lambda stock: stock.beginningDatetime - datetime.timedelta(minutes=60))
    dateCreated = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=3))
    dateModified = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1))
    numberOfTickets = 25
    price = 100


def _institution_email_builder(institution: models.EducationalInstitution) -> str:
    name = institution.name if institution.name else institution.institutionType
    name = re.sub(r"\W", "-", name.lower().strip())

    city = re.sub(r"\W", "-", institution.city.lower().strip())

    return f"{name}@{city}.fr"


class EducationalInstitutionFactory(BaseFactory):
    class Meta:
        model = models.EducationalInstitution

    institutionId = factory.Sequence(lambda x: f"{x+1}470009E")
    name = factory.Sequence("DE LA TOUR{}".format)
    city = "PARIS"
    postalCode = "75000"
    email = factory.LazyAttribute(_institution_email_builder)
    phoneNumber = "0600000000"
    institutionType = "COLLEGE"


class EducationalYearFactory(BaseFactory):
    class Meta:
        model = models.EducationalYear

    adageId = factory.Sequence(lambda number: str(_get_current_educational_year_adage_id() + number))
    beginningDate = factory.Sequence(
        lambda number: datetime.datetime(_get_current_educational_year(), 9, 1) + relativedelta(years=number)
    )
    expirationDate = factory.Sequence(
        lambda number: datetime.datetime(_get_current_educational_year() + 1, 8, 31, 23, 59)
        + relativedelta(years=number),
    )


def _get_current_educational_year() -> int:
    current_date = datetime.datetime.utcnow()
    current_year = current_date.year
    current_month = current_date.month
    current_educational_year = current_year

    if 1 <= current_month < 9:
        current_educational_year = current_year - 1

    return current_educational_year


class EducationalCurrentYearFactory(EducationalYearFactory):
    beginningDate = datetime.datetime(_get_current_educational_year(), 9, 1)
    expirationDate = datetime.datetime(_get_current_educational_year() + 1, 8, 31, 23, 59, 59)


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


class CollectiveDmsApplicationWithNoVenueFactory(BaseFactory):
    class Meta:
        model = models.CollectiveDmsApplication

    siret = "00000000000001"
    state = "en_construction"
    procedure = 1  # could be any positive integer
    application = factory.Sequence(int)
    lastChangeDate = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    depositDate = datetime.datetime.utcnow() - datetime.timedelta(days=10)
    expirationDate = datetime.datetime.utcnow() + datetime.timedelta(days=365)
    buildDate = factory.SelfAttribute("lastChangeDate")


class CollectiveDmsApplicationFactory(CollectiveDmsApplicationWithNoVenueFactory):
    class Meta:
        model = models.CollectiveDmsApplication

    venue = factory.SubFactory(offerers_factories.VenueFactory)
    siret = factory.SelfAttribute("venue.siret")


class CollectiveOfferRequestFactory(BaseFactory):
    class Meta:
        model = models.CollectiveOfferRequest

    comment = "Un commentaire sublime"
    educationalRedactor = factory.SubFactory(EducationalRedactorFactory)
    educationalInstitution = factory.SubFactory(EducationalInstitutionFactory)
    collectiveOfferTemplate = factory.SubFactory(CollectiveOfferTemplateFactory)


class NationalProgramFactory(BaseFactory):
    class Meta:
        model = models.NationalProgram

    name = factory.Sequence("Dispositif national {}".format)


class EducationalRedactorWithFavoriteCollectiveOffer(EducationalRedactorFactory):
    favoriteCollectiveOffers = factory.List([factory.SubFactory(CollectiveOfferFactory)])


class EducationalRedactorWithFavoriteCollectiveOfferTemplate(EducationalRedactorFactory):
    favoriteCollectiveOfferTemplates = factory.List([factory.SubFactory(CollectiveOfferTemplateFactory)])


class EducationalInstitutionProgramFactory(BaseFactory):
    class Meta:
        model = models.EducationalInstitutionProgram
        sqlalchemy_get_or_create = ["name"]

    # some programs are inserted by default.
    # since the id sequence starts at 0, this will trigger a unique
    # constraint error.
    id = factory.Sequence(lambda n: n + 1_000)
    name = factory.Sequence("Program {}".format)


class PlaylistFactory(BaseFactory):
    class Meta:
        model = models.CollectivePlaylist

    type = models.PlaylistType.CLASSROOM
    institution = factory.SubFactory(EducationalInstitutionFactory)
    collective_offer_template = factory.SubFactory(CollectiveOfferTemplateFactory)
    venue = factory.SubFactory(offerers_factories.VenueFactory)


class AdageVenueAddressFactory(BaseFactory):
    class Meta:
        model = models.AdageVenueAddress

    venue = factory.SubFactory(offerers_factories.CollectiveVenueFactory)
    adageId = factory.LazyAttribute(lambda ava: ava.venue.adageId)
    adageInscriptionDate = factory.LazyAttribute(lambda ava: ava.venue.adageInscriptionDate)


class NotImplementedStatus(BaseException):
    pass


def create_collective_offer_by_status(
    status: CollectiveOfferDisplayedStatus,
    **kwargs: typing.Any,
) -> models.CollectiveOffer:
    match status.value:
        case CollectiveOfferDisplayedStatus.ARCHIVED.value:
            kwargs["dateArchived"] = datetime.datetime.utcnow()
            return CollectiveOfferFactory(**kwargs)
        case CollectiveOfferDisplayedStatus.REJECTED.value:
            kwargs["validation"] = OfferValidationStatus.REJECTED
            return CollectiveOfferFactory(**kwargs)
        case CollectiveOfferDisplayedStatus.PENDING.value:
            kwargs["validation"] = OfferValidationStatus.PENDING
            return CollectiveOfferFactory(**kwargs)
        case CollectiveOfferDisplayedStatus.ACTIVE.value:
            return CollectiveOfferFactory(**kwargs)
        case CollectiveOfferDisplayedStatus.INACTIVE.value:
            kwargs["isActive"] = False
            return CollectiveOfferFactory(**kwargs)
        case CollectiveOfferDisplayedStatus.EXPIRED.value:
            kwargs["validation"] = OfferValidationStatus.APPROVED
            offer = CollectiveOfferFactory(**kwargs)
            yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)

            stock = CollectiveStockFactory(beginningDatetime=yesterday, collectiveOffer=offer)
            PendingCollectiveBookingFactory(collectiveStock=stock)
            return offer

        case CollectiveOfferDisplayedStatus.PREBOOKED.value:
            offer = CollectiveOfferFactory(**kwargs)

            tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            stock = CollectiveStockFactory(beginningDatetime=tomorrow, collectiveOffer=offer)
            _booking = PendingCollectiveBookingFactory(collectiveStock=stock)
            return offer
        case CollectiveOfferDisplayedStatus.BOOKED.value:
            offer = CollectiveOfferFactory(**kwargs)

            tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            stock = CollectiveStockFactory(beginningDatetime=tomorrow, collectiveOffer=offer)
            _booking = ConfirmedCollectiveBookingFactory(collectiveStock=stock)
            return offer
        case CollectiveOfferDisplayedStatus.ENDED.value:
            offer = CollectiveOfferFactory(**kwargs)
            yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
            stock = CollectiveStockFactory(collectiveOffer=offer, beginningDatetime=yesterday)
            _booking = UsedCollectiveBookingFactory(collectiveStock=stock)
            return offer

        case CollectiveOfferDisplayedStatus.REIMBURSED.value:
            offer = CollectiveOfferFactory(**kwargs)
            yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
            stock = CollectiveStockFactory(collectiveOffer=offer, beginningDatetime=yesterday)
            _booking = ReimbursedCollectiveBookingFactory(collectiveStock=stock)
            return offer

    raise NotImplementedStatus(f"Factory for {status}")
