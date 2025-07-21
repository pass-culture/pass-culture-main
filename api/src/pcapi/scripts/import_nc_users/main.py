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

from pcapi.app import app
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.domain.password import random_password
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.routes.serialization import users as users_serializers


logger = logging.getLogger(__name__)


class UserRow(typing.TypedDict):
    firstName: str
    lastName: str
    phoneNumber: str
    email: str


def create_pro(user_row: UserRow, offerer: offerers_models.Offerer, row_number: int) -> None:
    user_in_db = db.session.query(users_models.User).filter_by(email=user_row["email"]).one_or_none()

    if user_in_db is not None:
        logger.info("User already present for row %s", row_number)

        user_offerer_in_db = (
            db.session.query(offerers_models.UserOfferer).filter_by(offerer=offerer, user=user_in_db).one_or_none()
        )

        if user_offerer_in_db is not None:
            logger.info("User already linked to offerer for row %s", row_number)
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

    ### Reset the password
    reset_token = users_api.create_reset_password_token(pro_user)
    transactional_mails.send_reset_password_email_to_pro(reset_token)  # this is done on_commit

    ### Link user to offerer
    offerers_api.grant_user_offerer_access(offerer=offerer, user=pro_user)
    pro_user.add_pro_role()

    ### Update external tools
    external_attributes_api.update_external_pro(pro_user.email)  # this is done on_commit


@atomic()
def main(filename: str, not_dry: bool) -> None:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))

    with open(f"{namespace_dir}/{filename}", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")

        rows = list(reader)

    for i, row in enumerate(rows):
        user_row: UserRow = {
            "firstName": row["Prénom"].strip(),
            "lastName": row["Nom"].strip(),
            "phoneNumber": row["n° de téléphone"].strip(),
            "email": row["Adresse mail"].strip(),
        }

        offerer: offerers_models.Offerer = (
            db.session.query(offerers_models.Offerer).filter_by(siren=row["RIDET"].strip()).one()
        )

        create_pro(user_row=user_row, offerer=offerer, row_number=i + 1)

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
