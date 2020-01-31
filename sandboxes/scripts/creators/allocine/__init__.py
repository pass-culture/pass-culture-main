from random import randint

from models import EventType
from repository import repository
from repository.provider_queries import get_provider_by_local_class
from tests.model_creators.generic_creators import create_user, create_offerer, create_user_offerer, create_venue, \
    create_provider, create_venue_provider
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product


class Sirene():
    def __init__(self):
        self.siret = str(randint(00000000000000, 99999999999999))
        self.siren = self.siret[0:9]


def save_allocine_sandbox():

    sirene = Sirene()

    user = create_user(
        first_name='Didier',
        last_name='Champion',
        public_name='Didier Champion',
        email='pro.exploitant-cinema@example.net',
        can_book_free_offers=False
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
        comment='Salle de cinéma',
        name=offerer.name + ' - Salle 1',
        postal_code=offerer.postalCode,
        siret=sirene.siret
    )



    provider = get_provider_by_local_class('AllocineStocks')

    venue_provider = create_venue_provider(venue, provider)

    repository.save(user, offerer, user_offerer, venue, provider, venue_provider)

    offer = create_offer_with_event_product(venue, event_type=EventType.CINEMA, last_provider_id=provider.id, id_at_providers='TW92aWU6MjQ4MTAy%34007977100028-VF')

    repository.save(offer)
