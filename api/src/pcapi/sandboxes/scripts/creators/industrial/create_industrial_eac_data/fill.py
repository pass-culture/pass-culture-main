import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db


def fill_adage_playlists() -> None:
    institutions = list(educational_models.EducationalInstitution.query.all())
    collective_offer_templates = list(educational_models.CollectiveOfferTemplate.query.all())
    venues = list(offerers_models.Venue.query.join(offerers_models.Venue.collectiveOfferTemplates))

    for institution in institutions:
        playlist_items_to_add = [
            {
                "type": educational_models.PlaylistType.CLASSROOM,
                "institutionId": institution.id,
                "distanceInKm": 5.0,
                "collectiveOfferTemplateId": offer.id,
            }
            for offer in collective_offer_templates[:10]
        ]
        db.session.bulk_insert_mappings(educational_models.CollectivePlaylist, playlist_items_to_add)
        playlist_items_to_add = [
            {
                "type": educational_models.PlaylistType.LOCAL_OFFERER,
                "institutionId": institution.id,
                "distanceInKm": 5.0,
                "venueId": venue.id,
            }
            for venue in venues
        ]
        db.session.bulk_insert_mappings(educational_models.CollectivePlaylist, playlist_items_to_add)
        playlist_items_to_add = [
            {
                "type": educational_models.PlaylistType.NEW_OFFER,
                "institutionId": institution.id,
                "distanceInKm": 5.0,
                "collectiveOfferTemplateId": offer.id,
            }
            for offer in collective_offer_templates[:10]
        ]
        db.session.bulk_insert_mappings(educational_models.CollectivePlaylist, playlist_items_to_add)

    db.session.commit()
