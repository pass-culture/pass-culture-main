import datetime
import typing

import factory

from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.core.factories import BaseFactory
import pcapi.core.geography.factories as geography_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import feature
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import crypto
from pcapi.utils import siren as siren_utils
from pcapi.utils.date import timespan_str_to_numrange
import pcapi.utils.postal_code as postal_code_utils

from . import api
from . import models


if typing.TYPE_CHECKING:
    from pcapi.core.educational.models import AdageVenueAddress
    from pcapi.core.finance.models import BankAccount


OPENING_HOURS = [("10:00", "13:00"), ("14:00", "19:30")]


class OffererFactory(BaseFactory):
    class Meta:
        model = models.Offerer

    name = factory.Sequence("Le Petit Rintintin Management {}".format)
    street = "1 boulevard Poissonnière"
    postalCode = "75000"
    city = "Paris"
    siren = factory.Sequence(lambda n: siren_utils.complete_siren_or_siret(f"{n + 1:08}"))  # ensures valid format
    isActive = True
    validationStatus = ValidationStatus.VALIDATED
    allowedOnAdage = True


class NotValidatedOffererFactory(OffererFactory):
    validationStatus = ValidationStatus.NEW


class PendingOffererFactory(OffererFactory):
    validationStatus = ValidationStatus.PENDING


class RejectedOffererFactory(OffererFactory):
    validationStatus = ValidationStatus.REJECTED
    isActive = False


class CollectiveOffererFactory(OffererFactory):
    name = factory.Sequence("[EAC] La structure de Moz'Art {}".format)


class VenueFactory(BaseFactory):
    class Meta:
        model = models.Venue

    name = factory.Sequence("Le Petit Rintintin {}".format)
    latitude: float | None = 48.87004
    longitude: float | None = 2.37850
    managingOfferer = factory.SubFactory(OffererFactory)
    street = factory.LazyAttribute(lambda o: None if o.isVirtual else "1 boulevard Poissonnière")
    banId = factory.LazyAttribute(lambda o: None if o.isVirtual else "75102_7560_00001")
    postalCode = factory.LazyAttribute(lambda o: None if o.isVirtual else "75000")
    departementCode = factory.LazyAttribute(lambda o: None if o.isVirtual else _get_department_code(o.postalCode))
    city = factory.LazyAttribute(lambda o: None if o.isVirtual else "Paris")
    publicName = factory.SelfAttribute("name")
    siret = factory.LazyAttributeSequence(
        lambda o, n: siren_utils.complete_siren_or_siret(f"{o.managingOfferer.siren}{n:04}")
    )
    isVirtual = False
    isPermanent = factory.LazyAttribute(lambda o: o.venueTypeCode in models.PERMENANT_VENUE_TYPES)
    venueTypeCode = models.VenueTypeCode.OTHER
    description = factory.Faker("text", max_nb_chars=64)
    audioDisabilityCompliant: bool | None = False
    mentalDisabilityCompliant: bool | None = False
    motorDisabilityCompliant: bool | None = False
    visualDisabilityCompliant: bool | None = False
    contact = factory.RelatedFactory("pcapi.core.offerers.factories.VenueContactFactory", factory_related_name="venue")
    bookingEmail = factory.Sequence("venue{}@example.net".format)
    dmsToken = factory.LazyFunction(api.generate_dms_token)
    timezone: str = "Europe/Paris"
    _bannerUrl = None
    offererAddress = factory.SubFactory(
        "pcapi.core.offerers.factories.OffererAddressFactory", offerer=factory.SelfAttribute("..managingOfferer")
    )

    @factory.post_generation
    def pricing_point(  # pylint: disable=no-self-argument
        venue: models.Venue,
        create: bool,
        extracted: typing.Callable | None,
        **kwargs: typing.Any,
    ) -> models.VenuePricingPointLink | None:
        if not create:
            return None
        pricing_point = extracted
        if not pricing_point:
            return None
        if pricing_point == "self":
            pricing_point = venue
        return VenuePricingPointLinkFactory(venue=venue, pricingPoint=pricing_point)

    @factory.post_generation
    def reimbursement_point(  # pylint: disable=no-self-argument
        venue: models.Venue,
        create: bool,
        extracted: typing.Callable | None,
        **kwargs: typing.Any,
    ) -> models.VenueReimbursementPointLink | None:
        if not create:
            return None
        reimbursement_point = extracted
        if not reimbursement_point:
            return None
        if reimbursement_point == "self":
            reimbursement_point = venue
        return VenueReimbursementPointLinkFactory(
            venue=venue,
            reimbursementPoint=reimbursement_point,
        )

    @factory.post_generation
    def bank_account(
        self: models.Venue, create: bool, extracted: "BankAccount | None", **kwargs: typing.Any
    ) -> models.VenueBankAccountLink | None:
        if not create:
            return None
        bank_account = extracted
        if not bank_account:
            return None
        return VenueBankAccountLinkFactory(venue=self, bankAccount=bank_account)

    @factory.post_generation
    def opening_hours(
        self: models.Venue, create: bool, extracted: list[models.OpeningHours] | None, **kwargs: typing.Any
    ) -> list[models.OpeningHours] | None:
        if not create:
            return None
        opening_hours = extracted
        if not opening_hours:
            opening_hours = []
        if self.isPermanent:
            for weekday in models.Weekday:
                if weekday.value == "MONDAY":
                    timespan = timespan_str_to_numrange([OPENING_HOURS[1]])
                elif weekday.value != "SUNDAY":
                    timespan = timespan_str_to_numrange(OPENING_HOURS)
                else:
                    timespan = None
                opening_hours.append(OpeningHoursFactory(venue=self, weekday=weekday, timespan=timespan))
        return opening_hours

    @factory.post_generation
    def adage_venue_addresses(  # pylint: disable=no-self-argument
        venue: models.Venue,
        create: bool,
        extracted: typing.Any,
        **kwargs: typing.Any,
    ) -> typing.Sequence["AdageVenueAddress"]:
        from pcapi.core.educational.factories import AdageVenueAddressFactory

        if not create or not venue.adageId:
            return []
        return [AdageVenueAddressFactory(venue=venue)]


