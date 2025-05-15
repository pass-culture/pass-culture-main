import typing
from datetime import datetime

import sqlalchemy as sa

from pcapi.core.educational import models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


def new_venue_address(venue: offerers_models.Venue) -> models.AdageVenueAddress:
    ava = models.AdageVenueAddress(
        venue=venue,
        adageId=venue.adageId,
        adageInscriptionDate=venue.adageInscriptionDate,
    )

    db.session.add(ava)
    return ava


def delete_venue_address(venue_id: int) -> None:
    db.session.query(models.AdageVenueAddress).filter_by(venueId=venue_id).delete(synchronize_session=False)


def get_venue_address_by_adage_id(adage_id: str) -> models.AdageVenueAddress | None:
    return db.session.query(models.AdageVenueAddress).filter_by(adageId=adage_id).one_or_none()


def unlink_deactivated_venue_addresses(deactivated_adage_venues_ids: typing.Mapping[str, int]) -> int:
    """Find deactivated AdageVenueAddress rows and remove their adageId
    and adageInscriptionDate.
    """
    adage_ids = set(deactivated_adage_venues_ids.keys())
    venue_ids = set(deactivated_adage_venues_ids.values())

    return (
        db.session.query(models.AdageVenueAddress)
        .filter(
            sa.or_(
                models.AdageVenueAddress.adageId.in_(adage_ids),
                models.AdageVenueAddress.venueId.in_(venue_ids),
            )
        )
        .update({"adageId": None, "adageInscriptionDate": None}, synchronize_session="evaluate")
    )


def upsert_venues_addresses(adage_ids_venues: typing.Mapping[str, int]) -> None:
    """Find existing AdageVenueAddress and update them (venueId).
    Create missing AdageVenueAddress.
    """
    existing = db.session.query(models.AdageVenueAddress).filter(
        models.AdageVenueAddress.adageId.in_(adage_ids_venues.keys())
    )
    existing_ids = {row.adageId for row in existing}

    query = db.session.query(models.AdageVenueAddress).filter(models.AdageVenueAddress.adageId.in_(existing_ids))
    for ava in query:
        ava.venueId = adage_ids_venues[ava.adageId]
        db.session.add(ava)

    now = datetime.utcnow()
    missing_ids = adage_ids_venues.keys() - existing_ids
    for missing_id in missing_ids:
        db.session.add(
            models.AdageVenueAddress(venueId=adage_ids_venues[missing_id], adageId=missing_id, adageInscriptionDate=now)
        )
