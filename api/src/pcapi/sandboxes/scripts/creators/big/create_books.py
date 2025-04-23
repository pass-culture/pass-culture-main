import random

from factory.faker import faker

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.sandboxes.scripts.creators.test_cases import create_offer_with_ean
from pcapi.sandboxes.scripts.creators.test_cases import venues_mock


Fake = faker.Faker(locale="fr_FR")


def create_books(size: int) -> None:
    # not executed with sandbox - To be manually launched when needed
    venues = [
        offerers_factories.VenueFactory.create(
            name="Librairie,  " + str(venue["name"]),
            venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
            latitude=venue["latitude"],
            longitude=venue["longitude"],
            address=venue["address"],
            postalCode=venue["postalCode"],
            city=venue["city"],
            departementCode=venue["departementCode"],
        )
        for venue in venues_mock.venues
    ]
    for _ in range(size):
        create_offer_with_ean(Fake.ean13(), random.choice(venues), author=Fake.name())
