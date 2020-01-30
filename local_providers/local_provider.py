import traceback
from abc import abstractmethod
from collections import Iterator
from datetime import datetime
from pprint import pprint

from validation.models import handler
from connectors.redis import send_venue_provider_data_to_redis
from connectors.thumb_storage import save_provider_thumb
from local_providers.chunk_manager import get_existing_pc_obj, save_chunks
from local_providers.providable_info import ProvidableInfo
from models import ApiErrors
from models.db import Model, db
from models.has_thumb_mixin import HasThumbMixin
from models.local_provider_event import LocalProviderEvent, LocalProviderEventType
from repository import repository
from repository.providable_queries import get_last_update_for_provider
from repository.provider_queries import get_provider_by_local_class
from utils.logger import logger
from utils.object_storage import build_thumb_path

CHUNK_MAX_SIZE = 1000


class LocalProvider(Iterator):
    def __init__(self, venue_provider=None, **options):
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
        self.providables = []

    @property
    @abstractmethod
    def can_create(self):
        pass

    def getDeactivatedObjectIds(self):
        return []

    @abstractmethod
    def fill_object_attributes(self, obj):
        pass

    def create_providable_info(self,
                               pc_object: Model,
                               id_at_providers: str,
                               date_modified_at_provider: datetime) -> ProvidableInfo:
        if '|' in id_at_providers:
            raise Exception('Invalid character in idAtProviders field')
        providable_info = ProvidableInfo()
        providable_info.type = pc_object
        providable_info.id_at_providers = id_at_providers
        providable_info.date_modified_at_provider = date_modified_at_provider
        return providable_info

    def get_object_thumb(self) -> bytes:
        return bytes()

    def get_object_thumb_index(self) -> int:
        return 0

    @property
    @abstractmethod
    def name(self):
        pass

    def _handle_thumb(self, pc_object: Model):
        new_thumb_index = self.get_object_thumb_index()
        if new_thumb_index == 0:
            return
        self.checkedThumbs += 1

        new_thumb = self.get_object_thumb()
        if not new_thumb:
            return

        _save_same_thumb_from_thumb_count_to_index(pc_object, new_thumb_index, new_thumb)
        logger.debug("Creating thumb #" + str(new_thumb_index) + " for " + str(pc_object))
        self.createdThumbs += new_thumb_index

    def _create_object(self, providable_info: ProvidableInfo) -> Model:
        pc_object = providable_info.type()
        pc_object.idAtProviders = providable_info.id_at_providers
        pc_object.lastProviderId = self.provider.id
        pc_object.dateModifiedAtLastProvider = providable_info.date_modified_at_provider

        self.fill_object_attributes(pc_object)

        errors = handler.errors(pc_object)
        if errors and len(errors.errors) > 0:
            self.log_provider_event(LocalProviderEventType.SyncError, 'ApiErrors')
            self.erroredObjects += 1
            raise errors

        self.createdObjects += 1
        return pc_object

    def _handle_update(self, pc_object, providable_info):
        self.fill_object_attributes(pc_object)

        pc_object.lastProviderId = self.provider.id
        pc_object.dateModifiedAtLastProvider = providable_info.date_modified_at_provider

        errors = handler.errors(pc_object)
        if errors and len(errors.errors) > 0:
            self.log_provider_event(LocalProviderEventType.SyncError, 'ApiErrors')
            self.erroredObjects += 1
            raise errors

        self.updatedObjects += 1

    def log_provider_event(self, event_type, event_payload=None):
        local_provider_event = LocalProviderEvent()
        local_provider_event.type = event_type
        local_provider_event.payload = str(event_payload)
        local_provider_event.provider = self.provider
        db.session.add(local_provider_event)
        db.session.commit()

    def _print_objects_summary(self):
        logger.info("  Checked " + str(self.checkedObjects) + " objects")
        logger.info("  Created " + str(self.createdObjects) + " objects")
        logger.info("  Updated " + str(self.updatedObjects) + " objects")
        logger.info("  " + str(self.erroredObjects) + " errors in creations/updates")

        logger.info("  Checked " + str(self.checkedThumbs) + " thumbs")
        logger.info("  Created " + str(self.createdThumbs) + " thumbs")
        logger.info("  Updated " + str(self.updatedThumbs) + " thumbs")
        logger.info("  " + str(self.erroredThumbs) + " errors in thumb creations/updates")

    def updateObjects(self, limit=None):
        if self.venue_provider and \
                not self.venue_provider.isActive:
            logger.info("Venue provider is inactive")
            return

        if not self.provider.isActive:
            provider_name = self.__class__.__name__
            logger.info("Provider " + provider_name + " is inactive")
            return

        self.log_provider_event(LocalProviderEventType.SyncStart)

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
                chunk_key = providable_info.id_at_providers + '|' + str(providable_info.type.__name__)
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
                    object_need_update = last_update_for_current_provider is None \
                                         or last_update_for_current_provider < providable_info.date_modified_at_provider

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
                    except Exception as e:
                        self.log_provider_event(LocalProviderEventType.SyncError, e.__class__.__name__)
                        self.erroredThumbs += 1
                        logger.info('ERROR during handle thumb: ' + e.__class__.__name__ + ' ' + str(e))
                        traceback.print_tb(e.__traceback__)
                        pprint(vars(e))
                    pc_object_has_new_thumbs = pc_object.thumbCount != initial_thumb_count
                    if pc_object_has_new_thumbs:
                        errors = handler.errors(pc_object)
                        if errors and len(errors.errors) > 0:
                            self.log_provider_event(LocalProviderEventType.SyncError, 'ApiErrors')
                            continue

                        chunk_to_update[chunk_key] = pc_object

                self.checkedObjects += 1

                if len(chunk_to_insert) + len(chunk_to_update) >= CHUNK_MAX_SIZE:
                    save_chunks(chunk_to_insert, chunk_to_update)
                    chunk_to_insert = {}
                    chunk_to_update = {}

        if len(chunk_to_insert) + len(chunk_to_update) > 0:
            save_chunks(chunk_to_insert, chunk_to_update)

        self._print_objects_summary()
        self.log_provider_event(LocalProviderEventType.SyncEnd)

        if self.venue_provider is not None:
            self.venue_provider.lastSyncDate = datetime.utcnow()
            self.venue_provider.syncWorkerId = None
            repository.save(self.venue_provider)
            send_venue_provider_data_to_redis(self.venue_provider)


def _save_same_thumb_from_thumb_count_to_index(pc_object: Model, thumb_index: int, image_as_bytes: bytes):
    thumb_counter = pc_object.thumbCount if pc_object.thumbCount else 0
    if thumb_index <= thumb_counter:
        _add_new_thumb(pc_object, thumb_index, image_as_bytes)
    else:
        while thumb_counter < thumb_index:
            _add_new_thumb(pc_object, thumb_counter, image_as_bytes)
            thumb_counter += 1


def _add_new_thumb(pc_object: Model, thumb_index: int, image_as_bytes: bytes):
    thumb_destination_storage_id = build_thumb_path(pc_object, thumb_index)
    save_provider_thumb(thumb_destination_storage_id, image_as_bytes)
    pc_object.thumbCount = pc_object.thumbCount + 1
