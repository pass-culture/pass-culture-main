from pcapi.core.educational import models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


def new_venue(venue: offerers_models.Venue, save: bool = False) -> models.AdageVenueAddress:
    ava = models.AdageVenueAddress(
        venue=venue,
        adageId=venue.adageId,
        adageInscriptionDate=venue.adageInscriptionDate,
    )

    if save:
        db.session.add(ava)
        db.session.commit()

    return ava
