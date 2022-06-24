import datetime
from unittest.mock import patch

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import factories as users_factories
from pcapi.scripts.travelling_cinema.import_offers_for_travelling_cinema import import_offres_for_travelling_cinema


@patch("pcapi.scripts.travelling_cinema.import_offers_for_travelling_cinema.get_longitude_and_latitude_from_address")
def test_import_offers_for_travelling_cinema(mocked_get_longitude_and_latitude_from_address, db_session):
    mocked_get_longitude_and_latitude_from_address.return_value = [12, 24]
    users_factories.AdminFactory(email="admin@example.com")

    offerers_factories.OffererFactory(siren="555555555")

    import_offres_for_travelling_cinema(
        "admin@example.com", "travelling_cinema_offers.csv", "tests/scripts/travelling_cinema/fixtures/"
    )

    offers = offers_models.Offer.query.all()
    venues = offerers_models.Venue.query.all()
    assert len(offers) == 3
    assert len(venues) == 2


@patch("pcapi.scripts.travelling_cinema.import_offers_for_travelling_cinema.get_longitude_and_latitude_from_address")
def test_import_one_offer_fro_travelling_cinema(mocked_get_longitude_and_latitude_from_address, db_session):
    mocked_get_longitude_and_latitude_from_address.return_value = [12, 24]

    users_factories.AdminFactory(email="admin@example.com")

    offerers_factories.OffererFactory(siren="555555555")

    import_offres_for_travelling_cinema(
        "admin@example.com", "travelling_cinema_one_offer.csv", "tests/scripts/travelling_cinema/fixtures/"
    )

    offer = offers_models.Offer.query.one()
    venue = offerers_models.Venue.query.one()

    assert offer.name == "Buena Vista Social Club"
    assert offer.durationMinutes == 120
    assert not offer.visualDisabilityCompliant
    assert offer.mentalDisabilityCompliant
    assert offer.motorDisabilityCompliant
    assert not offer.audioDisabilityCompliant
    assert offer.withdrawalDetails == "Retrait sur place."
    assert len(offer.stocks) == 1
    assert offer.stocks[0].beginningDatetime == datetime.datetime(2022, 6, 16, 20, 30)
    assert offer.stocks[0].price == 10
    assert not offer.stocks[0].quantity

    assert venue.longitude == 12
    assert venue.latitude == 24
    assert venue.name == "Le bord de l'eau"
    assert venue.address == "313 Allée des Roses de Picardie"
    assert venue.postalCode == "60280"
    assert venue.city == "Margny-lès-Compiègne"
