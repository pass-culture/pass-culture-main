import datetime
import re
import typing

from dateutil.relativedelta import relativedelta
import factory

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import constants
from pcapi.core.educational import models
from pcapi.core.educational import utils
from pcapi.core.factories import BaseFactory
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils import db as db_utils


ADAGE_STARTING_EDUCATIONAL_YEAR = 2014


class EducationalDomainFactory(BaseFactory):
    class Meta:
        model = models.EducationalDomain

    name = "Architecture"


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
    latitude = 48.8566
    longitude = 2.3522


class CollectiveOfferFactory(BaseFactory):
    class Meta:
        model = models.CollectiveOffer

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
    formats = [EacFormat.PROJECTION_AUDIOVISUELLE]

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
    contactUrl: str | None = None
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
    formats = [EacFormat.PROJECTION_AUDIOVISUELLE]

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
            self.domains = [EducationalDomainFactory.create(name="Danse", collectiveOfferTemplates=[self])]

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
        return CollectiveOfferTemplateFactory.create()


class CollectiveStockFactory(BaseFactory):
    class Meta:
        model = models.CollectiveStock

    collectiveOffer = factory.SubFactory(CollectiveOfferFactory)
    startDatetime = factory.LazyFunction(lambda: datetime.datetime.utcnow() + datetime.timedelta(days=1))
    endDatetime = factory.LazyAttribute(lambda o: o.startDatetime)
    bookingLimitDatetime = factory.LazyAttribute(lambda stock: stock.startDatetime - datetime.timedelta(minutes=60))
    dateCreated = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=3))
    dateModified = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1))
    numberOfTickets = 25
    price = 100
    priceDetail = factory.LazyAttribute(lambda stock: f"Prix: {stock.price}€ pour {stock.numberOfTickets} tickets")


class EducationalYearFactory(BaseFactory):
    class Meta:
        model = models.EducationalYear

    adageId: factory.declarations.BaseDeclaration = factory.Sequence(
        lambda number: str(_get_current_educational_year_adage_id() + number)
    )
    beginningDate: factory.declarations.BaseDeclaration = factory.Sequence(
        lambda number: datetime.datetime(_get_current_educational_year(), 9, 1) + relativedelta(years=number)
    )
    expirationDate: factory.declarations.BaseDeclaration = factory.Sequence(
        lambda number: datetime.datetime(_get_current_educational_year() + 1, 8, 31, 23, 59)
        + relativedelta(years=number),
    )


def _get_educational_year_beginning(date_time: datetime.datetime) -> int:
    if 1 <= date_time.month < 9:
        return date_time.year - 1

    return date_time.year


def _get_current_educational_year() -> int:
    current_date = datetime.datetime.utcnow()

    return _get_educational_year_beginning(current_date)


def create_educational_year(date_time: datetime.datetime) -> models.EducationalYear:
    beginning_year = _get_educational_year_beginning(date_time)
    adage_id = beginning_year - ADAGE_STARTING_EDUCATIONAL_YEAR

    return EducationalYearFactory.create(
        beginningDate=datetime.datetime(beginning_year, 9, 1),
        expirationDate=datetime.datetime(beginning_year + 1, 8, 31, 23, 59, 59),
        adageId=adage_id,
    )


def _get_current_educational_year_adage_id() -> int:
    return _get_current_educational_year() - ADAGE_STARTING_EDUCATIONAL_YEAR


class EducationalCurrentYearFactory(EducationalYearFactory):
    beginningDate = factory.LazyFunction(lambda: datetime.datetime(_get_current_educational_year(), 9, 1))
    expirationDate = factory.LazyFunction(
        lambda: datetime.datetime(_get_current_educational_year() + 1, 8, 31, 23, 59, 59)
    )
    adageId = factory.LazyFunction(_get_current_educational_year_adage_id)


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
    cancellationLimitDate: factory.declarations.BaseDeclaration = factory.LazyAttribute(
        lambda self: utils.compute_educational_booking_cancellation_limit_date(
            self.collectiveStock.startDatetime, self.dateCreated
        )
    )
    confirmationLimitDate: factory.declarations.BaseDeclaration = factory.LazyFunction(
        lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1)
    )
    educationalInstitution = factory.SubFactory(EducationalInstitutionFactory)
    educationalYear = factory.SubFactory(EducationalYearFactory)
    educationalRedactor = factory.SubFactory(EducationalRedactorFactory)
    confirmationDate: factory.declarations.BaseDeclaration | None = factory.LazyFunction(
        lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1)
    )


