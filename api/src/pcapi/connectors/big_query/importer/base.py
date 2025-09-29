import abc
import enum
import logging
import typing
from typing import Any
from typing import Generic
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


BigQueryModel = typing.TypeVar("BigQueryModel")
BigQueryDeltaModel = typing.TypeVar("BigQueryDeltaModel")
SQLAlchemyModel = typing.TypeVar("SQLAlchemyModel", bound=HasId)


class DeltaAction(str, enum.Enum):
    ADD = "add"
    REMOVE = "remove"
    UPDATE = "update"


class AbstractImporter(abc.ABC, Generic[BigQueryModel, BigQueryDeltaModel, SQLAlchemyModel]):
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
        pks_to_delete = []
        query = self.get_delta_import_query()

        for delta_item in query.execute():
            if delta_item.action == DeltaAction.ADD:
                if not self.exists(delta_item):
                    items_to_add.append(self.create(delta_item))

            elif delta_item.action == DeltaAction.UPDATE:
                sqlalchemy_obj = self.exists(delta_item)
                if sqlalchemy_obj:
                    self.update(sqlalchemy_obj, delta_item)
                    items_to_update.append(sqlalchemy_obj)

            elif delta_item.action == DeltaAction.REMOVE:
                sqlalchemy_obj = self.exists(delta_item)
                if sqlalchemy_obj:
                    pks_to_delete.append(sqlalchemy_obj.id)

            if len(items_to_add) >= BATCH_SIZE:
                self._bulk_save(items_to_add)
                items_to_add = []
            if len(pks_to_delete) >= BATCH_SIZE:
                self._bulk_delete(pks_to_delete)
                pks_to_delete = []

        self._bulk_save(items_to_add)
        self._bulk_delete(pks_to_delete)

        if items_to_update:
            with transaction():
                logger.info(f"Successfully updated {len(items_to_update)} {class_name}")

        logger.info(f"Finished processing delta for {class_name}")

    def _bulk_save(self, items: list[SQLAlchemyModel]) -> None:
        if not items:
            return
        class_name = self.get_sqlalchemy_class().__name__
        try:
            with transaction():
                db.session.bulk_save_objects(items)
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
