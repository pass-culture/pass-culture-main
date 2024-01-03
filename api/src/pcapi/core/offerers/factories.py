import datetime
import typing

import factory

from pcapi.core.factories import BaseFactory
import pcapi.core.users.factories as users_factories
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import crypto

from . import api
from . import models


class OffererFactory(BaseFactory):
    class Meta:
        model = models.Offerer

    name = factory.Sequence("Le Petit Rintintin Management {}".format)
    address = "1 boulevard Poissonnière"
    postalCode = "75000"
    city = "Paris"
    siren = factory.Sequence(lambda n: f"{n + 1:09}")
    isActive = True
    validationStatus = ValidationStatus.VALIDATED


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
    departementCode = factory.LazyAttribute(lambda o: None if o.isVirtual else "75")
    latitude: float | None = 48.87004
    longitude: float | None = 2.37850
    managingOfferer = factory.SubFactory(OffererFactory)
    address = factory.LazyAttribute(lambda o: None if o.isVirtual else "1 boulevard Poissonnière")
    banId = factory.LazyAttribute(lambda o: None if o.isVirtual else "75102_7560_00001")
    postalCode = factory.LazyAttribute(lambda o: None if o.isVirtual else "75000")
    city = factory.LazyAttribute(lambda o: None if o.isVirtual else "Paris")
    publicName = factory.SelfAttribute("name")
    siret = factory.LazyAttributeSequence(lambda o, n: f"{o.managingOfferer.siren}{n:05}")
    isVirtual = False
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
    address = None
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

    timespan = factory.LazyFunction(lambda: [datetime.datetime.utcnow() - datetime.timedelta(days=365), None])


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


DEFAULT_PREFIX = "development_prefix"
DEFAULT_SECRET = "clearSecret"
DEFAULT_CLEAR_API_KEY = f"{DEFAULT_PREFIX}_{DEFAULT_SECRET}"


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
