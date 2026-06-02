import itertools
import logging
import traceback
from dataclasses import dataclass
from typing import TypedDict

from sqlalchemy import exc as sa_exc

from pcapi.connectors.big_query.queries import event_series as bq_event_series_queries
from pcapi.connectors.big_query.queries.artist import DeltaAction
from pcapi.core.event_series import models as event_series_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


class EventSeriesLog(TypedDict):
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class EventSeriesBatchResult:
    added: int
    updated: int
    removed: int
    skipped: int


class EventSeriesImporter:
    # ------------------------------------------------------------------
    # Delta import
    # ------------------------------------------------------------------

    def run_delta_update(self, batch_size: int = 100) -> None:
        logger.info("Processing delta for EventSeries")
        query = bq_event_series_queries.EventSeriesDeltaQuery()

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
            "Finished processing delta for EventSeries",
            extra={
                "total_added": total_added,
                "total_updated": total_updated,
                "total_removed": total_removed,
                "total_skipped": total_skipped,
            },
        )

    def _process_batch(
        self, batch: tuple[bq_event_series_queries.DeltaEventSeriesModel, ...]
    ) -> EventSeriesBatchResult:
        ids = [item.id for item in batch]
        existing_series = (
            db.session.query(event_series_models.EventSeries).filter(event_series_models.EventSeries.id.in_(ids)).all()
        )
        existing_series_map = {s.id: s for s in existing_series}

        items_to_add: list[event_series_models.EventSeries] = []
        items_to_update: list[bq_event_series_queries.DeltaEventSeriesModel] = []
        ids_to_remove: list[str] = []

        log_added: list[EventSeriesLog] = []
        log_updated: list[EventSeriesLog] = []
        log_removed: list[EventSeriesLog] = []
        log_skipped_existing: list[EventSeriesLog] = []
        log_skipped_update: list[EventSeriesLog] = []
        log_skipped_remove: list[EventSeriesLog] = []

        for delta_item in batch:
            existing = existing_series_map.get(delta_item.id)

            if delta_item.action == DeltaAction.ADD:
                if existing:
                    log_skipped_existing.append({"id": delta_item.id, "name": delta_item.name})
                    continue
                items_to_add.append(self._build_event_series(delta_item))
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
        updated_count = self._bulk_update(items_to_update, existing_series_map)
        removed_count = self._bulk_delete(ids_to_remove)

        if log_added:
            logger.info("EventSeries added in batch", extra={"event_series": log_added})
        if log_updated:
            logger.info("EventSeries updated in batch", extra={"event_series": log_updated})
        if log_removed:
            logger.info("EventSeries removed in batch", extra={"event_series": log_removed})
        if log_skipped_existing:
            logger.info("EventSeries skipped (already exist) in batch", extra={"event_series": log_skipped_existing})
        if log_skipped_update:
            logger.info("EventSeries skipped (update, not found) in batch", extra={"event_series": log_skipped_update})
        if log_skipped_remove:
            logger.info("EventSeries skipped (remove, not found) in batch", extra={"event_series": log_skipped_remove})

        return EventSeriesBatchResult(
            added=added_count,
            updated=updated_count,
            removed=removed_count,
            skipped=len(log_skipped_existing) + len(log_skipped_update) + len(log_skipped_remove),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_event_series(
        self, model: bq_event_series_queries.EventSeriesModel | bq_event_series_queries.DeltaEventSeriesModel
    ) -> event_series_models.EventSeries:
        return event_series_models.EventSeries(
            id=model.id,
            name=model.name,
            description=model.description,
            mediationUuid=model.mediation_uuid,
        )

    @staticmethod
    def _apply_update(
        event_series: event_series_models.EventSeries, delta_model: bq_event_series_queries.DeltaEventSeriesModel
    ) -> None:
        event_series.name = delta_model.name
        event_series.description = delta_model.description
        event_series.mediationUuid = delta_model.mediation_uuid

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    @staticmethod
    def _bulk_save(items: list[event_series_models.EventSeries]) -> int:
        if not items:
            return 0
        try:
            with atomic():
                db.session.add_all(items)
        except sa_exc.IntegrityError:
            logger.warning("Failed to bulk import EventSeries, importing one by one", extra={"count": len(items)})
            return _save_one_by_one(items, "EventSeries")

        logger.info("Successfully imported EventSeries batch", extra={"count": len(items)})
        return len(items)

    @staticmethod
    def _bulk_delete(item_ids: list[str]) -> int:
        if not item_ids:
            return 0
        try:
            with atomic():
                deleted = (
                    db.session.query(event_series_models.EventSeries)
                    .filter(event_series_models.EventSeries.id.in_(item_ids))
                    .delete(synchronize_session=False)
                )
        except Exception as err:
            logger.exception(
                "Failed to bulk delete EventSeries",
                extra={"count": len(item_ids), "error": str(err), "traceback": traceback.format_exc()},
            )
            return 0

        logger.info("Successfully deleted EventSeries batch", extra={"count": deleted})
        return deleted

    def _bulk_update(
        self,
        items: list[bq_event_series_queries.DeltaEventSeriesModel],
        existing_series_map: dict[str, event_series_models.EventSeries],
    ) -> int:
        if not items:
            return 0
        try:
            with atomic():
                for delta_item in items:
                    self._apply_update(existing_series_map[delta_item.id], delta_item)
        except sa_exc.IntegrityError:
            logger.warning("Batch update failed for EventSeries, retrying one by one", extra={"count": len(items)})
            return self._update_one_by_one(items, existing_series_map)

        logger.info("Successfully updated EventSeries batch", extra={"count": len(items)})
        return len(items)

    def _update_one_by_one(
        self,
        items: list[bq_event_series_queries.DeltaEventSeriesModel],
        existing_series_map: dict[str, event_series_models.EventSeries],
    ) -> int:
        count = 0
        for delta_item in items:
            try:
                with atomic():
                    self._apply_update(existing_series_map[delta_item.id], delta_item)
                    count += 1
            except sa_exc.IntegrityError as err:
                logger.exception(
                    "Failed to update individual EventSeries",
                    extra={"event_series_id": delta_item.id, "error": str(err), "traceback": traceback.format_exc()},
                )
        return count


@dataclass(frozen=True, slots=True)
class EventSeriesOfferLinkBatchResult:
    added: int
    removed: int
    skipped: int


class EventSeriesOfferLinkImporter:
    # ------------------------------------------------------------------
    # Delta import
    # ------------------------------------------------------------------

    def run_delta_update(self, batch_size: int = 100) -> None:
        logger.info("Processing delta for EventSeriesOfferLink")
        query = bq_event_series_queries.EventSeriesOfferLinkDeltaQuery()

        total_added = 0
        total_removed = 0
        total_skipped = 0

        for batch in itertools.batched(query.execute(), batch_size):
            result = self._process_batch(batch)
            total_added += result.added
            total_removed += result.removed
            total_skipped += result.skipped

        logger.info(
            "Finished processing delta for EventSeriesOfferLink",
            extra={
                "total_added": total_added,
                "total_removed": total_removed,
                "total_skipped": total_skipped,
            },
        )

    def _process_batch(
        self, batch: tuple[bq_event_series_queries.DeltaEventSeriesOfferLinkModel, ...]
    ) -> EventSeriesOfferLinkBatchResult:
        series_ids = [item.event_series_id for item in batch]
        offer_ids = [item.offer_id for item in batch]

        existing_links = (
            db.session.query(event_series_models.EventSeriesOfferLink)
            .filter(
                event_series_models.EventSeriesOfferLink.eventSeriesId.in_(series_ids),
                event_series_models.EventSeriesOfferLink.offerId.in_(offer_ids),
            )
            .all()
        )
        existing_links_map = {(link.eventSeriesId, link.offerId): link for link in existing_links}

        items_to_add: list[event_series_models.EventSeriesOfferLink] = []
        items_to_remove: list[event_series_models.EventSeriesOfferLink] = []
        skipped_keys: list[dict] = []

        for delta_item in batch:
            existing = existing_links_map.get((delta_item.event_series_id, delta_item.offer_id))

            if delta_item.action == DeltaAction.ADD:
                if existing:
                    skipped_keys.append(
                        {
                            "event_series_id": delta_item.event_series_id,
                            "offer_id": delta_item.offer_id,
                            "reason": "exists",
                        }
                    )
                    continue
                items_to_add.append(self._build_link(delta_item))

            elif delta_item.action == DeltaAction.REMOVE:
                if not existing:
                    skipped_keys.append(
                        {
                            "event_series_id": delta_item.event_series_id,
                            "offer_id": delta_item.offer_id,
                            "reason": "not_found",
                        }
                    )
                    continue
                items_to_remove.append(existing)

            elif delta_item.action == DeltaAction.UPDATE:
                logger.warning(
                    "Update action is not supported for EventSeriesOfferLink, skipping",
                    extra={"event_series_id": delta_item.event_series_id, "offer_id": delta_item.offer_id},
                )

        added_count = self._bulk_save(items_to_add)
        removed_count = self._bulk_delete(items_to_remove)

        if skipped_keys:
            logger.warning(
                "Some EventSeriesOfferLink delta operations could not be applied",
                extra={"skipped_count": len(skipped_keys), "skipped_keys": skipped_keys},
            )

        return EventSeriesOfferLinkBatchResult(
            added=added_count,
            removed=removed_count,
            skipped=len(skipped_keys),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_link(
        model: bq_event_series_queries.EventSeriesOfferLinkModel
        | bq_event_series_queries.DeltaEventSeriesOfferLinkModel,
    ) -> event_series_models.EventSeriesOfferLink:
        return event_series_models.EventSeriesOfferLink(
            eventSeriesId=model.event_series_id,
            offerId=model.offer_id,
        )

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    @staticmethod
    def _bulk_save(items: list[event_series_models.EventSeriesOfferLink]) -> int:
        if not items:
            return 0
        try:
            with atomic():
                db.session.add_all(items)
        except sa_exc.IntegrityError:
            logger.warning(
                "Failed to bulk import EventSeriesOfferLink, importing one by one",
                extra={"count": len(items)},
            )
            return _save_one_by_one(items, "EventSeriesOfferLink")

        logger.info("Successfully imported EventSeriesOfferLink batch", extra={"count": len(items)})
        return len(items)

    @staticmethod
    def _bulk_delete(items: list[event_series_models.EventSeriesOfferLink]) -> int:
        if not items:
            return 0
        item_ids = [item.id for item in items]
        try:
            with atomic():
                deleted = (
                    db.session.query(event_series_models.EventSeriesOfferLink)
                    .filter(event_series_models.EventSeriesOfferLink.id.in_(item_ids))
                    .delete(synchronize_session=False)
                )
        except Exception as err:
            logger.exception(
                "Failed to bulk delete EventSeriesOfferLink",
                extra={"count": len(item_ids), "error": str(err), "traceback": traceback.format_exc()},
            )
            return 0

        logger.info("Successfully deleted EventSeriesOfferLink batch", extra={"count": deleted})
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
