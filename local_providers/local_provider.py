import traceback
from abc import abstractmethod
from collections import Iterator
from datetime import datetime
from io import BytesIO
from pprint import pprint

from connectors.thumb_storage import save_thumb
from local_providers.chunk_manager import get_existing_pc_obj, save_chunks
from local_providers.providable_info import ProvidableInfo
from models import ApiErrors
from models.db import db, Model
from models.has_thumb_mixin import HasThumbMixin
from models.local_provider_event import LocalProviderEvent, LocalProviderEventType
from models.pc_object import PcObject
from repository.providable_queries import get_last_update_for_provider
from repository.provider_queries import get_provider_by_local_class
from utils.logger import logger

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

    @property
    @abstractmethod
    def help(self):
        pass

    def getDeactivatedObjectIds(self):
        return []

    @abstractmethod
    def fill_object_attributes(self, obj):
        pass

    def getObjectThumb(self, obj, index):
        return None

    def get_object_thumb_index(self) -> int:
        return None

    def get_object_thumb_date(self, obj: PcObject) -> datetime:
        return None

    def getObjectThumbDates(self, obj):
        return []

    @property
    @abstractmethod
    def identifier_description(self):
        pass

    @property
    @abstractmethod
    def identifier_regexp(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def object_type(self):
        pass

    def save_thumb_from_thumb_count_to_index(self, index: int, obj: Model, thumb: BytesIO):
        counter = obj.thumbCount
        while obj.thumbCount <= index:
            save_thumb(obj, thumb, counter, need_save=False)
            counter += 1

    def handle_thumb(self, obj):
        if not hasattr(obj, 'thumbCount'):
            return
        try:
            new_thumb_index = self.get_object_thumb_index()
            new_thumb_date = self.get_object_thumb_date(obj)
            if new_thumb_index is None \
                    or new_thumb_date is None:
                return

            self.checkedThumbs += 1
            existing_thumb_date = obj.thumb_date(new_thumb_index)
            if existing_thumb_date is None \
                    or existing_thumb_date < new_thumb_date:

                new_thumb = self.getObjectThumb(obj, new_thumb_index)
                if new_thumb is None:
                    return

                self.save_thumb_from_thumb_count_to_index(new_thumb_index, obj, new_thumb)

                if existing_thumb_date:
                    logger.info("    Updating thumb #" + str(new_thumb_index) + " for " + str(obj))
                    self.updatedThumbs += new_thumb_index + 1
                else:
                    logger.info("    Creating thumb #" + str(new_thumb_index) + " for " + str(obj))
                    self.createdThumbs += new_thumb_index + 1

        except Exception as e:
            self.log_provider_event(LocalProviderEventType.SyncError, e.__class__.__name__)
            self.erroredThumbs += 1
            logger.info('ERROR during handle thumb: '
                        + e.__class__.__name__ + ' ' + str(e))
            traceback.print_tb(e.__traceback__)
            pprint(vars(e))

    def create_object(self, providable_info: ProvidableInfo) -> Model:
        pc_object = providable_info.type()
        pc_object.idAtProviders = providable_info.id_at_providers
        pc_object.lastProviderId = self.provider.id
        pc_object.dateModifiedAtLastProvider = providable_info.date_modified_at_provider

        self.fill_object_attributes(pc_object)

        errors = pc_object.errors()
        if errors and len(errors.errors) > 0:
            self.log_provider_event(LocalProviderEventType.SyncError, 'ApiErrors')
            raise errors

        self.createdObjects += 1
        return pc_object

    def handle_update(self, pc_object, providable_info):
        self.fill_object_attributes(pc_object)
        pc_object.lastProviderId = self.provider.id
        pc_object.dateModifiedAtLastProvider = providable_info.date_modified_at_provider

        errors = pc_object.errors()
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

    def print_objects_summary(self):
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
            if limit and self.checkedObjects >= limit:
                break

            if providable_infos is None:
                self.checkedObjects += 1
                continue

            for providable_info in providable_infos:
                chunk_key = providable_info.id_at_providers + '|' + str(providable_info.type.__name__)
                pc_object = get_existing_pc_obj(providable_info, chunk_to_insert, chunk_to_update)

                if pc_object is None:
                    if not self.can_create:
                        continue

                    try:
                        pc_object = self.create_object(providable_info)
                        chunk_to_insert[chunk_key] = pc_object
                    except ApiErrors:
                        continue
                else:
                    last_update_for_current_provider = get_last_update_for_provider(self.provider.id, pc_object)
                    object_need_update = last_update_for_current_provider is None \
                                         or last_update_for_current_provider < providable_info.date_modified_at_provider

                    if object_need_update:
                        try:
                            self.handle_update(pc_object, providable_info)
                            if chunk_key in chunk_to_insert:
                                chunk_to_insert[chunk_key] = pc_object
                            else:
                                chunk_to_update[chunk_key] = pc_object
                        except ApiErrors:
                            continue

                if isinstance(pc_object, HasThumbMixin):
                    initial_thumb_count = pc_object.thumbCount
                    self.handle_thumb(pc_object)

                    if pc_object.thumbCount != initial_thumb_count:
                        errors = pc_object.errors()
                        if errors and len(errors.errors) > 0:
                            self.log_provider_event(LocalProviderEventType.SyncError, 'ApiErrors')
                            continue

                        chunk_to_update[chunk_key] = pc_object

                if len(chunk_to_insert) + len(chunk_to_update) >= CHUNK_MAX_SIZE:
                    save_chunks(chunk_to_insert, chunk_to_update, providable_info)
                    chunk_to_insert = {}
                    chunk_to_update = {}

                self.checkedObjects += 1

        if len(chunk_to_insert) + len(chunk_to_update) > 0:
            save_chunks(chunk_to_insert, chunk_to_update, providable_info)

        self.print_objects_summary()
        self.log_provider_event(LocalProviderEventType.SyncEnd)

        if self.venue_provider is not None:
            self.venue_provider.lastSyncDate = datetime.utcnow()
            PcObject.save(self.venue_provider)
