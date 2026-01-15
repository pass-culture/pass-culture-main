import datetime
import decimal
import typing

import factory

import pcapi.core.educational.models as educational_models
import pcapi.core.geography.factories as geography_factories
import pcapi.core.users.factories as users_factories
from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.core.factories import BaseFactory
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import crypto
from pcapi.utils import date as date_utils
from pcapi.utils import siren as siren_utils
from pcapi.utils.date import timespan_str_to_numrange

from . import api
from . import models


if typing.TYPE_CHECKING:
    from pcapi.core.finance.models import BankAccount


OPENING_HOURS = [("10:00", "13:00"), ("14:00", "19:30")]


class OffererFactory(BaseFactory):
    class Meta:
        model = models.Offerer

    name = factory.Sequence("Le Petit Rintintin Management {}".format)
    siren = factory.Sequence(lambda n: siren_utils.complete_siren_or_siret(f"{n + 1:08}"))  # ensures valid format
    isActive = True
    validationStatus = ValidationStatus.VALIDATED
    allowedOnAdage = True


class NewOffererFactory(OffererFactory):
    validationStatus = ValidationStatus.NEW
    allowedOnAdage = False


class PendingOffererFactory(NewOffererFactory):
    validationStatus = ValidationStatus.PENDING


class RejectedOffererFactory(OffererFactory):
    validationStatus = ValidationStatus.REJECTED
    isActive = False


class ClosedOffererFactory(OffererFactory):
    validationStatus = ValidationStatus.CLOSED


class CaledonianOffererFactory(OffererFactory):
    name = factory.Sequence("Structure calédonienne {}".format)
    siren = factory.Sequence(lambda n: siren_utils.rid7_to_siren(f"2{n + 1:06}"))
    allowedOnAdage = False


class NotValidatedCaledonianOffererFactory(CaledonianOffererFactory):
    validationStatus = ValidationStatus.NEW


class CollectiveOffererFactory(OffererFactory):
    name = factory.Sequence("[EAC] La structure de Moz'Art {}".format)


