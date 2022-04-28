import factory

from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories
from pcapi.utils import crypto

from . import models


class OffererFactory(BaseFactory):
    class Meta:
        model = models.Offerer

    name = factory.Sequence("Le Petit Rintintin Management {}".format)
    address = "1 boulevard Poissonnière"
    postalCode = "75000"
    city = "Paris"
    siren = factory.Sequence(lambda n: f"{n:09}")
    isActive = True


class VenueFactory(BaseFactory):
    class Meta:
        model = models.Venue

    name = factory.Sequence("Le Petit Rintintin {}".format)
    departementCode = factory.LazyAttribute(lambda o: None if o.isVirtual else "75")
    latitude = 48.87004
    longitude = 2.37850
    managingOfferer = factory.SubFactory(OffererFactory)
    address = factory.LazyAttribute(lambda o: None if o.isVirtual else "1 boulevard Poissonnière")
    postalCode = factory.LazyAttribute(lambda o: None if o.isVirtual else "75000")
    city = factory.LazyAttribute(lambda o: None if o.isVirtual else "Paris")
    publicName = factory.SelfAttribute("name")
    siret = factory.LazyAttributeSequence(lambda o, n: f"{o.managingOfferer.siren}{n:05}")
    isVirtual = False
    venueTypeCode = models.VenueTypeCode.OTHER  # type: ignore[attr-defined]
    venueType = factory.SubFactory(
        "pcapi.core.offerers.factories.VenueTypeFactory", label=factory.SelfAttribute("..venueTypeCode.value")
    )
    description = factory.Faker("text", max_nb_chars=64)
    audioDisabilityCompliant = False
    mentalDisabilityCompliant = False
    motorDisabilityCompliant = False
    visualDisabilityCompliant = False
    businessUnit = factory.SubFactory(
        "pcapi.core.finance.factories.BusinessUnitFactory",
        siret=factory.LazyAttribute(lambda bu: bu.factory_parent.siret),
    )
    contact = factory.RelatedFactory("pcapi.core.offerers.factories.VenueContactFactory", factory_related_name="venue")
    bookingEmail = factory.Sequence("venue{}@example.net".format)

    @factory.post_generation
    def venue_link(venue, create, extracted, **kwargs):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument
        import pcapi.core.finance.factories as finance_factories

        if not create:
            return None
        if not venue.businessUnit:
            return None
        return finance_factories.BusinessUnitVenueLinkFactory(venue=venue, businessUnit=venue.businessUnit)


class VirtualVenueFactory(VenueFactory):
    isVirtual = True
    address = None
    departementCode = None
    postalCode = None
    city = None
    latitude = None  # type: ignore [assignment]
    longitude = None  # type: ignore [assignment]
    siret = None
    audioDisabilityCompliant = False
    mentalDisabilityCompliant = False
    motorDisabilityCompliant = False
    visualDisabilityCompliant = False
    venueTypeCode = models.VenueTypeCode.DIGITAL  # type: ignore[attr-defined]


class UserOffererFactory(BaseFactory):
    class Meta:
        model = models.UserOfferer

    user = factory.SubFactory(users_factories.ProFactory)
    offerer = factory.SubFactory(OffererFactory)


class VirtualVenueTypeFactory(BaseFactory):
    class Meta:
        model = models.VenueType

    label = "Offre numérique"


class VenueTypeFactory(BaseFactory):
    class Meta:
        model = models.VenueType
        sqlalchemy_get_or_create = ("label",)

    label = "Librairie"


class VenueLabelFactory(BaseFactory):
    class Meta:
        model = models.VenueLabel

    label = "Cinéma d'art et d'essai"


class VenueContactFactory(BaseFactory):
    class Meta:
        model = models.VenueContact

    venue = factory.SubFactory(VenueFactory)
    email = "contact@venue.com"
    website = "https://my@website.com"
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
    def _create(cls, model_class, *args, **kwargs):  # type: ignore [no-untyped-def]
        kwargs["secret"] = crypto.hash_password(kwargs.get("secret", DEFAULT_SECRET))
        return super()._create(model_class, *args, **kwargs)


class OffererTagFactory(BaseFactory):
    class Meta:
        model = models.OffererTag

    name = factory.Sequence("OffererTag_{}".format)


class OffererTagMappingFactory(BaseFactory):
    class Meta:
        model = models.OffererTagMapping

    offerer = factory.SubFactory(OffererFactory)
    tag = factory.SubFactory(OffererTagFactory)
