from pcapi.models.feature import Feature


def find_all():  # type: ignore [no-untyped-def]
    return Feature.query.all()
