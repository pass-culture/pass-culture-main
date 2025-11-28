"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-39013-create_venue_locations \
  -f NAMESPACE=create_venue_locations \
  -f SCRIPT_ARGUMENTS="";

"""

import logging

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.app import app
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


@atomic()
def _create_venue_locations(max_venues: int) -> int:
    venues = (
        db.session.query(offerers_models.Venue)
        .join(offerers_models.Venue.offererAddress)
        .filter(
            sa.or_(
                offerers_models.OffererAddress.type.is_(None),
                offerers_models.OffererAddress.type == offerers_models.LocationType.OFFER_LOCATION,
            )
        )
        .options(sa_orm.contains_eager(offerers_models.Venue.offererAddress))
        .order_by(offerers_models.Venue.id)
        .limit(max_venues)
        .all()
    )

    for venue in venues:
        offerer_address = offerers_models.OffererAddress(
            label=None,  # venue.common_name later, but code should be updated to synchronize label with publicName
            addressId=venue.offererAddress.addressId,
            offererId=venue.managingOffererId,
            type=offerers_models.LocationType.VENUE_LOCATION,
            venueId=venue.id,
        )
        db.session.add(offerer_address)
        db.session.flush()
        venue.offererAddressId = offerer_address.id
        db.session.add(venue)

    return len(venues)


if __name__ == "__main__":
    app.app_context().push()

    while (count_processed := _create_venue_locations(100)) > 0:
        logger.info("create_venue_locations: %d venues processed", count_processed)
