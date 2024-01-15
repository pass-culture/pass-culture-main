import logging

import pcapi.connectors.big_query.queries as big_query
import pcapi.core.educational.models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def synchronize_classroom_playlist(
    playlist_type: educational_models.PlaylistType, institution: educational_models.EducationalInstitution
) -> None:
    new_rows = {
        int(row.collective_offer_id): row.distance_in_km
        for row in big_query.ClassroomPlaylistQuery().execute(institution_id=str(institution.id))
    }
    actual_rows = {
        row.collectiveOfferTemplateId: row
        for row in educational_models.CollectivePlaylist.query.filter(
            educational_models.CollectivePlaylist.type == playlist_type,
            educational_models.CollectivePlaylist.institution == institution,
        )
    }

    offer_ids_to_remove = actual_rows.keys() - new_rows.keys()
    offer_ids_to_add = new_rows.keys() - actual_rows.keys()
    offer_ids_to_update = new_rows.keys() & actual_rows.keys()

    playlist_ids_to_remove = [actual_rows[offer_id].id for offer_id in offer_ids_to_remove]

    playlist_items_to_add = [
        {
            "type": playlist_type,
            "institutionId": institution.id,
            "distanceInKm": new_rows[offer_id],
            "collectiveOfferTemplateId": offer_id,
        }
        for offer_id in offer_ids_to_add
    ]

    playlist_items_to_update = [
        {
            "id": actual_rows[offer_id].id,
            "distanceInKm": new_rows[offer_id],
        }
        for offer_id in offer_ids_to_update
        if new_rows[offer_id] != actual_rows[offer_id].distanceInKm
    ]

    if playlist_ids_to_remove:
        educational_models.CollectivePlaylist.query.filter(
            educational_models.CollectivePlaylist.id.in_(playlist_ids_to_remove)
        ).delete()
    if playlist_items_to_add:
        db.session.bulk_insert_mappings(educational_models.CollectivePlaylist, playlist_items_to_add)
    if playlist_items_to_update:
        db.session.bulk_update_mappings(educational_models.CollectivePlaylist, playlist_items_to_update)


def synchronize_classroom_playlists() -> None:
    playlist_type = educational_models.PlaylistType.CLASSROOM
    institutions = educational_models.EducationalInstitution.query.all()
    for institution in institutions:
        try:
            synchronize_classroom_playlist(playlist_type, institution)
            # Might be a shame that this will clear the initial institution query and will refetch
            # the institution every time. Small price to pay I guess.
            db.session.commit()
        except Exception:  # pylint: disable=broad-except
            logger.exception("Failed to synchronize playlist %s for institution %s", playlist_type, institution)
            db.session.rollback()
