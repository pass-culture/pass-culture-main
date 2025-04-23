"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/master/api/src/pcapi/scripts/pc-35654-fix-addresses-without-department-code/main.py

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.geography.models import Address
from pcapi.models import db
from pcapi.utils.regions import get_department_code_from_city_code


logger = logging.getLogger(__name__)


def main() -> None:
    try:
        incorrect_addresses: set[Address] = set(
            db.session.scalars(
                sa.select(Address).where(Address.departmentCode == None)  # pylint: disable=singleton-comparison
            )
        )
        if len(incorrect_addresses) > 0:
            for address in incorrect_addresses:
                address.departmentCode = get_department_code_from_city_code(address.postalCode)
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
