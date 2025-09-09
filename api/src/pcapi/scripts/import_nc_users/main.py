"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-37049-import-nc-users/api/src/pcapi/scripts/import_nc_users/main.py

"""

import argparse
import csv
import logging
import os
import typing

from pydantic import BaseModel

from pcapi.app import app
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.core.users.password_utils import random_password
from pcapi.models import db
from pcapi.routes.serialization import users as users_serializers
from pcapi.utils import siren as siren_utils
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


class UserRow(typing.TypedDict):
    firstName: str
    lastName: str
    phoneNumber: str
    email: str


class ImportCounter(BaseModel):
    total: int = 0
    created: int = 0
    already_present: int = 0
    already_linked: int = 0


def create_pro(user_row: UserRow, offerer: offerers_models.Offerer, row_number: int, counters: ImportCounter) -> None:
    user_in_db = db.session.query(users_models.User).filter_by(email=user_row["email"]).one_or_none()

    counters.total += 1
    if user_in_db is not None:
        logger.info("User already present for email %s for row %s", user_row["email"], row_number)
        counters.already_present += 1

        user_offerer_in_db = (
            db.session.query(offerers_models.UserOfferer).filter_by(offerer=offerer, user=user_in_db).one_or_none()
        )

        if user_offerer_in_db is not None:
            logger.info("User already linked to offerer for row %s", row_number)
            counters.already_linked += 1
        else:
            offerers_api.grant_user_offerer_access(offerer=offerer, user=user_in_db)

        return

    ### Create the user
    body = users_serializers.ProUserCreationBodyV2Model.parse_obj(
        {
            **user_row,
            "password": random_password(),
            "contactOk": False,
            "token": "",
        },
    )
    pro_user = users_api.create_pro_user(body)

    ### Validate the email
    users_api.validate_pro_user_email(pro_user)

    ### Link user to offerer
    offerers_api.grant_user_offerer_access(offerer=offerer, user=pro_user)
    pro_user.add_pro_role()

    ### Update external tools
    external_attributes_api.update_external_pro(pro_user.email)  # this is done on_commit

    counters.created += 1


@atomic()
def main(filename: str, not_dry: bool) -> None:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))

    with open(f"{namespace_dir}/{filename}", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")

        rows = list(reader)

    counters = ImportCounter()

    for i, row in enumerate(rows):
        user_row: UserRow = {
            "firstName": row["Prénom"].strip(),
            "lastName": row["Nom"].strip(),
            "phoneNumber": row["n° de téléphone"].strip(),
            "email": row["Adresse mail"].strip(),
        }
        ridet = row["RIDET"].strip().replace(" ", "").replace(".", "")
        rid7 = ridet[:7]
        siren = siren_utils.rid7_to_siren(rid7)

        offerer: offerers_models.Offerer = db.session.query(offerers_models.Offerer).filter_by(siren=siren).one()

        create_pro(user_row=user_row, offerer=offerer, row_number=i + 1, counters=counters)

    logger.info("Import counters: %s", counters.model_dump(mode="json"))

    if not not_dry:
        mark_transaction_as_invalid()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--filename", type=str, required=True)
    args = parser.parse_args()

    logger.info("Starting NC users import with args %s", args)

    main(filename=args.filename, not_dry=args.not_dry)

    logger.info("Finished")
