import csv
from typing import Iterable

from pcapi.connectors.cgr import cgr
from pcapi.core.offerers.models import Venue
from pcapi.core.providers.api import delete_venue_provider
from pcapi.core.providers.models import CGRCinemaDetails
from pcapi.core.providers.models import CinemaProviderPivot
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
from pcapi.models import db


class CGRCinema:
    def __init__(self, venue_id: int, name: str, url: str, password: str) -> None:
        self.venue_id = venue_id
        self.name = name
        self.url = url
        self.password = password


def add_all_cinema_pivot_from_file(file_path: str) -> None:
    cgr_provider = Provider.query.filter(Provider.localClass == "CGRStocks").one()
    print("read csv file")
    with open(file_path, mode="r", newline="", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        cinemas_to_add = get_all_cinemas_to_add_from_csv(csv_reader)
        print(f"{len(cinemas_to_add)} cinemas to add")

        for cinema in cinemas_to_add:
            add_cgr_provider_pivot_for_cinema(cinema, cgr_provider)

        db.session.commit()
        print(f"{len(cinemas_to_add)} pivots and venueProviders created")


def get_all_cinemas_to_add_from_csv(rows: Iterable[dict]) -> list[CGRCinema]:
    cinemas_to_add = []
    for row in rows:
        cinema = CGRCinema(
            venue_id=row["Id PC"],
            name=row["CINEMA"],
            url=row["URL WSDL"],
            password=row["MOT DE PASSE"],
        )
        cinemas_to_add.append(cinema)

    return cinemas_to_add


def add_cgr_provider_pivot_for_cinema(cinema: CGRCinema, provider: Provider) -> None:
    print(f"Adding pivot for {cinema.venue_id} - {cinema.url} - ...")

    venue = Venue.query.filter(Venue.id == cinema.venue_id).one_or_none()
    if not venue:
        print(f"No venue found with ID : {cinema.venue_id}")
        return
    pivot = CinemaProviderPivot(venue=venue, provider=provider, idAtProvider=cinema.name)
    cgr_details = CGRCinemaDetails(cinemaProviderPivot=pivot, cinemaUrl=cinema.url)
    num_cine = check_if_api_call_is_ok(cgr_details)
    if not num_cine:
        print(f"Connexion à l'API CGR KO for cinema {cinema.name}, url = {cinema.url}")
        return
    cgr_details.numCinema = num_cine
    venue_provider = VenueProvider.query.filter(VenueProvider.venueId == venue.id).one_or_none()
    if venue_provider:
        delete_venue_provider(venue_provider)
    print("Creating venue provider")
    new_venue_provider = VenueProvider(
        provider=provider, venue=venue, venueIdAtOfferProvider=cinema.name, isDuoOffers=True
    )

    db.session.add(pivot)
    db.session.add(cgr_details)
    db.session.add(new_venue_provider)


def check_if_api_call_is_ok(cgr_cinema_details: CGRCinemaDetails) -> int | None:
    try:
        response = cgr.get_seances_pass_culture(cgr_cinema_details)
        return response.ObjetRetour.NumCine
    # it could be an unexpected XML parsing error
    except Exception:  # pylint: disable=broad-except
        print("Error while checking CGR API information")
    return None