class CancelledCollectiveBookingFactory(CollectiveBookingFactory):
    status = models.CollectiveBookingStatus.CANCELLED
    cancellationDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(hours=1))
    cancellationReason = factory.Iterator(models.CollectiveBookingCancellationReasons)


class PendingCollectiveBookingFactory(CollectiveBookingFactory):
    cancellationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() + datetime.timedelta(days=10))
    confirmationLimitDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() + datetime.timedelta(days=10))
    confirmationDate = None
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

    siret: str | factory.declarations.BaseDeclaration = "00000000000001"
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


class DomainToNationalProgramFactory(BaseFactory):
    class Meta:
        model = models.DomainToNationalProgram


class EducationalRedactorWithFavoriteCollectiveOfferTemplateFactory(EducationalRedactorFactory):
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


class EducationalInstitutionProgramAssociationFactory(BaseFactory):
    class Meta:
        model = models.EducationalInstitutionProgramAssociation
        sqlalchemy_get_or_create = ["institution", "program"]

    institution = factory.SubFactory(EducationalInstitutionFactory)
    program = factory.SubFactory(EducationalInstitutionProgramFactory)
    timespan = db_utils.make_timerange(start=constants.MEG_BEGINNING_DATE, end=None)


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


class CollectiveOfferBaseFactory(CollectiveOfferFactory):
    institution = factory.SubFactory(EducationalInstitutionFactory)


class ArchivedCollectiveOfferFactory(CollectiveOfferBaseFactory):
    isActive = False
    dateArchived = factory.LazyFunction(datetime.datetime.utcnow)


class RejectedCollectiveOfferFactory(CollectiveOfferBaseFactory):
    validation = OfferValidationStatus.REJECTED
    isActive = False

    @factory.post_generation
    def create_stock(self, _create: bool, _extracted: typing.Any, **_kwargs: typing.Any) -> None:
        # a rejected offer has a stock because it completed the creation process
        CollectiveStockFactory.create(
            startDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=10), collectiveOffer=self
        )


class UnderReviewCollectiveOfferFactory(CollectiveOfferBaseFactory):
    validation = OfferValidationStatus.PENDING
    isActive = False

    @factory.post_generation
    def create_stock(self, _create: bool, _extracted: typing.Any, **_kwargs: typing.Any) -> None:
        # an offer under review has a stock because it completed the creation process
        CollectiveStockFactory.create(
            startDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=10), collectiveOffer=self
        )


class DraftCollectiveOfferFactory(CollectiveOfferBaseFactory):
    validation = OfferValidationStatus.DRAFT
    isActive = False


class PublishedCollectiveOfferFactory(CollectiveOfferBaseFactory):
    validation = OfferValidationStatus.APPROVED

    @factory.post_generation
    def create_stock(self, _create: bool, _extracted: typing.Any, **_kwargs: typing.Any) -> None:
        future = datetime.datetime.utcnow() + datetime.timedelta(days=10)
        CollectiveStockFactory.create(startDatetime=future, collectiveOffer=self)


class HiddenCollectiveOfferFactory(CollectiveOfferBaseFactory):
    isActive = False


class ExpiredWithoutBookingCollectiveOfferFactory(CollectiveOfferBaseFactory):
    validation = OfferValidationStatus.APPROVED

    @factory.post_generation
    def create_expired_stock(self, _create: bool, _extracted: typing.Any, **_kwargs: typing.Any) -> None:
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        CollectiveStockFactory.create(bookingLimitDatetime=yesterday, collectiveOffer=self)


class ExpiredWithBookingCollectiveOfferFactory(CollectiveOfferBaseFactory):
    validation = OfferValidationStatus.APPROVED

    @factory.post_generation
    def create_expired_stock(self, _create: bool, _extracted: typing.Any, **_kwargs: typing.Any) -> None:
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        stock = CollectiveStockFactory.create(bookingLimitDatetime=yesterday, collectiveOffer=self)
        PendingCollectiveBookingFactory.create(collectiveStock=stock)


