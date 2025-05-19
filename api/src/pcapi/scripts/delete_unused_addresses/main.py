"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-35652-fix-addresses-without-street/api/src/pcapi/scripts/delete_unused_addresses
/main.py

"""

import argparse
import logging

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.app import app
from pcapi.core.geography.models import Address
from pcapi.core.offerers.models import OffererAddress
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool = False) -> None:
    try:
        statement = sa.delete(Address).where(
            Address.id.in_(
                sa.select(Address.id)
                .outerjoin(OffererAddress, Address.id == OffererAddress.addressId)
                .where(OffererAddress.id == None)  # pylint: disable=singleton-comparison
                .options(sa_orm.load_only(Address.id))
            )
        )
        db.session.execute(statement, execution_options={"synchronize_session": False})
        if not_dry:
            db.session.commit()

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.info(
            "Addresses could not be deleted - %s",
            str(e),
        )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(args.not_dry)

    if args.not_dry:
        logger.info("Script run finished")
    else:
        logger.info("Dry run finished, rollback")
        db.session.rollback()
