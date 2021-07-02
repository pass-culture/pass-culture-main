from pcapi.models.feature import Feature


def find_all():
    return Feature.query.all()
