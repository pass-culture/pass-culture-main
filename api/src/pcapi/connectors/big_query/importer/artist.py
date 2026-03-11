import itertools
import logging
import traceback
from dataclasses import dataclass
from typing import TypedDict

from sqlalchemy import exc as sa_exc

from pcapi import settings
from pcapi.connectors.big_query.queries import artist as bq_artist_queries
from pcapi.connectors.big_query.queries.artist import DeltaAction
from pcapi.core.artist import models as artist_models
from pcapi.core.artist.utils import get_artist_type
from pcapi.core.artist.utils import sanitize_author_html
from pcapi.core.object_storage.backends.gcp import GCPBackend
from pcapi.core.object_storage.backends.gcp import GCPData
from pcapi.core.object_storage.backends.utils import copy_file_between_storage_backends
from pcapi.models import db
from pcapi.utils.repository import atomic


logger = logging.getLogger(__name__)


class ArtistLog(TypedDict):
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class ArtistBatchResult:
    added: int
    updated: int
    removed: int
    skipped: int


class ArtistImporter:
    def __init__(self) -> None:
        self.gcp_data = GCPData()
        self.gcp_backend = GCPBackend()

    # ------------------------------------------------------------------
    # Delta import
    # ------------------------------------------------------------------

    def run_delta_update(self, batch_size: int = 100) -> None:
        logger.info("Processing delta for Artist")
        query = bq_artist_queries.ArtistDeltaQuery()

        total_added = 0
        total_updated = 0
        total_removed = 0
        total_skipped = 0

        for batch in itertools.batched(query.execute(), batch_size):
            result = self._process_batch(batch)
            total_added += result.added
            total_updated += result.updated
            total_removed += result.removed
            total_skipped += result.skipped

        logger.info(
            "Finished processing delta for Artist",
            extra={
                "total_added": total_added,
                "total_updated": total_updated,
                "total_removed": total_removed,
                "total_skipped": total_skipped,
            },
        )

    def _process_batch(self, batch: tuple[bq_artist_queries.DeltaArtistModel, ...]) -> ArtistBatchResult:
        ids = [item.id for item in batch]
        existing_artists = db.session.query(artist_models.Artist).filter(artist_models.Artist.id.in_(ids)).all()
        existing_artists_map = {a.id: a for a in existing_artists}

        wikidata_ids_to_check = {
            item.wikidata_id for item in batch if item.action == DeltaAction.ADD and item.wikidata_id
        }
        existing_wikidata_ids = set()
        if wikidata_ids_to_check:
            existing_wikidata_ids = {
                wikidata_id
                for (wikidata_id,) in db.session.query(artist_models.Artist.wikidata_id)
                .filter(artist_models.Artist.wikidata_id.in_(wikidata_ids_to_check))
                .tuples()
                .all()
            }

        items_to_add: list[artist_models.Artist] = []
        items_to_update: list[bq_artist_queries.DeltaArtistModel] = []
        ids_to_remove: list[str] = []

        log_added: list[ArtistLog] = []
        log_updated: list[ArtistLog] = []
        log_removed: list[ArtistLog] = []
        log_skipped_existing: list[ArtistLog] = []
        log_skipped_wikidata: list[ArtistLog] = []
        log_skipped_update: list[ArtistLog] = []
        log_skipped_remove: list[ArtistLog] = []

        for delta_item in batch:
            existing = existing_artists_map.get(delta_item.id)

            if delta_item.action == DeltaAction.ADD:
                if existing:
                    log_skipped_existing.append({"id": delta_item.id, "name": delta_item.name})
                    continue
                if delta_item.wikidata_id and delta_item.wikidata_id in existing_wikidata_ids:
                    log_skipped_wikidata.append({"id": delta_item.id, "name": delta_item.name})
                    continue
                items_to_add.append(self._build_artist(delta_item))
                log_added.append({"id": delta_item.id, "name": delta_item.name})

            elif delta_item.action == DeltaAction.UPDATE:
                if not existing:
                    log_skipped_update.append({"id": delta_item.id, "name": delta_item.name})
                    continue
                items_to_update.append(delta_item)
                log_updated.append({"id": delta_item.id, "name": delta_item.name})

            elif delta_item.action == DeltaAction.REMOVE:
                if not existing:
                    log_skipped_remove.append({"id": delta_item.id, "name": delta_item.name})
                    continue
                ids_to_remove.append(existing.id)
                log_removed.append({"id": delta_item.id, "name": existing.name})

        added_count = self._bulk_save(items_to_add)
        updated_count = self._bulk_update(items_to_update, existing_artists_map)
        removed_count = self._bulk_delete(ids_to_remove)

        if log_added:
            logger.info("Artists added in batch", extra={"artists": log_added})
        if log_updated:
            logger.info("Artists updated in batch", extra={"artists": log_updated})
        if log_removed:
            logger.info("Artists removed in batch", extra={"artists": log_removed})
        if log_skipped_existing:
            logger.info("Artists skipped (already exist) in batch", extra={"artists": log_skipped_existing})
        if log_skipped_wikidata:
            logger.info("Artists skipped (duplicate wikidata_id) in batch", extra={"artists": log_skipped_wikidata})
        if log_skipped_update:
            logger.info("Artists skipped (update, not found) in batch", extra={"artists": log_skipped_update})
        if log_skipped_remove:
            logger.info("Artists skipped (remove, not found) in batch", extra={"artists": log_skipped_remove})

        return ArtistBatchResult(
            added=added_count,
            updated=updated_count,
            removed=removed_count,
            skipped=len(log_skipped_existing)
            + len(log_skipped_wikidata)
            + len(log_skipped_update)
            + len(log_skipped_remove),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_artist(
        self, model: bq_artist_queries.ArtistModel | bq_artist_queries.DeltaArtistModel
    ) -> artist_models.Artist:
        mediation_uuid = None
        if model.mediation_uuid:
            mediation_uuid = copy_file_between_storage_backends(
                source_storage=self.gcp_data,
                destination_storage=self.gcp_backend,
                source_folder=settings.DATA_ARTIST_THUMBS_FOLDER_NAME,
                destination_folder=settings.ARTIST_THUMBS_FOLDER_NAME,
                file_id=model.mediation_uuid,
            )

        return artist_models.Artist(
            id=model.id,
            name=model.name,
            description=model.description,
            image=model.image,
            image_author=sanitize_author_html(model.image_author),
            image_license=model.image_license,
            image_license_url=model.image_license_url,
            wikidata_id=model.wikidata_id,
            biography=model.biography,
            wikipedia_url=model.wikipedia_url,
            mediation_uuid=mediation_uuid,
        )

    @staticmethod
    def _apply_update(artist: artist_models.Artist, delta_model: bq_artist_queries.DeltaArtistModel) -> None:
        artist.name = delta_model.name
        artist.description = delta_model.description
        artist.image = delta_model.image
        artist.image_author = sanitize_author_html(delta_model.image_author)
        artist.image_license = delta_model.image_license
        artist.image_license_url = delta_model.image_license_url
        artist.wikidata_id = delta_model.wikidata_id
        artist.biography = delta_model.biography
        artist.wikipedia_url = delta_model.wikipedia_url

    def _apply_update_with_mediation(
        self, artist: artist_models.Artist, delta_model: bq_artist_queries.DeltaArtistModel
    ) -> None:
        self._apply_update(artist, delta_model)
        if delta_model.mediation_uuid and delta_model.mediation_uuid != artist.mediation_uuid:
            artist.mediation_uuid = copy_file_between_storage_backends(
                source_storage=self.gcp_data,
                destination_storage=self.gcp_backend,
                source_folder=settings.DATA_ARTIST_THUMBS_FOLDER_NAME,
                destination_folder=settings.ARTIST_THUMBS_FOLDER_NAME,
                file_id=delta_model.mediation_uuid,
            )

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    @staticmethod
    def _bulk_save(items: list[artist_models.Artist]) -> int:
        if not items:
            return 0
        try:
            with atomic():
                db.session.add_all(items)
        except sa_exc.IntegrityError:
            logger.warning("Failed to bulk import Artist, importing one by one", extra={"count": len(items)})
            return _save_one_by_one(items, "Artist")

        logger.info("Successfully imported Artist batch", extra={"count": len(items)})
        return len(items)

    @staticmethod
    def _bulk_delete(item_ids: list[str]) -> int:
        if not item_ids:
            return 0
        try:
            with atomic():
                deleted = (
                    db.session.query(artist_models.Artist)
                    .filter(artist_models.Artist.id.in_(item_ids))
                    .delete(synchronize_session=False)
                )
        except Exception as err:
            logger.exception(
                "Failed to bulk delete Artist",
                extra={"count": len(item_ids), "error": str(err), "traceback": traceback.format_exc()},
            )
            return 0

        logger.info("Successfully deleted Artist batch", extra={"count": deleted})
        return deleted

    def _bulk_update(
        self, items: list[bq_artist_queries.DeltaArtistModel], existing_artists_map: dict[str, artist_models.Artist]
    ) -> int:
        if not items:
            return 0
        try:
            with atomic():
                for delta_item in items:
                    self._apply_update_with_mediation(existing_artists_map[delta_item.id], delta_item)
        except sa_exc.IntegrityError:
            logger.warning("Batch update failed for Artist, retrying one by one", extra={"count": len(items)})
            return self._update_one_by_one(items, existing_artists_map)

        logger.info("Successfully updated Artist batch", extra={"count": len(items)})
        return len(items)

    def _update_one_by_one(
        self, items: list[bq_artist_queries.DeltaArtistModel], existing_artists_map: dict[str, artist_models.Artist]
    ) -> int:
        count = 0
        for delta_item in items:
            try:
                with atomic():
                    self._apply_update_with_mediation(existing_artists_map[delta_item.id], delta_item)
                    count += 1
            except sa_exc.IntegrityError as err:
                logger.exception(
                    "Failed to update individual Artist",
                    extra={"artist_id": delta_item.id, "error": str(err), "traceback": traceback.format_exc()},
                )
        return count


@dataclass(frozen=True, slots=True)
class ArtistProductLinkBatchResult:
    added: int
    removed: int
    skipped: int


class ArtistProductLinkImporter:
    # ------------------------------------------------------------------
    # Delta import
    # ------------------------------------------------------------------

    def run_delta_update(self, batch_size: int = 100) -> None:
        logger.info("Processing delta for ArtistProductLink")
        query = bq_artist_queries.ArtistProductLinkDeltaQuery()

        total_added = 0
        total_removed = 0
        total_skipped = 0

        for batch in itertools.batched(query.execute(), batch_size):
            result = self._process_batch(batch)
            total_added += result.added
            total_removed += result.removed
            total_skipped += result.skipped

        logger.info(
            "Finished processing delta for ArtistProductLink",
            extra={
                "total_added": total_added,
                "total_removed": total_removed,
                "total_skipped": total_skipped,
            },
        )

    def _process_batch(
        self, batch: tuple[bq_artist_queries.DeltaArtistProductLinkModel, ...]
    ) -> ArtistProductLinkBatchResult:
        artist_ids = [item.artist_id for item in batch]
        product_ids = [item.product_id for item in batch]

        existing_links = (
            db.session.query(artist_models.ArtistProductLink)
            .filter(
                artist_models.ArtistProductLink.artist_id.in_(artist_ids),
                artist_models.ArtistProductLink.product_id.in_(product_ids),
            )
            .all()
        )
        existing_links_map = {(link.artist_id, link.product_id, link.artist_type): link for link in existing_links}

        items_to_add: list[artist_models.ArtistProductLink] = []
        items_to_remove: list[artist_models.ArtistProductLink] = []
        skipped_keys: list[dict] = []

        for delta_item in batch:
            existing = existing_links_map.get(
                (delta_item.artist_id, delta_item.product_id, get_artist_type(delta_item.artist_type))
            )

            if delta_item.action == DeltaAction.ADD:
                if existing:
                    skipped_keys.append(
                        {"artist_id": delta_item.artist_id, "product_id": delta_item.product_id, "reason": "exists"}
                    )
                    continue
                items_to_add.append(self._build_link(delta_item))

            elif delta_item.action == DeltaAction.REMOVE:
                if not existing:
                    skipped_keys.append(
                        {"artist_id": delta_item.artist_id, "product_id": delta_item.product_id, "reason": "not_found"}
                    )
                    continue
                items_to_remove.append(existing)

            elif delta_item.action == DeltaAction.UPDATE:
                logger.warning(
                    "Update action is not supported for ArtistProductLink, skipping",
                    extra={"artist_id": delta_item.artist_id, "product_id": delta_item.product_id},
                )

        added_count = self._bulk_save(items_to_add)
        removed_count = self._bulk_delete(items_to_remove)

        if skipped_keys:
            logger.warning(
                "Some ArtistProductLink delta operations could not be applied",
                extra={"skipped_count": len(skipped_keys), "skipped_keys": skipped_keys},
            )

        return ArtistProductLinkBatchResult(
            added=added_count,
            removed=removed_count,
            skipped=len(skipped_keys),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_link(
        model: bq_artist_queries.ArtistProductLinkModel | bq_artist_queries.DeltaArtistProductLinkModel,
    ) -> artist_models.ArtistProductLink:
        return artist_models.ArtistProductLink(
            artist_id=model.artist_id,
            product_id=model.product_id,
            artist_type=get_artist_type(model.artist_type),
        )

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    @staticmethod
    def _bulk_save(items: list[artist_models.ArtistProductLink]) -> int:
        if not items:
            return 0
        try:
            with atomic():
                db.session.add_all(items)
        except sa_exc.IntegrityError:
            logger.warning(
                "Failed to bulk import ArtistProductLink, importing one by one",
                extra={"count": len(items)},
            )
            return _save_one_by_one(items, "ArtistProductLink")

        logger.info("Successfully imported ArtistProductLink batch", extra={"count": len(items)})
        return len(items)

    @staticmethod
    def _bulk_delete(items: list[artist_models.ArtistProductLink]) -> int:
        if not items:
            return 0
        item_ids = [item.id for item in items]
        try:
            with atomic():
                deleted = (
                    db.session.query(artist_models.ArtistProductLink)
                    .filter(artist_models.ArtistProductLink.id.in_(item_ids))
                    .delete(synchronize_session=False)
                )
        except Exception as err:
            logger.exception(
                "Failed to bulk delete ArtistProductLink",
                extra={"count": len(item_ids), "error": str(err), "traceback": traceback.format_exc()},
            )
            return 0

        logger.info("Successfully deleted ArtistProductLink batch", extra={"count": deleted})
        return deleted


# ------------------------------------------------------------------
# Shared helpers
# ------------------------------------------------------------------


def _save_one_by_one(items: list, class_name: str) -> int:
    count = 0
    errors: list[str] = []
    for item in items:
        try:
            with atomic():
                db.session.add(item)
            count += 1
        except sa_exc.IntegrityError as exc:
            errors.append(str(exc))

    if errors:
        logger.warning(
            "Some items could not be imported individually",
            extra={"class_name": class_name, "error_count": len(errors), "errors": errors},
        )
    return count
