from random import randint

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.categories import subcategories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.models import db
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_admin_users import create_industrial_admin_users


class Sirene:
    def __init__(self) -> None:
        self.siret = str(randint(00000000000000, 99999999999999))
        self.siren = self.siret[0:9]


def save_allocine_sandbox() -> None:
    sirene = Sirene()

    create_industrial_admin_users()

    offerer = offerers_factories.OffererFactory.create(
        name="Le Royal - Cinéma d'essai",
        siren=sirene.siren,
    )

    offerers_factories.UserOffererFactory.create(offerer=offerer, user__email="api@example.com")

    venue = offerers_factories.VenueFactory.create(
        managingOfferer=offerer,
        bookingEmail="fake@email.com",
        comment="Salle de cinéma",
        name=offerer.name + " - Salle 1",
        siret=sirene.siret,
        offererAddress__address__street="145, rue Chaplin",
        offererAddress__address__postalCode="75017",
        offererAddress__address__city="Paris 17",
    )

    provider = get_provider_by_local_class("AllocineStocks")
    assert provider  # helps mypy

    venue_provider = providers_factories.VenueProviderFactory.create(venue=venue, provider=provider)

    db.session.add_all((offerer, venue, provider, venue_provider))

    offer = offers_factories.OfferFactory.create(
        venue=venue,
        product__subcategoryId=subcategories.SEANCE_CINE.id,
        lastProviderId=provider.id,
        idAtProvider="TW92aWU6MjQ4MTAy%34007977100028-VF",
    )

    db.session.add(offer)
    db.session.commit()
