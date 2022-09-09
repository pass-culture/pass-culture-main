from pcapi.models import db

from . import exceptions
from . import models


# FIXME (dbaty, 2021-12-13): the checks here could be shared with
# other parts of the code that validates SIRET but, as of now, this
# function is used temporarily in business unit initialization. It
# will be removed soon.
def check_business_unit_siret(business_unit: models.BusinessUnit, siret: str) -> None:
    validate_siret_format(siret)

    if db.session.query(models.BusinessUnit.query.filter_by(siret=siret).exists()).scalar():
        raise exceptions.InvalidSiret()

    venue = business_unit.venues[0]
    offerer = venue.managingOfferer

    if not offerer.siren:  # FIXME: while Offerer.siren is nullable
        raise exceptions.InvalidSiret()
    if siret[:9] != offerer.siren:
        raise exceptions.InvalidSiret()


def validate_siret_format(siret: str) -> None:
    if len(siret) != 14:
        raise exceptions.WrongLengthSiret()
    if not siret.isdigit():
        raise exceptions.NotAllDigitSiret()
