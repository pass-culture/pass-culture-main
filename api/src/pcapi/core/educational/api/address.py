from datetime import datetime
import typing

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
    models.AdageVenueAddress.query.filter_by(venueId=venue_id).delete(synchronize_session=False)


def get_venue_address_by_adage_id(adage_id: str) -> models.AdageVenueAddress | None:
    return models.AdageVenueAddress.query.filter_by(adageId=adage_id).one_or_none()


def unlink_unknown_venue_addresses(known_adage_ids: typing.Collection[str]) -> int:
    """Find unknown AdageVenueAddress (adageId not in known_adage_ids)
    and remove their adageId and adageInscriptionDate.
    """
    count = models.AdageVenueAddress.query.filter(models.AdageVenueAddress.adageId.not_in(known_adage_ids)).update(
        {"adageId": None, "adageInscriptionDate": None}, synchronize_session="evaluate"
    )

    return count


def upsert_venues_addresses(adage_ids_venues: typing.Mapping[str, int]) -> None:
    """Find existing AdageVenueAddress and update them (venueId).
    Create missing AdageVenueAddress.
    """
    existing = models.AdageVenueAddress.query.filter(models.AdageVenueAddress.adageId.in_(adage_ids_venues.keys()))
    existing_ids = {row.adageId for row in existing}

    query = models.AdageVenueAddress.query.filter(models.AdageVenueAddress.adageId.in_(existing_ids))
    for ava in query:
        ava.venueId = adage_ids_venues[ava.adageId]
        db.session.add(ava)

    now = datetime.utcnow()
    missing_ids = adage_ids_venues.keys() - existing_ids
    for missing_id in missing_ids:
        db.session.add(
            models.AdageVenueAddress(venueId=adage_ids_venues[missing_id], adageId=missing_id, adageInscriptionDate=now)
        )