class PrebookedCollectiveOfferFactory(CollectiveOfferBaseFactory):
    @factory.post_generation
    def create_prebooked_stock(self, _create: bool, _extracted: typing.Any, **_kwargs: typing.Any) -> None:
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        stock = CollectiveStockFactory.create(startDatetime=tomorrow, collectiveOffer=self)
        PendingCollectiveBookingFactory.create(collectiveStock=stock)


class CancelledWithoutBookingCollectiveOfferFactory(CollectiveOfferBaseFactory):
    @factory.post_generation
    def create_cancelled_stock(self, _create: bool, _extracted: typing.Any, **_kwargs: typing.Any) -> None:
        in_past = datetime.datetime.utcnow() - datetime.timedelta(days=4)
        CollectiveStockFactory.create(startDatetime=in_past, collectiveOffer=self)


class CancelledWithBookingCollectiveOfferFactory(CollectiveOfferBaseFactory):
    @factory.post_generation
    def create_cancelled_stock(self, _create: bool, _extracted: typing.Any, **_kwargs: typing.Any) -> None:
        in_past = datetime.datetime.utcnow() - datetime.timedelta(days=4)
        stock = CollectiveStockFactory.create(startDatetime=in_past, collectiveOffer=self)
        CancelledCollectiveBookingFactory.create(
            collectiveStock=stock, cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER
        )


class CancelledDueToExpirationCollectiveOfferFactory(CollectiveOfferBaseFactory):
    @factory.post_generation
    def create_cancelled_stock(self, _create: bool, _extracted: typing.Any, **_kwargs: typing.Any) -> None:
        in_past = datetime.datetime.utcnow() - datetime.timedelta(days=4)
        stock = CollectiveStockFactory.create(startDatetime=in_past, collectiveOffer=self)
        CancelledCollectiveBookingFactory.create(
            collectiveStock=stock, cancellationReason=models.CollectiveBookingCancellationReasons.EXPIRED
        )


class BookedCollectiveOfferFactory(CollectiveOfferBaseFactory):
    @factory.post_generation
    def create_booked_stock(self, _create: bool, _extracted: typing.Any, **_kwargs: typing.Any) -> None:
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        stock = CollectiveStockFactory.create(startDatetime=tomorrow, collectiveOffer=self)
        ConfirmedCollectiveBookingFactory.create(collectiveStock=stock)


class EndedCollectiveOfferFactory(CollectiveOfferBaseFactory):
    @factory.post_generation
    def booking_is_confirmed(self, _create: bool, booking_is_confirmed: bool = False, **kwargs: typing.Any) -> None:
        if booking_is_confirmed:
            yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        else:
            yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=3)

        stock = CollectiveStockFactory.create(startDatetime=yesterday, collectiveOffer=self)

        if booking_is_confirmed:
            ConfirmedCollectiveBookingFactory.create(collectiveStock=stock)
        else:
            UsedCollectiveBookingFactory.create(collectiveStock=stock)


class ReimbursedCollectiveOfferFactory(CollectiveOfferBaseFactory):
    @factory.post_generation
    def create_reimbursed_stock(self, _create: bool, _extracted: typing.Any, **_kwargs: typing.Any) -> None:
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        stock = CollectiveStockFactory.create(startDatetime=yesterday, collectiveOffer=self)
        ReimbursedCollectiveBookingFactory.create(collectiveStock=stock)


