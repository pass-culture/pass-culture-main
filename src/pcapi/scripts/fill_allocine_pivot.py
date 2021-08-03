# WARNING:
# this expects the CSV to be formatted as "theaterId", "internalId", siret in that order !
import argparse
import csv

import sqlalchemy.exc

from pcapi.app import app
from pcapi.models import AllocinePivot
from pcapi.models.db import db


def read_allocine_csv(file_path: str) -> list[tuple]:
    with open(file_path, mode="r", newline="\n") as file:
        return [tuple(line) for line in csv.reader(file, delimiter=",")]


def fill_allocine_pivot(lines):
    for line in lines:
        try:
            with db.session.begin_nested():
                pivot = AllocinePivot(
                    theaterId=line[0],
                    internalId=line[1],
                    siret=line[2],
                )
                db.session.add(pivot)
                db.session.flush()
        except sqlalchemy.exc.IntegrityError as e:
            print("Ignoring line: %s because %s" % (str(line), e.orig.diag.message_detail))
        else:
            print("Imported line: %s" % str(line))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""imports a CSV of allocine pivot ordered as ("theaterId", "internalId", "siret")."""
    )
    parser.add_argument("filename", help="path to the CSV file with pivot to import")
    parser.add_argument(
        "--no-dry-run", "-n", help="deactivate the dry run mode", dest="dry_run", action="store_false", default=True
    )
    args = parser.parse_args()

    data = read_allocine_csv(args.filename)
    with app.app_context():
        fill_allocine_pivot(data)
        if args.dry_run:
            db.session.rollback()
        else:
            db.session.commit()