class VenueFactory(BaseFactory):
    class Meta:
        model = models.Venue

    activity = factory.Maybe(
        "isOpenToPublic",
        yes_declaration=factory.Iterator(models.ActivityOpenToPublic),
        no_declaration=factory.Iterator(models.ActivityNotOpenToPublic),
    )
    name = factory.Sequence("Le Petit Rintintin {}".format)
    managingOfferer = factory.SubFactory(OffererFactory)
    publicName = factory.SelfAttribute("name")
    siret: factory.declarations.BaseDeclaration | None = factory.LazyAttributeSequence(
        lambda o, n: siren_utils.complete_siren_or_siret(f"{o.managingOfferer.siren}{n:04}")
    )
    isVirtual = False
    isPermanent: bool | factory.declarations.BaseDeclaration | None = factory.LazyAttribute(
        lambda o: o.venueTypeCode in models.PERMENANT_VENUE_TYPES
    )
    isOpenToPublic = factory.LazyAttribute(lambda o: o.isPermanent is True)
    venueTypeCode = models.VenueTypeCode.OTHER
    description = factory.Faker("text", max_nb_chars=64)
    audioDisabilityCompliant: bool | None = False
    mentalDisabilityCompliant: bool | None = False
    motorDisabilityCompliant: bool | None = False
    visualDisabilityCompliant: bool | None = False
    contact = factory.RelatedFactory("pcapi.core.offerers.factories.VenueContactFactory", factory_related_name="venue")
    bookingEmail = factory.Sequence("venue{}@example.net".format)
    dmsToken = factory.LazyFunction(api.generate_dms_token)
    _bannerUrl: str | None = None
    adageId: str | factory.declarations.BaseDeclaration | None = None

    offererAddress: factory.declarations.BaseDeclaration | None = factory.RelatedFactory(
        "pcapi.core.offerers.factories.VenueLocationFactory",
        factory_related_name="venue",
        address=factory.SubFactory("pcapi.core.geography.factories.AddressFactory"),
        offerer=factory.SelfAttribute("..managingOfferer"),
    )

    @factory.post_generation
    def pricing_point(
        self,
        create: bool,
        extracted: typing.Callable | None,
        **kwargs: typing.Any,
    ) -> models.VenuePricingPointLink | None:
        if not create:
            return None
        pricing_point: "VenueFactory | typing.Callable | None" = extracted
        if not pricing_point:
            return None
        if pricing_point == "self":
            pricing_point = self
        return VenuePricingPointLinkFactory.create(venue=self, pricingPoint=pricing_point)

    @factory.post_generation
    def bank_account(
        self, create: bool, extracted: "BankAccount | None", **kwargs: typing.Any
    ) -> models.VenueBankAccountLink | None:
        if not create:
            return None
        bank_account = extracted
        if not bank_account:
            return None
        return VenueBankAccountLinkFactory.create(venue=self, bankAccount=bank_account)

    @factory.post_generation
    def opening_hours(
        self, create: bool, extracted: list[models.OpeningHours] | None, **kwargs: typing.Any
    ) -> list[models.OpeningHours] | None:
        if not create:
            return None
        opening_hours = extracted
        if not opening_hours:
            opening_hours = []
        if self.isOpenToPublic:
            for weekday in models.Weekday:
                if weekday.value == "MONDAY":
                    timespan = timespan_str_to_numrange([OPENING_HOURS[1]])
                elif weekday.value != "SUNDAY":
                    timespan = timespan_str_to_numrange(OPENING_HOURS)
                else:
                    timespan = None
                opening_hours.append(
                    OpeningHoursFactory.create(venue=self, offer=None, weekday=weekday, timespan=timespan)
                )
        return opening_hours

    @factory.post_generation
    def collectiveDomains(
        self, create: bool, extracted: list[educational_models.EducationalDomain] | None, **kwargs: typing.Any
    ) -> list[educational_models.EducationalDomain]:
        if not create:
            return []
        if kwargs:
            raise ValueError(
                "`VenueFactory(collectiveDomains__*)` not allowed, please use explicit `VenueFactory(collectiveDomains=[EducationalDomainFactory()]`"
            )
        if not self.isOpenToPublic and extracted is None:
            extracted = db.session.query(educational_models.EducationalDomain).limit(1).all()
        if not self.isOpenToPublic and not extracted:
            import pcapi.core.educational.factories as educational_factories

            extracted = [educational_factories.EducationalDomainFactory()]
        self.collectiveDomains = extracted or []
        return extracted or []


class CaledonianVenueFactory(VenueFactory):
    name = factory.Sequence("Partenaire culturel calédonien {}".format)
    managingOfferer = factory.SubFactory(CaledonianOffererFactory)
    siret: factory.declarations.BaseDeclaration | None = factory.LazyAttributeSequence(
        lambda o, n: siren_utils.ridet_to_siret(f"{siren_utils.siren_to_rid7(o.managingOfferer.siren)}{n % 100:03}")
    )
    venueTypeCode = models.VenueTypeCode.BOOKSTORE
    adageId = None

    offererAddress: factory.declarations.BaseDeclaration | None = factory.RelatedFactory(
        "pcapi.core.offerers.factories.VenueLocationFactory",
        factory_related_name="venue",
        address=factory.SubFactory("pcapi.core.geography.factories.CaledonianAddressFactory"),
        offerer=factory.SelfAttribute("..managingOfferer"),
    )


class CollectiveVenueFactory(VenueFactory):
    venueTypeCode = models.VenueTypeCode.PERFORMING_ARTS

    isPermanent = True

    adageId = factory.Sequence(str)
    adageInscriptionDate = factory.LazyFunction(lambda: date_utils.get_naive_utc_now() - datetime.timedelta(days=365))

    managingOfferer = factory.SubFactory(CollectiveOffererFactory)

    name = factory.Sequence("[EAC] Le lieu de Moz'Art {}".format)

    collectiveDescription = factory.Sequence(
        "Une description passionnante à propos des lieux {}.\n Description multi-lignes avec des liens et mails:\n- Est-ce qu'on gère les liens ? ".format
    )

    collectiveInterventionArea = ["75", "92"]


