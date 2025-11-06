import csv
import os
from uuid import uuid4

from pcapi.app import app
from pcapi.core.chronicles.models import Chronicle
from pcapi.core.chronicles.models import ChronicleClubType
from pcapi.core.chronicles.models import ChronicleProductIdentifierType
from pcapi.core.offers.models import Product
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


FILE_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/chronicles.csv"


def get_user_id(email: str) -> int | None:
    return (
        db.session.query(
            User.id,
        )
        .filter(
            User.email == email,
        )
        .limit(1)
        .scalar()
    )


def get_products(ean: str) -> list[Product] | None:
    product = db.session.query(Product).filter(Product.ean == ean).one_or_none()
    if product:
        return [product]
    return []


@atomic()
def import_chronicle(line: dict) -> None:
    db.session.add(
        Chronicle(
            age=int(line["Age"]),
            city=line["Ville"],
            clubType=ChronicleClubType.BOOK_CLUB,
            content=line["Chronique"],
            identifierChoiceId=f"manual-import-{uuid4()}",
            email=line["Mail"],
            firstName=line["Prénom"],
            externalId=f"manual-import-{uuid4()}",
            isIdentityDiffusible=False,
            isSocialMediaDiffusible=True,
            products=get_products(line["EAN"]),
            productIdentifierType=ChronicleProductIdentifierType.EAN,
            productIdentifier=line["EAN"],
            userId=get_user_id(line["Mail"]),
            isActive=False,
        )
    )


def main() -> None:
    with open(FILE_PATH, encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        for line in reader:
            import_chronicle(line)


if __name__ == "__main__":
    app.app_context().push()
    main()