def create_collective_offer_by_status(
    status: models.CollectiveOfferDisplayedStatus,
    **kwargs: typing.Any,
) -> models.CollectiveOffer:
    match status:
        case models.CollectiveOfferDisplayedStatus.ARCHIVED:
            return ArchivedCollectiveOfferFactory.create(**kwargs)
        case models.CollectiveOfferDisplayedStatus.REJECTED:
            return RejectedCollectiveOfferFactory.create(**kwargs)
        case models.CollectiveOfferDisplayedStatus.UNDER_REVIEW:
            return UnderReviewCollectiveOfferFactory.create(**kwargs)
        case models.CollectiveOfferDisplayedStatus.PUBLISHED:
            return PublishedCollectiveOfferFactory.create(**kwargs)
        case models.CollectiveOfferDisplayedStatus.HIDDEN:
            return HiddenCollectiveOfferFactory.create(**kwargs)
        case models.CollectiveOfferDisplayedStatus.EXPIRED:
            return ExpiredWithBookingCollectiveOfferFactory.create(**kwargs)
        case models.CollectiveOfferDisplayedStatus.PREBOOKED:
            return PrebookedCollectiveOfferFactory.create(**kwargs)
        case models.CollectiveOfferDisplayedStatus.CANCELLED:
            return CancelledWithoutBookingCollectiveOfferFactory.create(**kwargs)
        case models.CollectiveOfferDisplayedStatus.BOOKED:
            return BookedCollectiveOfferFactory.create(**kwargs)
        case models.CollectiveOfferDisplayedStatus.ENDED:
            return EndedCollectiveOfferFactory.create(**kwargs)
        case models.CollectiveOfferDisplayedStatus.REIMBURSED:
            return ReimbursedCollectiveOfferFactory.create(**kwargs)
        case models.CollectiveOfferDisplayedStatus.DRAFT:
            return DraftCollectiveOfferFactory.create(**kwargs)
        case _:
            raise ValueError(f"No factory for collective offer status {status}")


def create_collective_offer_template_by_status(
    status: models.CollectiveOfferDisplayedStatus,
    **kwargs: typing.Any,
) -> models.CollectiveOfferTemplate:
    match status:
        case models.CollectiveOfferDisplayedStatus.ARCHIVED:
            kwargs.update({"isActive": False, "dateArchived": datetime.datetime.utcnow()})
            return CollectiveOfferTemplateFactory.create(**kwargs)

        case models.CollectiveOfferDisplayedStatus.REJECTED:
            kwargs["validation"] = OfferValidationStatus.REJECTED
            kwargs["rejectionReason"] = models.CollectiveOfferRejectionReason.MISSING_PRICE
            return CollectiveOfferTemplateFactory.create(**kwargs)

        case models.CollectiveOfferDisplayedStatus.UNDER_REVIEW:
            kwargs["validation"] = OfferValidationStatus.PENDING
            return CollectiveOfferTemplateFactory.create(**kwargs)

        case models.CollectiveOfferDisplayedStatus.DRAFT:
            kwargs["validation"] = OfferValidationStatus.DRAFT
            return CollectiveOfferTemplateFactory.create(**kwargs)

        case models.CollectiveOfferDisplayedStatus.HIDDEN:
            kwargs["isActive"] = False
            return CollectiveOfferTemplateFactory.create(**kwargs)

        case models.CollectiveOfferDisplayedStatus.PUBLISHED:
            return CollectiveOfferTemplateFactory.create(**kwargs)

        case models.CollectiveOfferDisplayedStatus.ENDED:
            now = datetime.datetime.utcnow()
            start = now - datetime.timedelta(days=14)
            date_range = db_utils.make_timerange(start=start, end=now - datetime.timedelta(days=7))
            return CollectiveOfferTemplateFactory.create(**kwargs, dateRange=date_range, dateCreated=start)

    raise ValueError(f"No factory for collective offer status {status}")


def create_collective_booking_by_status(
    status: models.CollectiveBookingStatus, **kwargs: typing.Any
) -> models.CollectiveBooking:
    match status:
        case models.CollectiveBookingStatus.PENDING:
            return PendingCollectiveBookingFactory.create(**kwargs)
        case models.CollectiveBookingStatus.CONFIRMED:
            return ConfirmedCollectiveBookingFactory.create(**kwargs)
        case models.CollectiveBookingStatus.USED:
            return UsedCollectiveBookingFactory.create(**kwargs)
        case models.CollectiveBookingStatus.CANCELLED:
            return CancelledCollectiveBookingFactory.create(**kwargs)
        case models.CollectiveBookingStatus.REIMBURSED:
            return ReimbursedCollectiveBookingFactory.create(**kwargs)

    raise ValueError(f"No factory for collective booking status {status}")
