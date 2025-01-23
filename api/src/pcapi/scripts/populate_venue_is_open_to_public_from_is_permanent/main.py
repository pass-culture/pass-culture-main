from pcapi.core.offerers import models as offerer_models
from pcapi.models import db


def populate_venue_is_open_to_public_from_is_permanent() -> None:
    batch_size = 500
    venues_count = offerer_models.Venue.query.filter(offerer_models.Venue.isPermanent == True).count()
    batch_num = 0
    while batch_size * batch_num <= venues_count:
        venues = (
            offerer_models.Venue.query.filter(offerer_models.Venue.isPermanent == True)
            .order_by(offerer_models.Venue.id.asc())
            .limit(batch_size)
            .offset(batch_num * batch_size)
            .all()
        )
        for venue in venues:
            venue.isOpenToPublic = True
        batch_num += 1
    db.session.commit()


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()
    populate_venue_is_open_to_public_from_is_permanent()
