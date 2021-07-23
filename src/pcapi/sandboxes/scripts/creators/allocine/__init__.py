from random import randint

from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.generic_creators import create_venue_provider
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.models import EventType
from pcapi.repository import repository
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_admin_users import *


class Sirene:
    def __init__(self) -> None:
        self.siret = str(randint(00000000000000, 99999999999999))
        self.siren = self.siret[0:9]


def save_allocine_sandbox() -> None:

    sirene = Sirene()

    create_industrial_admin_users()

    user = users_factories.UserFactory(
        firstName="Didier",
        lastName="Champion",
        publicName="Didier Champion",
        email="pro.exploitant-cinema@example.net",
        isBeneficiary=False,
    )

    offerer = create_offerer(
        address="145, rue Chaplin",
        city="Paris 17",
        name="Le Royal - Cinéma d'essai",
        postal_code="75017",
        siren=sirene.siren,
    )

    user_offerer = create_user_offerer(
        offerer=offerer,
        user=user,
    )

    venue = create_venue(
        offerer,
        address=offerer.address,
        booking_email="fake@email.com",
        city=offerer.city,
        comment="Salle de cinéma",
        name=offerer.name + " - Salle 1",
        postal_code=offerer.postalCode,
        siret=sirene.siret,
    )

    activate_provider("AllocineStocks")
    provider = get_provider_by_local_class("AllocineStocks")

    venue_provider = create_venue_provider(venue, provider=provider, is_active=True)

    repository.save(offerer, user_offerer, venue, provider, venue_provider)

    offer = create_offer_with_event_product(
        venue,
        event_type=EventType.CINEMA,
        last_provider_id=provider.id,
        id_at_providers="TW92aWU6MjQ4MTAy%34007977100028-VF",
        last_provider=provider,
    )

    repository.save(offer)
