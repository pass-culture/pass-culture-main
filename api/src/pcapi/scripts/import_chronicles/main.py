"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):
https://github.com/pass-culture/pass-culture-main/blob/pc-37392-rpa-import-chronicles/api/src/pcapi/scripts/import_chronicles/main.py
"""

import csv
import logging
import os.path
from base64 import b64encode
from os import urandom

from pcapi.app import app
from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.offers.models import Product
from pcapi.core.users.repository import find_user_by_email
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)
FILE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/37392.csv"


def main() -> None:
    with open(FILE_PATH, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            register_chronicle(row)


@atomic()
def register_chronicle(chronicle_line: list[str]) -> None:
    user = find_user_by_email(chronicle_line[3].strip())
    user_id = user.id if user else None
    db.session.add(
        chronicles_models.Chronicle(
            firstName=chronicle_line[0],
            age=int(chronicle_line[1]),
            city=chronicle_line[2],
            clubType=chronicles_models.ChronicleClubType.BOOK_CLUB,
            externalId=f"CSV_{b64encode(urandom(24)).decode('utf-8')}",
            email=chronicle_line[3].strip(),
            userId=user_id,
            productIdentifierType=chronicles_models.ChronicleProductIdentifierType.EAN,
            productIdentifier=chronicle_line[4].strip(),
            products=db.session.query(Product).filter(Product.ean == chronicle_line[4].strip()).all(),
            content=chronicle_line[5].strip(),
            isIdentityDiffusible=True,
            isSocialMediaDiffusible=True,
        )
    )


if __name__ == "__main__":
    app.app_context().push()
    main()
