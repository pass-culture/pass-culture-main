"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-35652-fix-addresses-without-street/api/src/pcapi/scripts/fix_addresses_without_street/main.py

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.geography.models import Address
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    try:
        incorrect_addresses: set[Address] = set(
            db.session.scalars(sa.select(Address).where(Address.street == None))  # pylint: disable=singleton-comparison
        )
        if len(incorrect_addresses) > 0:
            for address in incorrect_addresses:
                existing_addresses: set[Address] = set(
                    db.session.scalars(
                        sa.select(Address).where(
                            Address.id != address.id,
                            Address.city == address.city,
                            Address.postalCode == address.postalCode,
                            Address.latitude == address.latitude,
                            Address.longitude == address.longitude,
                            Address.street == address.city,
                        )
                    )
                )
                if len(existing_addresses) > 0:
                    address.banId = None
                    address.isManualEdition = True
                    address.street = "-"
                else:
                    address.street = address.city
                db.session.add(address)
            logger.info(
                "Found %s Address(es) to fix",
                len(incorrect_addresses),
            )
        else:
            logger.info("Found no Address to fix")

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.info(
            "Addresses could not be fixed - %s",
            str(e),
        )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main()

    if args.not_dry:
        logger.info("Script run finished")
        db.session.commit()
    else:
        logger.info("Dry run finished, rollback")
        db.session.rollback()
