import csv
from io import StringIO
import logging

from sqlalchemy import and_
from sqlalchemy import not_
from sqlalchemy import or_

from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.utils.human_ids import humanize


logger = logging.getLogger(__name__)


CSV_HEADER = [
    "offerer_id",
    "offerer_humanized_id",
    "offerer_siren",
    "offerer_name",
    "venue_id",
    "venue_humanized_id",
    "venue_siret",
    "venue_name",
    "venue_departement",
]


def generate_non_editable_venues_csv():
    logger.info(" START : FIND NON EDITABLE VENUES ")
    offerer_venues = _get_non_editable_venues()
    logger.info(" CREATING CSV FOR %i NON EDITABLE VENUES", len(offerer_venues))

    csv_lines = [_as_csv_row(offerer_venue) for offerer_venue in offerer_venues]
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_HEADER)
    writer.writerows(csv_lines)

    logger.info(" END : GENERATING CSV ")
    return output.getvalue()


def _get_non_editable_venues():
    offerer_venues = (
        Venue.query.join(Offerer, Venue.managingOffererId == Offerer.id)
        .filter(
            or_(
                and_(Venue.siret.is_(None), Offerer.siren.is_(None)),
                Offerer.name == "",
                Offerer.siren.is_(None),
                not_(Venue.siret.startswith(Offerer.siren)),
            )
        )
        .with_entities(
            Venue.id.label("venueId"),
            Venue.siret.label("venueSiret"),
            Venue.departementCode.label("venueDepartmentCode"),
            Venue.name.label("venueName"),
            Offerer.id.label("offererId"),
            Offerer.siren.label("offererSiren"),
            Offerer.name.label("offererName"),
        )
        .all()
    )

    return offerer_venues


def _as_csv_row(offerer_venue):
    return [
        offerer_venue.offererId,
        humanize(offerer_venue.offererId),
        offerer_venue.offererSiren,
        offerer_venue.offererName,
        offerer_venue.venueId,
        humanize(offerer_venue.venueId),
        offerer_venue.venueSiret,
        offerer_venue.venueName,
        offerer_venue.venueDepartmentCode,
    ]
