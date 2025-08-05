from random import randint

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.categories import subcategories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_admin_users import create_industrial_admin_users
from pcapi.utils import repository


class Sirene:
    def __init__(self) -> None:
        self.siret = str(randint(00000000000000, 99999999999999))
        self.siren = self.siret[0:9]


def save_allocine_sandbox() -> None:
    sirene = Sirene()

    create_industrial_admin_users()

    offerer = offerers_factories.OffererFactory.create(
        address="145, rue Chaplin",
        city="Paris 17",
        name="Le Royal - Cinéma d'essai",
        postalCode="75017",
        siren=sirene.siren,
    )

    offerers_factories.UserOffererFactory.create(offerer=offerer, user__email="api@example.com")

    venue = offerers_factories.VenueFactory.create(
        managingOfferer=offerer,
        address=offerer.address,
        bookingEmail="fake@email.com",
        city=offerer.city,
        comment="Salle de cinéma",
        name=offerer.name + " - Salle 1",
        postalCode=offerer.postalCode,
        siret=sirene.siret,
    )

    provider = get_provider_by_local_class("AllocineStocks")

    venue_provider = providers_factories.VenueProviderFactory.create(venue=venue, provider=provider)

    repository.save(offerer, venue, provider, venue_provider)

    offer = offers_factories.OfferFactory.create(
        venue=venue,
        product__subcategoryId=subcategories.SEANCE_CINE.id,
        lastProviderId=provider.id,
        idAtProvider="TW92aWU6MjQ4MTAy%34007977100028-VF",
    )

    repository.save(offer)
