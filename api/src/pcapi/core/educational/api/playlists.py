import logging
import random
import typing
from dataclasses import dataclass

import pcapi.connectors.big_query.queries as big_query
import pcapi.connectors.big_query.queries.adage_playlists as bq_playlists
import pcapi.core.educational.api.institution as institution_api
import pcapi.core.educational.models as educational_models
from pcapi.connectors.big_query.queries.base import BaseQuery
from pcapi.core.educational import repository
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.repository import transaction


logger = logging.getLogger(__name__)


BIGQUERY_PLAYLIST_BATCH_SIZE = 100_000


@dataclass
class QueryCtx:
    query: type[BaseQuery]
    bq_attr_name: str
    bq_attr_formatter: typing.Callable[[str], int]
    local_attr_name: str
    foreign_class: type


def format_collective_offer_id(collective_offer_id: str) -> int:
    # template ids have the form 'template-95710'

    return int(collective_offer_id.split("-")[1])


QUERY_DESC = {
    educational_models.PlaylistType.CLASSROOM: QueryCtx(
        query=big_query.ClassroomPlaylistQuery,
        bq_attr_name="collective_offer_id",
        bq_attr_formatter=format_collective_offer_id,
        local_attr_name="collectiveOfferTemplateId",
        foreign_class=educational_models.CollectiveOfferTemplate,
    ),
    educational_models.PlaylistType.NEW_OFFER: QueryCtx(
        query=big_query.NewTemplateOffersPlaylistQuery,
        bq_attr_name="collective_offer_id",
        bq_attr_formatter=format_collective_offer_id,
        local_attr_name="collectiveOfferTemplateId",
        foreign_class=educational_models.CollectiveOfferTemplate,
    ),
    educational_models.PlaylistType.LOCAL_OFFERER: QueryCtx(
        query=big_query.LocalOfferersQuery,
        bq_attr_name="venue_id",
        bq_attr_formatter=int,
        local_attr_name="venueId",
        foreign_class=offerers_models.Venue,
    ),
    educational_models.PlaylistType.NEW_OFFERER: QueryCtx(
        query=big_query.NewOffererQuery,
        bq_attr_name="venue_id",
        bq_attr_formatter=int,
        local_attr_name="venueId",
        foreign_class=offerers_models.Venue,
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
    new_rows = {ctx.bq_attr_formatter(getattr(row, ctx.bq_attr_name)): row.distance_in_km for row in rows}

    actual_rows = {
        getattr(row, ctx.local_attr_name): row
        for row in db.session.query(educational_models.CollectivePlaylist).filter(
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
        db.session.query(educational_models.CollectivePlaylist).filter(
            educational_models.CollectivePlaylist.id.in_(playlist_ids_to_remove)
        ).delete()
    if playlist_items_to_add:
        # Ensure that objects added to playlist still exist before insertion
        requested_foreign_ids = {item[ctx.local_attr_name] for item in playlist_items_to_add}
        existing_foreign_ids = {
            id_
            for (id_,) in db.session.query(ctx.foreign_class.id).filter(ctx.foreign_class.id.in_(requested_foreign_ids))  # type: ignore[attr-defined]
        }
        playlist_items_to_really_add = filter(
            lambda item: item[ctx.local_attr_name] in existing_foreign_ids,
            playlist_items_to_add,
        )
        db.session.bulk_insert_mappings(educational_models.CollectivePlaylist, playlist_items_to_really_add)
    if playlist_items_to_update:
        db.session.bulk_update_mappings(educational_models.CollectivePlaylist, playlist_items_to_update)


def synchronize_collective_playlist(playlist_type: educational_models.PlaylistType) -> None:
    ctx = QUERY_DESC[playlist_type]
    institution = None
    institution_rows: BigQueryPlaylistModels = []
    for row in ctx.query().execute(page_size=BIGQUERY_PLAYLIST_BATCH_SIZE):
        current_institution_id = int(getattr(row, "institution_id"))
        if institution is None:
            institution = db.session.get(educational_models.EducationalInstitution, current_institution_id)
        if institution.id != current_institution_id:
            try:
                with transaction():
                    synchronize_institution_playlist(playlist_type, institution, institution_rows)
            except Exception:
                logger.exception("Failed to synchronize institution %s playlist from BigQuery", institution.id)
                db.session.rollback()
            institution = db.session.get(educational_models.EducationalInstitution, current_institution_id)
            institution_rows = []
        institution_rows.append(row)
    # Don't forget to synchronize the latest institution
    if institution and institution_rows:
        try:
            with transaction():
                synchronize_institution_playlist(playlist_type, institution, institution_rows)
        except Exception:
            logger.exception("Failed to synchronize institution %s playlist from BigQuery", institution.id)
            db.session.rollback()


def get_playlist_items(
    institution: educational_models.EducationalInstitution,
    playlist_type: educational_models.PlaylistType,
    min_items: int = 10,
) -> typing.Collection[educational_models.CollectivePlaylist]:
    playlist_items = (
        repository.get_collective_offer_templates_for_playlist_query(
            institution_id=institution.id,
            playlist_type=playlist_type,
            max_distance=institution_api.get_playlist_max_distance(institution),
        )
        .distinct(educational_models.CollectivePlaylist.venueId)
        .limit(10)
        .all()
    )

    if len(playlist_items) < min_items:
        missing_count = min_items - len(playlist_items)
        playlist_items += (
            repository.get_collective_offer_templates_for_playlist_query(
                institution_id=institution.id,
                playlist_type=playlist_type,
                min_distance=institution_api.get_playlist_max_distance(institution),
            )
            .distinct(educational_models.CollectivePlaylist.venueId)
            .limit(missing_count)
            .all()
        )

    random.shuffle(playlist_items)
    return playlist_items