class GooglePlacesInfoFactory(BaseFactory):
    class Meta:
        model = models.GooglePlacesInfo

    venue = factory.SubFactory(VenueFactory)
    placeId = factory.Sequence("ChIJd8BlQ2Bx5kcRwE0uQdK5P8U{}".format)
    bannerUrl = factory.Sequence(
        "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={}".format
    )
    bannerMeta: dict | None = None


class VenueWithoutSiretFactory(VenueFactory):
    siret = None
    comment = "No SIRET"


class CaledonianVenueWithoutRidetFactory(CaledonianVenueFactory):
    siret = None
    comment = "No RIDET"


class VenuePricingPointLinkFactory(BaseFactory):
    class Meta:
        model = models.VenuePricingPointLink

    venue = factory.SubFactory(VenueFactory)
    pricingPoint = factory.SubFactory(
        VenueFactory,
        managingOfferer=factory.SelfAttribute("..venue.managingOfferer"),
    )
    timespan = factory.LazyFunction(
        lambda: [
            date_utils.get_naive_utc_now() - datetime.timedelta(days=365),
            None,
        ]
    )


class VenueBankAccountLinkFactory(BaseFactory):
    class Meta:
        model = models.VenueBankAccountLink

    venue = factory.SubFactory(VenueFactory)
    bankAccount = factory.SubFactory(
        "pcapi.core.finance.factories.BankAccountFactory", offerer=factory.SelfAttribute("..venue.managingOfferer")
    )
    timespan = factory.LazyFunction(lambda: [date_utils.get_naive_utc_now() - datetime.timedelta(days=365), None])


class OpeningHoursFactory(BaseFactory):
    class Meta:
        model = models.OpeningHours

    # TODO(jbaudet::2025-07) make both optional and check that only one
    # is set at a time
    venue = factory.SubFactory(VenueFactory)
    offer: factory.SubFactory | None = None

    weekday = models.Weekday.MONDAY
    timespan = timespan_str_to_numrange(OPENING_HOURS)


class UserOffererFactory(BaseFactory):
    class Meta:
        model = models.UserOfferer

    user = factory.SubFactory(users_factories.ProFactory)
    offerer = factory.SubFactory(OffererFactory)
    validationStatus = ValidationStatus.VALIDATED


class NonAttachedUserOffererFactory(UserOffererFactory):
    user = factory.SubFactory(users_factories.NonAttachedProFactory)


class NewUserOffererFactory(NonAttachedUserOffererFactory):
    validationStatus = ValidationStatus.NEW


class PendingUserOffererFactory(NonAttachedUserOffererFactory):
    validationStatus = ValidationStatus.PENDING


class RejectedUserOffererFactory(NonAttachedUserOffererFactory):
    validationStatus = ValidationStatus.REJECTED


class DeletedUserOffererFactory(NonAttachedUserOffererFactory):
    validationStatus = ValidationStatus.DELETED


class UserNotValidatedOffererFactory(BaseFactory):
    class Meta:
        model = models.UserOfferer

    user = factory.SubFactory(users_factories.NonAttachedProFactory)
    offerer = factory.SubFactory(NewOffererFactory)
    validationStatus = ValidationStatus.VALIDATED


class VenueLabelFactory(BaseFactory):
    class Meta:
        model = models.VenueLabel

    label = "Cinéma d'art et d'essai"


class VenueContactFactory(BaseFactory):
    class Meta:
        model = models.VenueContact

    venue = factory.SubFactory(VenueFactory)
    email = "contact@venue.com"
    website = "https://my.website.com"
    phone_number = "+33102030405"
    social_medias = {"instagram": "http://instagram.com/@venue"}


def build_clear_api_key(prefix: str | None = None, secret: str | None = None) -> str:
    prefix = prefix if prefix else DEFAULT_PREFIX
    secret = secret if secret else DEFAULT_SECRET

    return f"{prefix}_{secret}"


