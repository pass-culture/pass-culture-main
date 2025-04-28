from pcapi.models import db
from pcapi.models.feature import Feature


def find_all() -> list[Feature]:
    return db.session.query(Feature).all()
