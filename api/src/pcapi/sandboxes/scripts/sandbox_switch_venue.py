from dataclasses import dataclass

from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db


@dataclass
class Location:
    address: str
    city: str
    latitude: float
    longitude: float
    postalCode: str


OFFERER_LOCATIONS = [
    Location(address="Rue des Poilus", city="Drancy", latitude=48.928099, longitude=2.460249, postalCode="93700"),
    Location(address="Rue de Nieuport", city="Drancy", latitude=48.91683, longitude=2.438839, postalCode="93700"),
    Location(address="Rue Francois Rude", city="Drancy", latitude=48.926432, longitude=2.432279, postalCode="93700"),
    Location(address="Rue Pollet", city="Aulnay-sous-Bois", latitude=48.945379, longitude=2.502902, postalCode="93600"),
    Location(
        address="Rue de Pimodan", city="Aulnay-sous-Bois", latitude=48.926299, longitude=2.490079, postalCode="93600"
    ),
    Location(
        address="Rue de Pologne", city="Aulnay-sous-Bois", latitude=48.940826, longitude=2.479869, postalCode="93600"
    ),
    Location(address="Rue Pasteur", city="Kourou", latitude=5.170549, longitude=-52.649077, postalCode="97310"),
    Location(address="Rue de Cali", city="Kourou", latitude=5.158387, longitude=-52.637413, postalCode="97310"),
    Location(address="Rue de Paris", city="Kourou", latitude=5.161934, longitude=-52.639804, postalCode="97310"),
    Location(address="Rue Panacoco", city="Cayenne", latitude=4.916571, longitude=-52.319168, postalCode="97300"),
    Location(address="Rue Aristote", city="Cayenne", latitude=4.934074, longitude=-52.297176, postalCode="97300"),
    Location(address="Cayenne", city="Cayenne", latitude=4.925246, longitude=-52.311586, postalCode="97300"),
    Location(
        address="RT3", city="Matāʻutu", latitude=-13.282339262455315, longitude=-176.1771062948854, postalCode="98600"
    ),
]


def build_user(email: str) -> users_models.User:
    found_user = db.session.query(users_models.User).filter_by(email=email).one_or_none()
    if found_user:
        return found_user
    else:
        return users_factories.ProFactory.create(lastName="SWITCH-VENUE", firstName="Retention", email=email)


def link_user_and_offerer(user: users_models.User, offerer: offerers_models.Offerer) -> None:
    if db.session.query(offerers_models.UserOfferer).filter_by(userId=user.id, offererId=offerer.id).one_or_none():
        return None
    offerers_factories.UserOffererFactory.create(offerer=offerer, user=user)


def build_offerer_and_venues_and_bank_account(
    name: str, locations: list[Location], siren: str, siret: str, with_bank_account: bool = True
) -> offerers_models.Offerer:
    # check if sandbox has already run
    if (
        existing_offerer := db.session.query(offerers_models.Offerer)
        .filter(offerers_models.Offerer.siren == siren)
        .one_or_none()
    ):
        return existing_offerer

    offerer = offerers_factories.OffererFactory.create(name=name, siren=siren)

    if with_bank_account:
        bank_account = finance_factories.BankAccountFactory.create(
            offerer=offerer, dsApplicationId=9000000 + offerer.id
        )

    for idx, location in enumerate(locations):
        venue = offerers_factories.VenueFactory.create(
            managingOfferer=offerer,
            bookingEmail=f"switch.venue.{siret}@email.com",
            comment="Salle de cinéma",
            name=offerer.name + ", une librairie",
            siret=siret[:-1] + str(idx),
            venueTypeCode=offerers_schemas.VenueTypeCode.LIBRARY,
            offererAddress__address__street=location.address.upper(),
            offererAddress__address__city=location.city,
            offererAddress__address__postalCode=location.postalCode,
        )

        if with_bank_account:
            offerers_factories.VenueBankAccountLinkFactory.create(venue=venue, bankAccount=bank_account)

    return offerer


def save_sandbox() -> None:
    name = "Une structure, un lieu"
    locations = OFFERER_LOCATIONS[0:1]
    siren = "333333000"
    siret = "33333333333000"
    offerer = build_offerer_and_venues_and_bank_account(name, locations, siren, siret)
    user = build_user("one.offerer.one.venue@retention.com")
    link_user_and_offerer(user, offerer)

    name = "Une structure, deux lieux"
    locations = OFFERER_LOCATIONS[1:3]
    siren = "444444000"
    siret = "44444444444000"
    offerer = build_offerer_and_venues_and_bank_account(name, locations, siren, siret)
    user = build_user("one.offerer.two.venues@retention.com")
    link_user_and_offerer(user, offerer)

    name = "Une structure, deux lieux, de nouveau"
    locations = OFFERER_LOCATIONS[3:5]
    siren = "555555000"
    siret = "55555555555000"
    offerer = build_offerer_and_venues_and_bank_account(name, locations, siren, siret)
    user = build_user("one.offerer.two.venues.2@retention.com")
    link_user_and_offerer(user, offerer)

    name = "Une structure, deux lieux, sans compte bancaire"
    locations = OFFERER_LOCATIONS[5:7]
    siren = "666666000"
    siret = "66666666666000"
    offerer = build_offerer_and_venues_and_bank_account(name, locations, siren, siret, with_bank_account=False)
    user = build_user("one.offerer.two.venues.no.bank.accounts@retention.com")
    link_user_and_offerer(user, offerer)