DEFAULT_PREFIX = "development_prefix"
DEFAULT_SECRET = "clearSecret"
DEFAULT_CLEAR_API_KEY = build_clear_api_key()


class ApiKeyFactory(BaseFactory):
    class Meta:
        model = models.ApiKey

    prefix = DEFAULT_PREFIX

    @classmethod
    def _create(
        cls,
        model_class: type[models.ApiKey],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.ApiKey:
        kwargs["secret"] = crypto.hash_public_api_key(kwargs.get("secret", DEFAULT_SECRET))
        return super()._create(model_class, *args, **kwargs)


class OffererTagFactory(BaseFactory):
    class Meta:
        model = models.OffererTag

    name = factory.Sequence("OffererTag_{}".format)


class OffererTagCategoryFactory(BaseFactory):
    class Meta:
        model = models.OffererTagCategory

    name = factory.Sequence("offerer-tag-category-{}".format)


class OffererTagCategoryMappingFactory(BaseFactory):
    class Meta:
        model = models.OffererTagCategoryMapping


class OffererTagMappingFactory(BaseFactory):
    class Meta:
        model = models.OffererTagMapping


class VenueEducationalStatusFactory(BaseFactory):
    class Meta:
        model = models.VenueEducationalStatus

    id = factory.Sequence(int)
    name = factory.Sequence(lambda x: f"venue educational status {x}")


class VenueRegistrationFactory(BaseFactory):
    class Meta:
        model = models.VenueRegistration

    venue = factory.SubFactory(VenueFactory)
    target = models.Target.INDIVIDUAL_AND_EDUCATIONAL
    webPresence = "https://example.com, https://pass.culture.fr"


class OffererInvitationFactory(BaseFactory):
    class Meta:
        model = models.OffererInvitation

    offerer = factory.SubFactory(OffererFactory)
    email = factory.Sequence("invited.pro{}@example.net".format)
    dateCreated = date_utils.get_naive_utc_now()
    user = factory.SubFactory(users_factories.ProFactory)
    status = models.InvitationStatus.PENDING


class IndividualOffererSubscriptionFactory(BaseFactory):
    class Meta:
        model = models.IndividualOffererSubscription

    offerer = factory.SubFactory(NewOffererFactory)
    isEmailSent = True
    dateEmailSent = factory.LazyFunction(lambda: datetime.date.today() - datetime.timedelta(days=3))
    dateReminderEmailSent: datetime.datetime | None = None


class OffererStatsFactory(BaseFactory):
    class Meta:
        model = models.OffererStats

    syncDate = factory.LazyFunction(lambda: datetime.date.today() - datetime.timedelta(hours=3))


class AccessibilityProviderFactory(BaseFactory):
    class Meta:
        model = models.AccessibilityProvider

    venue = factory.SubFactory(VenueFactory)
    externalAccessibilityId = factory.Sequence("slug-d-accessibilite-{}".format)
    externalAccessibilityData = {
        "access_modality": [acceslibre_enum.EXTERIOR_ACCESS_ELEVATOR, acceslibre_enum.ENTRANCE_ELEVATOR],
        "audio_description": [],
        "deaf_and_hard_of_hearing_amenities": [
            acceslibre_enum.DEAF_AND_HARD_OF_HEARING_PORTABLE_INDUCTION_LOOP,
            acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SUBTITLE,
        ],
        "facilities": [acceslibre_enum.FACILITIES_UNADAPTED],
        "sound_beacon": [acceslibre_enum.SOUND_BEACON],
        "trained_personnel": [acceslibre_enum.PERSONNEL_UNTRAINED],
        "transport_modality": [acceslibre_enum.PARKING_NEARBY],
    }
    externalAccessibilityUrl = factory.LazyAttribute(
        lambda p: f"https://site-d-accessibilite.com/erps/{p.externalAccessibilityId}/"
    )
    lastUpdateAtProvider = datetime.datetime(2024, 3, 1, 0, 0)


class OffererAddressFactory(BaseFactory):
    class Meta:
        model = models.OffererAddress

    label: factory.declarations.BaseDeclaration | None = factory.Sequence("Address label {}".format)
    address = factory.SubFactory(geography_factories.AddressFactory)

    @classmethod
    def _create(
        cls, model_class: type[models.OffererAddress], *args: typing.Any, **kwargs: typing.Any
    ) -> models.OffererAddress:
        offerer = kwargs.get("offerer")
        if venue := kwargs.get("venue"):
            if offerer:
                if offerer != venue.managingOfferer:
                    raise ValueError("venue must be consistent with offerer")
            else:
                kwargs["offerer"] = venue.managingOfferer
        elif not offerer:
            kwargs["offerer"] = OffererFactory()
        return super()._create(model_class, *args, **kwargs)


class _LocationFactory(OffererAddressFactory):
    # TODO (prouzet, 2025-11-13) CLEAN_OA When venueId is mandatory, type always set and Venue.offererAddressId removed,
    # this could be simplified and Venue created in OffererAddressFactory._create without reference to self.
    @factory.post_generation
    def venue(self, create: bool, extracted: models.Venue | None, **kwargs: typing.Any) -> models.Venue | None:
        if not create:
            return None
        if extracted:
            self.venue = extracted
            if self.offerer != extracted.managingOfferer:  # type: ignore[attr-defined]
                raise ValueError("venue must be consistent with offerer")
        else:
            self.venue = VenueFactory.create(managingOfferer=self.offerer, offererAddress=self)  # type: ignore[attr-defined]
            db.session.add(self)
            db.session.flush()
        return self.venue


class VenueLocationFactory(_LocationFactory):
    type = models.LocationType.VENUE_LOCATION
    label = None


class OfferLocationFactory(_LocationFactory):
    type = models.LocationType.OFFER_LOCATION


def get_offerer_address_with_label_from_venue(venue: models.Venue) -> models.OffererAddress | None:
    oa = (
        db.session.query(models.OffererAddress)
        .filter_by(address=venue.offererAddress.address, offerer=venue.managingOfferer, label=venue.common_name)
        .one_or_none()
    )
    if oa:
        return oa

    return OffererAddressFactory.create(
        address=venue.offererAddress.address, offerer=venue.managingOfferer, label=venue.common_name
    )


class OffererConfidenceRuleFactory(BaseFactory):
    class Meta:
        model = models.OffererConfidenceRule

    # One (and only one) must be set
    offerer: factory.SubFactory | None = None
    venue: factory.SubFactory | None = None


class ManualReviewOffererConfidenceRuleFactory(OffererConfidenceRuleFactory):
    offerer = factory.SubFactory(OffererFactory)
    confidenceLevel = models.OffererConfidenceLevel.MANUAL_REVIEW


class WhitelistedOffererConfidenceRuleFactory(OffererConfidenceRuleFactory):
    offerer = factory.SubFactory(OffererFactory)
    confidenceLevel = models.OffererConfidenceLevel.WHITELIST


class ManualReviewVenueConfidenceRuleFactory(OffererConfidenceRuleFactory):
    venue = factory.SubFactory(VenueFactory)
    confidenceLevel = models.OffererConfidenceLevel.MANUAL_REVIEW


class WhitelistedVenueConfidenceRuleFactory(OffererConfidenceRuleFactory):
    venue = factory.SubFactory(VenueFactory)
    confidenceLevel = models.OffererConfidenceLevel.WHITELIST


class NonPaymentNoticeFactory(BaseFactory[models.NonPaymentNotice]):
    class Meta:
        model = models.NonPaymentNotice

    amount = decimal.Decimal("199.99")
    emitterName = "Guy Ssier de Justice"
    emitterEmail = "plus.dargent@example.com"
    dateReceived = factory.LazyFunction(lambda: datetime.date.today() - datetime.timedelta(days=3))
    noticeType = models.NoticeType.UNPAID_AMOUNT_NOTICE
    reference = factory.Sequence("TEST{}".format)
