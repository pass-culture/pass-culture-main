import itertools
import logging
import traceback
from dataclasses import dataclass
from dataclasses import field
from typing import Sequence
from typing import TypeVar
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
    name: str | None


@dataclass(frozen=True, slots=True)
class EventSeriesBatchResult:
    added: int
    updated: int
    removed: int
    skipped: int


@dataclass
class EventSeriesImportLogs:
    added: list[EventSeriesLog] = field(default_factory=list)
    updated: list[EventSeriesLog] = field(default_factory=list)
    removed: list[EventSeriesLog] = field(default_factory=list)
    skipped_existing: list[EventSeriesLog] = field(default_factory=list)
    skipped_update: list[EventSeriesLog] = field(default_factory=list)
    skipped_remove: list[EventSeriesLog] = field(default_factory=list)


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
        existing_series = db.session.query(event_series_models.EventSeries).filter(
            event_series_models.EventSeries.id.in_(ids)
        )
        existing_series_map = {s.id: s for s in existing_series}

        items_to_add: list[event_series_models.EventSeries] = []
        items_to_update: list[bq_event_series_queries.DeltaEventSeriesModel] = []
        ids_to_remove: list[str] = []

        logs = EventSeriesImportLogs()

        for delta_item in batch:
            existing = existing_series_map.get(delta_item.id)

            if delta_item.action == DeltaAction.ADD:
                if existing:
                    logs.skipped_existing.append({"id": delta_item.id, "name": delta_item.name})
                    continue
                items_to_add.append(self._build_event_series(delta_item))
                logs.added.append({"id": delta_item.id, "name": delta_item.name})

            elif delta_item.action == DeltaAction.UPDATE:
                if not existing:
                    logs.skipped_update.append({"id": delta_item.id, "name": delta_item.name})
                    continue
                items_to_update.append(delta_item)
                logs.updated.append({"id": delta_item.id, "name": delta_item.name})

            elif delta_item.action == DeltaAction.REMOVE:
                if not existing:
                    logs.skipped_remove.append({"id": delta_item.id, "name": delta_item.name})
                    continue
                ids_to_remove.append(existing.id)
                logs.removed.append({"id": delta_item.id, "name": existing.name})

        added_count = _bulk_save(items_to_add, event_series_models.EventSeries)
        updated_count = self._bulk_update(items_to_update, existing_series_map)
        removed_count = _bulk_delete(event_series_models.EventSeries, ids_to_remove)

        if logs.added:
            logger.info("EventSeries added in batch", extra={"event_series": logs.added})
        if logs.updated:
            logger.info("EventSeries updated in batch", extra={"event_series": logs.updated})
        if logs.removed:
            logger.info("EventSeries removed in batch", extra={"event_series": logs.removed})
        if logs.skipped_existing:
            logger.info("EventSeries skipped (already exist) in batch", extra={"event_series": logs.skipped_existing})
        if logs.skipped_update:
            logger.info("EventSeries skipped (update, not found) in batch", extra={"event_series": logs.skipped_update})
        if logs.skipped_remove:
            logger.info("EventSeries skipped (remove, not found) in batch", extra={"event_series": logs.skipped_remove})

        return EventSeriesBatchResult(
            added=added_count,
            updated=updated_count,
            removed=removed_count,
            skipped=len(logs.skipped_existing) + len(logs.skipped_update) + len(logs.skipped_remove),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_event_series(
        self, model: bq_event_series_queries.EventSeriesModel | bq_event_series_queries.DeltaEventSeriesModel
    ) -> event_series_models.EventSeries:
        assert model.name is not None  # only "remove" rows may have no name, and those never reach this method
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
        assert delta_model.name is not None  # only "remove" rows may have no name, and those never reach this method
        event_series.name = delta_model.name
        event_series.description = delta_model.description
        event_series.mediationUuid = delta_model.mediation_uuid

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

        existing_links = db.session.query(event_series_models.EventSeriesOfferLink).filter(
            event_series_models.EventSeriesOfferLink.eventSeriesId.in_(series_ids),
            event_series_models.EventSeriesOfferLink.offerId.in_(offer_ids),
        )
        existing_links_map = {(link.eventSeriesId, link.offerId): link for link in existing_links}

        items_to_add: list[event_series_models.EventSeriesOfferLink] = []
        ids_to_remove: list[int] = []
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
                ids_to_remove.append(existing.id)

            elif delta_item.action == DeltaAction.UPDATE:
                logger.warning(
                    "Update action is not supported for EventSeriesOfferLink, skipping",
                    extra={"event_series_id": delta_item.event_series_id, "offer_id": delta_item.offer_id},
                )

        added_count = _bulk_save(items_to_add, event_series_models.EventSeriesOfferLink)
        removed_count = _bulk_delete(event_series_models.EventSeriesOfferLink, ids_to_remove)

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
# Shared helpers
# ------------------------------------------------------------------


T = TypeVar("T", event_series_models.EventSeries, event_series_models.EventSeriesOfferLink)


def _save_one_by_one(
    items: Sequence[T],
    model_class: type[T],
) -> int:
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
            extra={"class_name": model_class.__name__, "error_count": len(errors), "errors": errors},
        )
    return count


def _bulk_save(
    items: Sequence[T],
    model_class: type[T],
) -> int:
    if not items:
        return 0
    try:
        with atomic():
            db.session.add_all(items)
    except sa_exc.IntegrityError:
        logger.warning(
            "Failed to bulk import %s, importing one by one",
            model_class.__name__,
            extra={"count": len(items)},
        )
        return _save_one_by_one(items, model_class)

    logger.info("Successfully imported %s batch", model_class.__name__, extra={"count": len(items)})
    return len(items)


def _bulk_delete(
    model_class: type[event_series_models.EventSeries | event_series_models.EventSeriesOfferLink],
    item_ids: Sequence[str] | Sequence[int],
) -> int:
    if not item_ids:
        return 0
    try:
        with atomic():
            deleted = (
                db.session.query(model_class).filter(model_class.id.in_(item_ids)).delete(synchronize_session=False)
            )
    except Exception as err:
        logger.exception(
            "Failed to bulk delete %s",
            model_class.__name__,
            extra={"count": len(item_ids), "error": str(err), "traceback": traceback.format_exc()},
        )
        return 0

    logger.info("Successfully deleted %s batch", model_class.__name__, extra={"count": deleted})
    return deleted
