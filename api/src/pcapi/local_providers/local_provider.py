from abc import abstractmethod
from collections.abc import Iterator
from datetime import datetime
import logging

from pcapi.connectors.thumb_storage import create_thumb
from pcapi.core import search
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
import pcapi.core.providers.models as providers_models
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.local_providers.chunk_manager import get_existing_pc_obj
from pcapi.local_providers.chunk_manager import save_chunks
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.has_thumb_mixin import HasThumbMixin
from pcapi.repository import repository
from pcapi.repository.providable_queries import get_last_update_for_provider
from pcapi.validation.models import entity_validator


logger = logging.getLogger(__name__)


CHUNK_MAX_SIZE = 1000


class LocalProvider(Iterator):
    def __init__(self, venue_provider=None, **options):  # type: ignore [no-untyped-def]
        self.venue_provider = venue_provider
        self.updatedObjects = 0
        self.createdObjects = 0
        self.checkedObjects = 0
        self.erroredObjects = 0
        self.createdThumbs = 0
        self.updatedThumbs = 0
        self.checkedThumbs = 0
        self.erroredThumbs = 0
        self.provider = get_provider_by_local_class(self.__class__.__name__)

    @property
    @abstractmethod
    def can_create(self):  # type: ignore [no-untyped-def]
        pass

    @abstractmethod
    def fill_object_attributes(self, obj):  # type: ignore [no-untyped-def]
        pass

    def create_providable_info(
        self, pc_object: Model, id_at_providers: str, date_modified_at_provider: datetime, new_id_at_provider: str  # type: ignore [valid-type]
    ) -> ProvidableInfo:
        if "|" in id_at_providers:
            raise Exception("Invalid character in idAtProviders field")
        return ProvidableInfo(
            type=pc_object,
            id_at_providers=id_at_providers,
            new_id_at_provider=new_id_at_provider,
            date_modified_at_provider=date_modified_at_provider,
        )

    def get_object_thumb(self) -> bytes:
        return bytes()

    def get_object_thumb_index(self) -> int:
        return 0

    def get_keep_poster_ratio(self) -> bool:
        return True

    @property
    @abstractmethod
    def name(self):  # type: ignore [no-untyped-def]
        pass

    def _handle_thumb(self, pc_object: Model):  # type: ignore [no-untyped-def, valid-type]
        new_thumb_index = self.get_object_thumb_index()
        if new_thumb_index == 0:
            return
        self.checkedThumbs += 1

        new_thumb = self.get_object_thumb()
        if not new_thumb:
            return

        _save_same_thumb_from_thumb_count_to_index(pc_object, new_thumb_index, new_thumb, self.get_keep_poster_ratio())
        self.createdThumbs += new_thumb_index

    def _create_object(self, providable_info: ProvidableInfo) -> Model:  # type: ignore [valid-type]
        pc_object = providable_info.type()  # type: ignore [misc]
        pc_object.idAtProviders = providable_info.id_at_providers
        pc_object.idAtProvider = providable_info.new_id_at_provider
        pc_object.lastProviderId = self.provider.id
        pc_object.dateModifiedAtLastProvider = providable_info.date_modified_at_provider

        self.fill_object_attributes(pc_object)

        errors = entity_validator.validate(pc_object)
        if errors and len(errors.errors) > 0:
            self.log_provider_event(providers_models.LocalProviderEventType.SyncError, "ApiErrors")
            self.erroredObjects += 1
            raise errors

        self.createdObjects += 1
        return pc_object

    def _handle_update(self, pc_object, providable_info):  # type: ignore [no-untyped-def]
        self.fill_object_attributes(pc_object)

        pc_object.lastProviderId = self.provider.id
        pc_object.dateModifiedAtLastProvider = providable_info.date_modified_at_provider

        errors = entity_validator.validate(pc_object)
        if errors and len(errors.errors) > 0:
            # expire pc_object because we may have modified it during fill_object_attributes
            # and we don't want it to be pushed to the DB if there is any error
            db.session.expire(pc_object)
            self.log_provider_event(providers_models.LocalProviderEventType.SyncError, "ApiErrors")
            self.erroredObjects += 1
            raise errors

        self.updatedObjects += 1

    def log_provider_event(self, event_type, event_payload=None):  # type: ignore [no-untyped-def]
        local_provider_event = providers_models.LocalProviderEvent()
        local_provider_event.type = event_type
        local_provider_event.payload = str(event_payload)
        local_provider_event.provider = self.provider
        db.session.add(local_provider_event)
        db.session.commit()

    def _print_objects_summary(self):  # type: ignore [no-untyped-def]
        # FIXME (dbaty, 2020-02-05): I don't know how we could end up
        # here with no venue_provider, but there are checks elsewhere
        # so I do the same here.
        venue_id = self.venue_provider.venueId if self.venue_provider else "none"
        logger.info(
            "Synchronization of objects of venue=%s, checked=%d, created=%d, updated=%d, errors=%s",
            venue_id,
            self.checkedObjects,
            self.createdObjects,
            self.updatedObjects,
            self.erroredObjects,
        )
        logger.info(
            "Synchronization of thumbs of venue=%s, checked=%d, created=%d, updated=%d, errors=%s",
            venue_id,
            self.checkedThumbs,
            self.createdThumbs,
            self.updatedThumbs,
            self.erroredThumbs,
        )

    def updateObjects(self, limit=None):  # type: ignore [no-untyped-def]
        # pylint: disable=too-many-nested-blocks
        if self.venue_provider and not self.venue_provider.isActive:
            logger.info("Venue provider %s is inactive", self.venue_provider)
            return

        if not self.provider.isActive:
            provider_name = self.__class__.__name__
            logger.info("Provider %s is inactive", provider_name)
            return

        # TODO (asaunier,2021-03-18): We may replace this log in BDD with logs in the monitoring system
        self.log_provider_event(providers_models.LocalProviderEventType.SyncStart)

        chunk_to_insert = {}
        chunk_to_update = {}

        for providable_infos in self:
            objects_limit_reached = limit and self.checkedObjects >= limit
            if objects_limit_reached:
                break

            has_no_providables_info = len(providable_infos) == 0
            if has_no_providables_info:
                self.checkedObjects += 1
                continue

            for providable_info in providable_infos:
                chunk_key = providable_info.id_at_providers + "|" + str(providable_info.type.__name__)
                pc_object = get_existing_pc_obj(providable_info, chunk_to_insert, chunk_to_update)

                if pc_object is None:
                    if not self.can_create:
                        continue

                    try:
                        pc_object = self._create_object(providable_info)
                        chunk_to_insert[chunk_key] = pc_object
                    except ApiErrors:
                        continue
                else:
                    last_update_for_current_provider = get_last_update_for_provider(self.provider.id, pc_object)
                    object_need_update = (
                        last_update_for_current_provider is None
                        or last_update_for_current_provider < providable_info.date_modified_at_provider
                    )

                    if object_need_update:
                        try:
                            self._handle_update(pc_object, providable_info)
                            if chunk_key in chunk_to_insert:
                                chunk_to_insert[chunk_key] = pc_object
                            else:
                                chunk_to_update[chunk_key] = pc_object
                        except ApiErrors:
                            continue

                if isinstance(pc_object, HasThumbMixin):
                    initial_thumb_count = pc_object.thumbCount
                    try:
                        self._handle_thumb(pc_object)
                    except Exception as e:  # pylint: disable=broad-except
                        self.log_provider_event(providers_models.LocalProviderEventType.SyncError, e.__class__.__name__)
                        self.erroredThumbs += 1
                        logger.info("ERROR during handle thumb: %s", e, exc_info=True)
                    pc_object_has_new_thumbs = pc_object.thumbCount != initial_thumb_count
                    if pc_object_has_new_thumbs:
                        errors = entity_validator.validate(pc_object)
                        if errors and len(errors.errors) > 0:
                            self.log_provider_event(providers_models.LocalProviderEventType.SyncError, "ApiErrors")
                            continue

                        chunk_to_update[chunk_key] = pc_object

                self.checkedObjects += 1

                if len(chunk_to_insert) + len(chunk_to_update) >= CHUNK_MAX_SIZE:
                    save_chunks(chunk_to_insert, chunk_to_update)
                    _reindex_offers(list(chunk_to_insert.values()) + list(chunk_to_update.values()))
                    chunk_to_insert = {}
                    chunk_to_update = {}

        if len(chunk_to_insert) + len(chunk_to_update) > 0:
            save_chunks(chunk_to_insert, chunk_to_update)
            _reindex_offers(list(chunk_to_insert.values()) + list(chunk_to_update.values()))

        self._print_objects_summary()
        self.log_provider_event(providers_models.LocalProviderEventType.SyncEnd)

        if self.venue_provider is not None:
            self.venue_provider.lastSyncDate = datetime.utcnow()
            repository.save(self.venue_provider)


def _save_same_thumb_from_thumb_count_to_index(pc_object: Model, thumb_index: int, image_as_bytes: bytes, keep_poster_ratio: bool = False):  # type: ignore [no-untyped-def, valid-type]
    if pc_object.thumbCount is None:  # type: ignore [attr-defined]
        pc_object.thumbCount = 0  # type: ignore [attr-defined]
    if thumb_index <= pc_object.thumbCount:  # type: ignore [attr-defined]
        # replace existing thumb
        create_thumb(pc_object, image_as_bytes, thumb_index, keep_ratio=keep_poster_ratio)
    else:
        # add new thumb
        for index in range(pc_object.thumbCount, thumb_index):  # type: ignore [attr-defined]
            create_thumb(pc_object, image_as_bytes, index, keep_ratio=keep_poster_ratio)
            pc_object.thumbCount += 1  # type: ignore [attr-defined]


def _reindex_offers(created_or_updated_objects):  # type: ignore [no-untyped-def]
    offer_ids = set()
    for obj in created_or_updated_objects:
        if isinstance(obj, Stock):
            offer_ids.add(obj.offerId)
        elif isinstance(obj, Offer):
            offer_ids.add(obj.id)
    search.async_index_offer_ids(offer_ids)