def _get_department_code(postal_code: str | None) -> str | None:
    if not postal_code:
        return None
    return postal_code_utils.PostalCode(postal_code).get_departement_code()


class CollectiveVenueFactory(VenueFactory):
    venueTypeCode = models.VenueTypeCode.PERFORMING_ARTS

    isPermanent = True

    adageId = factory.Sequence(str)
    adageInscriptionDate = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=365))

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
    bannerMeta = None


class VirtualVenueFactory(VenueFactory):
    isVirtual = True
    street = None
    departementCode = None
    postalCode = None
    city = None
    latitude = None
    longitude = None
    siret = None
    audioDisabilityCompliant = None
    mentalDisabilityCompliant = None
    motorDisabilityCompliant = None
    visualDisabilityCompliant = None
    venueTypeCode = models.VenueTypeCode.DIGITAL


class VenueWithoutSiretFactory(VenueFactory):
    siret = None
    comment = "No SIRET"


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
            datetime.datetime.utcnow() - datetime.timedelta(days=365),
            None,
        ]
    )


class VenueReimbursementPointLinkFactory(BaseFactory):
    class Meta:
        model = models.VenueReimbursementPointLink

    venue = factory.SubFactory(VenueFactory)
    reimbursementPoint = factory.SubFactory(
        VenueFactory,
        managingOfferer=factory.SelfAttribute("..venue.managingOfferer"),
    )
    timespan = factory.LazyFunction(
        lambda: [
            datetime.datetime.utcnow() - datetime.timedelta(days=365),
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
    timespan = factory.LazyFunction(lambda: [datetime.datetime.utcnow() - datetime.timedelta(days=365), None])


class OpeningHoursFactory(BaseFactory):
    class Meta:
        model = models.OpeningHours

    venue = factory.SubFactory(VenueFactory)
    weekday = models.Weekday.MONDAY
    timespan = timespan_str_to_numrange(OPENING_HOURS)


class UserOffererFactory(BaseFactory):
    class Meta:
        model = models.UserOfferer

    user = factory.SubFactory(users_factories.ProFactory)
    offerer = factory.SubFactory(OffererFactory)
    validationStatus = ValidationStatus.VALIDATED


class NotValidatedUserOffererFactory(UserOffererFactory):
    user = factory.SubFactory(users_factories.NonAttachedProFactory)
    validationStatus = ValidationStatus.NEW


class RejectedUserOffererFactory(UserOffererFactory):
    validationStatus = ValidationStatus.REJECTED


class DeletedUserOffererFactory(UserOffererFactory):
    validationStatus = ValidationStatus.DELETED


class UserNotValidatedOffererFactory(BaseFactory):
    class Meta:
        model = models.UserOfferer

    user = factory.SubFactory(users_factories.NonAttachedProFactory)
    offerer = factory.SubFactory(NotValidatedOffererFactory)
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

    offerer = factory.SubFactory(OffererFactory)
    prefix = DEFAULT_PREFIX

    @classmethod
    def _create(
        cls,
        model_class: type[models.ApiKey],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.ApiKey:
        if feature.FeatureToggle.WIP_ENABLE_NEW_HASHING_ALGORITHM.is_active():
            kwargs["secret"] = crypto.hash_public_api_key(kwargs.get("secret", DEFAULT_SECRET))
        else:
            kwargs["secret"] = crypto.hash_password(kwargs.get("secret", DEFAULT_SECRET))

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
    dateCreated = datetime.datetime.utcnow()
    user = factory.SubFactory(users_factories.ProFactory)
    status = models.InvitationStatus.PENDING


class IndividualOffererSubscription(BaseFactory):
    class Meta:
        model = models.IndividualOffererSubscription

    offerer = factory.SubFactory(NotValidatedOffererFactory)
    isEmailSent = True
    dateEmailSent = factory.LazyFunction(lambda: datetime.date.today() - datetime.timedelta(days=3))


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
    label = factory.Sequence("Address label {}".format)
    address = factory.SubFactory(geography_factories.AddressFactory)
    offerer = factory.SubFactory(OffererFactory)

    class Meta:
        model = models.OffererAddress


class OffererConfidenceRuleFactory(BaseFactory):
    class Meta:
        model = models.OffererConfidenceRule

    # One (and only one) must be set
    offerer = None
    venue = None


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
