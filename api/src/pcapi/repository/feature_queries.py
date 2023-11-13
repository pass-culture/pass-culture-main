from pcapi.models.feature import Feature


def find_all() -> list[Feature]:
    return Feature.query.all()
