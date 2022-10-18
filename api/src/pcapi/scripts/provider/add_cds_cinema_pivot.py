import csv
from typing import Iterable

from pcapi.core.providers.models import CDSCinemaDetails
from pcapi.core.providers.models import CinemaProviderPivot
from pcapi.core.providers.models import Provider
from pcapi.models import db


class CDSCinema:
    def __init__(self, account_id: str, cinema_id: str, cds_token: str, venue_siret: str = None) -> None:
        self.account_id = account_id
        self.cinema_id = cinema_id
        self.cds_token = cds_token
        self.venue_siret = venue_siret


def add_all_cinema_pivot_from_file(
    file_path: str,
    dry_run: bool = True,
) -> None:
    cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one_or_none()
    if cds_provider:

        print("read csv file")
        with open(file_path, mode="r", newline="", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            cinemas_to_add = get_all_cinemas_to_add_from_csv(csv_reader)
            print(f"{len(cinemas_to_add)} cinemas to add")

        for cinema in cinemas_to_add:
            update_token_provider_pivot_for_cinema(cinema)

        if dry_run:
            db.session.rollback()
        else:
            db.session.commit()
    else:
        print("CDS Provider not found")


def update_token_provider_pivot_for_cinema(cinema: CDSCinema) -> None:
    print(f"Update Pivot {cinema.account_id} - {cinema.cinema_id} -  ...")
    existing_cds_details = (
        CDSCinemaDetails.query.join(CinemaProviderPivot)
        .filter(CinemaProviderPivot.idAtProvider == cinema.cinema_id)
        .one_or_none()
    )
    if existing_cds_details:
        existing_cds_details.cinemaApiToken = cinema.cds_token
        db.session.add(existing_cds_details)
        db.session.flush()
        print(f"{cinema.cinema_id} updated successfully")
    else:
        print(f"No Pivot found for cinema : {cinema.cinema_id}")


def get_all_cinemas_to_add_from_csv(rows: Iterable[dict]) -> list[CDSCinema]:
    cinemas_to_add = []
    for row in rows:
        cinema = get_cds_cinema_from_csv_row(row)
        if isValidToken(cinema.cds_token):
            cinemas_to_add.append(cinema)
        else:
            print(f"Ignoring {cinema.account_id} - {cinema.cinema_id} : incorrect token")

    return cinemas_to_add


def get_cds_cinema_from_csv_row(row: dict) -> CDSCinema:
    return CDSCinema(
        account_id=row["compte"],
        cinema_id=row["cinemaid"],
        cds_token=row["vadtoken"],
        venue_siret=row["SIRET (manuel)"],
    )


def get_cds_cinema_from_excel_row(row: dict) -> CDSCinema:
    return CDSCinema(
        account_id=row["compte"],
        cinema_id=row["cinemaid"],
        cds_token=row["vadtoken"],
        venue_siret=row["SIRET (manuel)"],
    )


def isValidToken(token: str) -> bool:
    return token not in ["", "null"]
