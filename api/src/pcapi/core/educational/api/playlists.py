from dataclasses import dataclass
import logging

import pcapi.connectors.big_query.queries as big_query
import pcapi.connectors.big_query.queries.adage_playlists as bq_playlists
from pcapi.connectors.big_query.queries.base import BaseQuery
import pcapi.core.educational.models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)


BIGQUERY_PLAYLIST_BATCH_SIZE = 100_000


@dataclass
class QueryCtx:
    query: type[BaseQuery]
    bq_attr_name: str
    local_attr_name: str


QUERY_DESC = {
    educational_models.PlaylistType.CLASSROOM: QueryCtx(
        query=big_query.ClassroomPlaylistQuery,
        bq_attr_name="collective_offer_id",
        local_attr_name="collectiveOfferTemplateId",
    ),
    educational_models.PlaylistType.NEW_OFFER: QueryCtx(
        query=big_query.NewTemplateOffersPlaylistQuery,
        bq_attr_name="collective_offer_id",
        local_attr_name="collectiveOfferTemplateId",
    ),
    educational_models.PlaylistType.LOCAL_OFFERER: QueryCtx(
        query=big_query.LocalOfferersQuery, bq_attr_name="venue_id", local_attr_name="venueId"
    ),
}


BigQueryPlaylistModels = list[
    bq_playlists.ClassroomPlaylistModel | bq_playlists.LocalOfferersModel | bq_playlists.NewTemplateOffersPlaylistModel
]


def synchronize_institution_playlist(
    playlist_type: educational_models.PlaylistType,
    institution: educational_models.EducationalInstitution,
    rows: BigQueryPlaylistModels,
) -> None:
    ctx = QUERY_DESC[playlist_type]
    new_rows = {int(getattr(row, ctx.bq_attr_name)): row.distance_in_km for row in rows}

    actual_rows = {
        getattr(row, ctx.local_attr_name): row
        for row in educational_models.CollectivePlaylist.query.filter(
            educational_models.CollectivePlaylist.type == playlist_type,
            educational_models.CollectivePlaylist.institution == institution,
        )
    }

    item_ids_to_remove = actual_rows.keys() - new_rows.keys()
    item_ids_to_add = new_rows.keys() - actual_rows.keys()
    item_ids_to_update = new_rows.keys() & actual_rows.keys()

    playlist_ids_to_remove = [actual_rows[item_id].id for item_id in item_ids_to_remove]

    playlist_items_to_add = [
        {
            "type": playlist_type,
            "institutionId": institution.id,
            "distanceInKm": new_rows[item_id],
            ctx.local_attr_name: item_id,
        }
        for item_id in item_ids_to_add
    ]

    playlist_items_to_update = [
        {
            "id": actual_rows[item_id].id,
            "distanceInKm": new_rows[item_id],
        }
        for item_id in item_ids_to_update
        if new_rows[item_id] != actual_rows[item_id].distanceInKm
    ]

    if playlist_ids_to_remove:
        educational_models.CollectivePlaylist.query.filter(
            educational_models.CollectivePlaylist.id.in_(playlist_ids_to_remove)
        ).delete()
    if playlist_items_to_add:
        db.session.bulk_insert_mappings(educational_models.CollectivePlaylist, playlist_items_to_add)
    if playlist_items_to_update:
        db.session.bulk_update_mappings(educational_models.CollectivePlaylist, playlist_items_to_update)


def synchronize_collective_playlist(playlist_type: educational_models.PlaylistType) -> None:
    ctx = QUERY_DESC[playlist_type]
    institution = None
    institution_rows: BigQueryPlaylistModels = []
    for row in ctx.query().execute(page_size=BIGQUERY_PLAYLIST_BATCH_SIZE):
        current_institution_id = int(getattr(row, "institution_id"))
        if institution is None:
            institution = educational_models.EducationalInstitution.query.get(current_institution_id)
        if institution.id != current_institution_id:
            try:
                synchronize_institution_playlist(playlist_type, institution, institution_rows)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Failed to synchronize institution %s playlist from BigQuery", institution.id)
                db.session.rollback()
            institution = educational_models.EducationalInstitution.query.get(current_institution_id)
            institution_rows = []
        institution_rows.append(row)
    # Don't forget to synchronize the latest institution
    if institution and institution_rows:
        try:
            synchronize_institution_playlist(playlist_type, institution, institution_rows)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Failed to synchronize institution %s playlist from BigQuery", institution.id)
            db.session.rollback()
