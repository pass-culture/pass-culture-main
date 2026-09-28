"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-43477/script_add_integration_movies \
  -f NAMESPACE=add_integration_movies \
  -f SCRIPT_ARGUMENTS="";

"""

import os
import argparse
import csv
import logging
import pathlib
import pprint
import typing
from datetime import datetime

import pydantic

from pcapi.core.categories import subcategories
from pcapi.core.categories.pro_categories import CategoryIdEnum
from pcapi.core.offers.models import Product
from pcapi.models import db


logger = logging.getLogger(__name__)


class Company(pydantic.BaseModel):
    name: str | None
    activity: str


class CreditPerson(pydantic.BaseModel):
    firstName: str
    lastName: str


class CreditPosition(pydantic.BaseModel):
    name: str


class Credit(pydantic.BaseModel):
    person: CreditPerson
    position: CreditPosition


class CinemaData(pydantic.BaseModel):
    visa: str
    allocine_id: str
    name: str
    description: str
    casting: list[str]
    countries: list[str]
    companies: list[Company]
    genres: list[str]
    release_date: datetime
    movie_type: str
    credits: Credit
    category_id: CategoryIdEnum


class CouldNotParseRow(Exception):
    def __init__(self, line: int, data: dict, *args: typing.Any, **kwargs: typing.Any) -> None:
        self.line = line
        self.data = data
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return f"LINE={self.line}, DATA={pprint.pformat(self.data)}"


class UnexpectedDataError(CouldNotParseRow):
    pass


def parse_row(row: dict) -> dict:
    return {
        **row,
        # lists and dicts have been serialized as strings
        # eval() is not recommended, BUT: we are the one
        # injecting the input data, we know what is inside
        "Casting": eval(row["Casting"]),  # nosemgrep: python.lang.security.audit.eval-detected.eval-detected
        "Countries": eval(row["Countries"]),  # nosemgrep: python.lang.security.audit.eval-detected.eval-detected
        "Companies": eval(  # nosemgrep: python.lang.security.audit.eval-detected.eval-detected
            row["Companies"].replace("null", "None")
        ),
        "Genres": [
            genre.upper()
            for genre in eval(row["Genres"])  # nosemgrep
        ],
    }


def load_data_from_csv(path: pathlib.Path) -> list[CinemaData]:
    rows = []

    with open(path) as f:
        loader = csv.DictReader(f)
        for idx, base_row in enumerate(loader):
            try:
                row = parse_row(base_row)

                # not great, not perfect but works most of the times with
                # the input data used
                stage_director = row["Stage Director"].split(" ")
                stage_director_first_name = " ".join(stage_director[:-1])
                stage_director_last_name = stage_director[-1]

                rows.append(
                    CinemaData(
                        visa=row["Visa"],
                        allocine_id=row["allocine_id"],
                        name=row["Offer Name"],
                        description=row["Offer Description"],
                        casting=row["Casting"],
                        countries=row["Countries"],
                        companies=row["Companies"],
                        genres=row["Genres"],
                        release_date=row["Release Date"],
                        movie_type=row["Movie Type"],
                        category_id=row["Offer Category ID"],
                        credits={  # type: ignore
                            "person": {"firstName": stage_director_first_name, "lastName": stage_director_last_name},
                            "position": {"name": "DIRECTOR"},
                        },
                    )
                )
            except pydantic.ValidationError as error:
                raise UnexpectedDataError(line=idx, data=base_row) from error
            except Exception as error:
                raise CouldNotParseRow(line=idx, data=base_row) from error

    return rows


def insert_products_from_data(rows: list[CinemaData]) -> None:
    for idx, data in enumerate(rows):
        db.session.add(
            Product(
                name=data.name,
                description=data.description,
                subcategoryId=subcategories.SEANCE_CINE.id,
                extraData={
                    "visa": data.visa,
                    "allocineId": data.allocine_id,
                    "cast": data.casting,
                    "countries": data.countries,
                    "companies": data.companies,
                    "genres": data.genres,
                    "releaseDate": data.release_date,
                    "type": data.movie_type,
                    "credits": data.credits,
                },
            )
        )

        logger.info("Added one product: %s", data.name)

    logger.info("Added %d products", len(rows))


def main(path: pathlib.Path) -> None:
    rows = load_data_from_csv(path)
    insert_products_from_data(rows)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--path", type=pathlib.Path, default=None)
    args = parser.parse_args()

    if not args.path:
        namespace_dir = os.path.dirname(os.path.abspath(__file__))
        path = pathlib.Path(namespace_dir) / "cinema.integration.data.csv"
    else:
        path = args.path

    main(path)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
