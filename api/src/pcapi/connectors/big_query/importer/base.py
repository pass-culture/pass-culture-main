import abc
import enum
import logging
from typing import Any
from typing import Protocol
from typing import Type

from sqlalchemy import exc as sa_exc

from pcapi.connectors.big_query.queries.base import BaseQuery
from pcapi.models import db
from pcapi.utils.repository import transaction


logger = logging.getLogger(__name__)
BATCH_SIZE = 1000


class HasId(Protocol):
    id: Any


class DeltaAction(str, enum.Enum):
    ADD = "add"
    REMOVE = "remove"
    UPDATE = "update"


class AbstractImporter[BigQueryModel, BigQueryDeltaModel, SQLAlchemyModel: HasId](abc.ABC):
    def import_all(self) -> None:
        class_name = self.get_sqlalchemy_class().__name__
        logger.info(f"Starting full import for {class_name}")

        imported_items = []
        query = self.get_full_import_query()

        for bq_item in query.execute():
            if self.exists(bq_item):
                continue

            new_sqlalchemy_obj = self.create(bq_item)
            imported_items.append(new_sqlalchemy_obj)

            if len(imported_items) >= BATCH_SIZE:
                self._bulk_save(imported_items)
                imported_items = []

        self._bulk_save(imported_items)
        logger.info(f"Finished full import for {class_name}")

    def run_delta_update(self) -> None:
        class_name = self.get_sqlalchemy_class().__name__
        logger.info(f"Processing delta for {class_name}")

        items_to_add = []
        items_to_update = []
        items_to_remove = []
        query = self.get_delta_import_query()
        for delta_item in query.execute():
            sqlalchemy_obj = self.exists(delta_item)
            if delta_item.action == DeltaAction.ADD:
                if not sqlalchemy_obj:
                    items_to_add.append(self.create(delta_item))

            elif delta_item.action == DeltaAction.UPDATE:
                if sqlalchemy_obj:
                    items_to_update.append((sqlalchemy_obj.id, delta_item))

            elif delta_item.action == DeltaAction.REMOVE:
                if sqlalchemy_obj:
                    items_to_remove.append(sqlalchemy_obj)

            if len(items_to_add) >= BATCH_SIZE:
                self._bulk_save(items_to_add)
                items_to_add = []

            if len(items_to_remove) >= BATCH_SIZE:
                self._handle_removals(items_to_remove)
                items_to_remove = []

            if len(items_to_update) >= BATCH_SIZE:
                self._handle_updates(items_to_update)
                items_to_update = []

        self._bulk_save(items_to_add)
        self._handle_removals(items_to_remove)
        self._handle_updates(items_to_update)

        logger.info(f"Finished processing delta for {class_name}")

    def _bulk_save(self, items: list[SQLAlchemyModel]) -> None:
        if not items:
            return
        class_name = self.get_sqlalchemy_class().__name__
        try:
            with transaction():
                db.session.add_all(items)
            logger.info(f"Successfully imported {len(items)} {class_name}")
        except sa_exc.IntegrityError as exc:
            logger.warning(f"Failed to bulk import {class_name}: {exc}. Importing one by one.")
            db.session.rollback()
            self._save_one_by_one(items)

    def _save_one_by_one(self, items: list[SQLAlchemyModel]) -> None:
        class_name = self.get_sqlalchemy_class().__name__
        for item in items:
            try:
                with transaction():
                    db.session.add(item)
            except sa_exc.IntegrityError as exc:
                logger.error(f"Failed to import item for {class_name}: {exc}")

    def _handle_removals(self, items_to_remove: list[SQLAlchemyModel]) -> None:
        if not items_to_remove:
            return

        pks_to_delete = [item.id for item in items_to_remove]
        self._bulk_delete(pks_to_delete)

    def _bulk_delete(self, pks: list) -> None:
        if not pks:
            return
        model_class = self.get_sqlalchemy_class()
        try:
            with transaction():
                query = db.session.query(model_class).filter(model_class.id.in_(pks))
                deleted_count = query.delete(synchronize_session=False)
                logger.info(f"Successfully deleted {deleted_count} {model_class.__name__}")
        except Exception as e:
            logger.error(f"Failed to bulk delete {model_class.__name__}: {e}", exc_info=True)
            db.session.rollback()

    def _handle_updates(self, items: list[tuple[Any, BigQueryDeltaModel]]) -> None:
        if not items:
            return

        class_name = self.get_sqlalchemy_class().__name__
        object_ids = [item_id for item_id, _ in items]
        try:
            with transaction():
                objects_map = {
                    obj.id: obj
                    for obj in db.session.query(self.get_sqlalchemy_class()).filter(
                        self.get_sqlalchemy_class().id.in_(object_ids)
                    )
                }
                for item_id, delta_item in items:
                    if item_id in objects_map:
                        self.update(objects_map[item_id], delta_item)
                logger.info(f"Committing a batch of {len(items)} updates for {class_name}.")

        except sa_exc.IntegrityError as exc:
            logger.warning(f"Batch update failed for {class_name}: {exc}. Retrying one by one.")
            db.session.rollback()
            self._update_one_by_one(items)

    def _update_one_by_one(self, items: list[tuple[Any, BigQueryDeltaModel]]) -> None:
        class_name = self.get_sqlalchemy_class().__name__
        for item_id, delta_item in items:
            try:
                with transaction():
                    sqlalchemy_obj = db.session.query(self.get_sqlalchemy_class()).get(item_id)
                    if sqlalchemy_obj:
                        self.update(sqlalchemy_obj, delta_item)
            except sa_exc.IntegrityError as exc:
                logger.error(f"Failed to update individual {class_name} (id: {item_id}): {exc}")

    @abc.abstractmethod
    def get_sqlalchemy_class(self) -> Type[SQLAlchemyModel]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_full_import_query(self) -> BaseQuery:
        raise NotImplementedError

    @abc.abstractmethod
    def get_delta_import_query(self) -> BaseQuery:
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, model: BigQueryModel | BigQueryDeltaModel) -> SQLAlchemyModel | None:
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, model: BigQueryModel | BigQueryDeltaModel) -> SQLAlchemyModel:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, sqlalchemy_obj: SQLAlchemyModel, delta_model: BigQueryDeltaModel) -> None:
        raise NotImplementedError
