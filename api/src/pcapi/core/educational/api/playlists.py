from dataclasses import dataclass
import logging

import pcapi.connectors.big_query.queries as big_query
from pcapi.connectors.big_query.queries.base import BaseQuery
import pcapi.core.educational.models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)


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


def synchronize_institution_playlist(
    playlist_type: educational_models.PlaylistType,
    institution: educational_models.EducationalInstitution,
    bq_extra_filters: dict,
) -> None:
    bq_extra_filters = {k: v for k, v in bq_extra_filters.items() if v}
    bq_filters = {"institution_id": str(institution.id), **bq_extra_filters}

    ctx = QUERY_DESC[playlist_type]
    new_rows = {int(getattr(row, ctx.bq_attr_name)): row.distance_in_km for row in ctx.query().execute(**bq_filters)}

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


def synchronize_collective_playlist(playlist_type: educational_models.PlaylistType, with_range: bool = False) -> None:
    institutions = educational_models.EducationalInstitution.query.all()
    for institution in institutions:
        try:
            extra_args = _compute_extra_args(institution.ruralLevel, with_range)
            synchronize_institution_playlist(playlist_type, institution, extra_args)
            # Might be a shame that this will clear the initial institution query and will refetch
            # the institution every time. Small price to pay I guess.
            db.session.commit()
        except Exception:  # pylint: disable=broad-except
            logger.exception("Failed to synchronize playlist %s for institution %s", playlist_type, institution)
            db.session.rollback()


def _compute_extra_args(rural_level: educational_models.InstitutionRuralLevel, with_range: bool = False) -> dict:
    if with_range:
        max_range = {
            educational_models.InstitutionRuralLevel.URBAIN_DENSE: 3,
            educational_models.InstitutionRuralLevel.URBAIN_DENSITE_INTERMEDIAIRE: 10,
            educational_models.InstitutionRuralLevel.RURAL_SOUS_FORTE_INFLUENCE_D_UN_POLE: 15,
            educational_models.InstitutionRuralLevel.RURAL_SOUS_FAIBLE_INFLUENCE_D_UN_POLE: 60,
            educational_models.InstitutionRuralLevel.RURAL_AUTONOME_PEU_DENSE: 60,
            educational_models.InstitutionRuralLevel.RURAL_AUTONOME_TRES_PEU_DENSE: 60,
            None: 60,
        }.get(rural_level, 60)
        return {"range": max_range}
    return {}
