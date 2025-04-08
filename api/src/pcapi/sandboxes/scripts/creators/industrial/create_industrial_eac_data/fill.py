from functools import cache

from sqlalchemy import orm as sa_orm

from pcapi.core.educational import models as educational_models
from pcapi.core.geography import api as geography_api
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


def fill_adage_playlists() -> None:
    institutions: list[educational_models.EducationalInstitution] = db.session.query(
        educational_models.EducationalInstitution
    ).all()

    collective_offer_templates: list[educational_models.CollectiveOfferTemplate] = db.session.query(
        educational_models.CollectiveOfferTemplate
    ).all()

    venues: list[offerers_models.Venue] = (
        db.session.query(offerers_models.Venue)
        .join(offerers_models.Venue.collectiveOfferTemplates)
        .options(
            sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(offerers_models.OffererAddress.address)
        )
        .all()
    )

    classroom_offers = [offer for offer in collective_offer_templates if _offer_is_in_school(offer)]

    for institution in institutions:
        playlist_items_to_add = [
            {
                "type": educational_models.PlaylistType.CLASSROOM,
                "institutionId": institution.id,
                # this is supposed to be the distance with another close institution that booked an offer
                # check adage_home_playlist_moving_offerers data table for more details
                "distanceInKm": 5.0,
                "collectiveOfferTemplateId": offer.id,
            }
            for offer in classroom_offers[:10]
        ]
        db.session.bulk_insert_mappings(educational_models.CollectivePlaylist, playlist_items_to_add)

        playlist_items_to_add = [
            {
                "type": educational_models.PlaylistType.LOCAL_OFFERER,
                "institutionId": institution.id,
                "distanceInKm": _compute_distance(venue, institution),
                "venueId": venue.id,
            }
            for venue in venues
        ]
        db.session.bulk_insert_mappings(educational_models.CollectivePlaylist, playlist_items_to_add)

        playlist_items_to_add = [
            {
                "type": educational_models.PlaylistType.NEW_OFFER,
                "institutionId": institution.id,
                "distanceInKm": _compute_distance(offer.venue, institution),
                "collectiveOfferTemplateId": offer.id,
            }
            for offer in collective_offer_templates[:10]
        ]
        db.session.bulk_insert_mappings(educational_models.CollectivePlaylist, playlist_items_to_add)

        playlist_items_to_add = [
            {
                "type": educational_models.PlaylistType.NEW_OFFERER,
                "institutionId": institution.id,
                "distanceInKm": _compute_distance(venue, institution),
                "venueId": venue.id,
            }
            for venue in venues
        ]
        db.session.bulk_insert_mappings(educational_models.CollectivePlaylist, playlist_items_to_add)

    db.session.commit()


def _offer_is_in_school(offer: educational_models.CollectiveOfferTemplate) -> bool:
    """
    offerVenue["addressType"] is the current location field, which will be replaced with locationType
    """
    return (
        offer.offerVenue["addressType"] == educational_models.OfferAddressType.SCHOOL
        or offer.locationType == educational_models.CollectiveLocationType.SCHOOL
    )


@cache
def _compute_distance(venue: offerers_models.Venue, institution: educational_models.EducationalInstitution) -> float:
    assert venue.offererAddress is not None
    assert institution.latitude is not None
    assert institution.longitude is not None

    venue_address = venue.offererAddress.address
    return geography_api.compute_distance(
        first_point=geography_models.Coordinates(latitude=venue_address.latitude, longitude=venue_address.longitude),
        second_point=geography_models.Coordinates(latitude=institution.latitude, longitude=institution.longitude),
    )
