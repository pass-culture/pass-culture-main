import csv
from io import StringIO

from sqlalchemy import and_
from sqlalchemy import not_
from sqlalchemy import or_

from pcapi.models import Offerer
from pcapi.models import VenueSQLEntity
from pcapi.utils.human_ids import humanize
from pcapi.utils.logger import logger


CSV_HEADER = [
    "offerer_id",
    "offerer_humanized_id",
    "offerer_siren",
    "offerer_name",
    "venue_id",
    "venue_humanized_id",
    "venue_siret",
    "venue_name",
    "venue_departement"
]


def generate_non_editable_venues_csv():
    logger.info(" START : FIND NON EDITABLE VENUES ")
    offerer_venues = _get_non_editable_venues()
    logger.info(f' CREATING CSV FOR {len(offerer_venues)} NON EDITABLE VENUES')

    csv_lines = [_as_csv_row(offerer_venue) for offerer_venue in offerer_venues]
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_HEADER)
    writer.writerows(csv_lines)

    logger.info(" END : GENERATING CSV ")
    return output.getvalue()


def _get_non_editable_venues():
    offerer_venues = VenueSQLEntity.query.join(Offerer, VenueSQLEntity.managingOffererId == Offerer.id).filter(
        or_(and_(VenueSQLEntity.siret == None, Offerer.siren == None),
            Offerer.name == '',
            Offerer.siren == None,
            not_(VenueSQLEntity.siret.startswith(Offerer.siren)))).with_entities(VenueSQLEntity.id.label('venueId'),
                                                                                 VenueSQLEntity.siret.label(
                                                                                     'venueSiret'),
                                                                                 VenueSQLEntity.departementCode.label(
                                                                                     'venueDepartmentCode'),
                                                                                 VenueSQLEntity.name.label(
                                                                                     'venueName'),
                                                                                 Offerer.id.label('offererId'),
                                                                                 Offerer.siren.label('offererSiren'),
                                                                                 Offerer.name.label(
                                                                                     'offererName')).all()

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
            offerer_venue.venueDepartmentCode
            ]
