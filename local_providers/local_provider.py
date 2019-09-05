import traceback
from abc import abstractmethod
from collections import Iterator
from datetime import datetime
from pprint import pprint

from postgresql_audit.flask import versioning_manager
from sqlalchemy import text

from local_providers.providable_info import ProvidableInfo
from local_providers.utils.retreive_provider_object import get_existing_pc_obj, get_last_modification_date_for_provider
from local_providers.utils.save_provider_objects import save_chunks, save_thumb_from_thumb_count_to_index
from models.db import db
from models.has_thumb_mixin import HasThumbMixin
from models.local_provider_event import LocalProviderEvent, LocalProviderEventType
from models.pc_object import PcObject
from repository.provider_queries import get_provider_by_local_class
from utils.date import read_json_date
from utils.human_ids import humanize
from utils.inflect_engine import inflect_engine
from utils.logger import logger

CHUNK_MAX_SIZE = 1000


class LocalProvider(Iterator):
    def __init__(self, venue_provider=None, **options):
        self.venueProvider = venue_provider
        self.updatedObjects = 0
        self.createdObjects = 0
        self.checkedObjects = 0
        self.erroredObjects = 0
        self.createdThumbs = 0
        self.updatedThumbs = 0
        self.checkedThumbs = 0
        self.erroredThumbs = 0
        self.dbObject = get_provider_by_local_class(self.__class__.__name__)
        self.providables = []

    @property
    @abstractmethod
    def canCreate(self):
        pass

    @property
    @abstractmethod
    def help(self):
        pass

    def getDeactivatedObjectIds(self):
        return []

    def updateObject(self, obj):
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
    def identifierDescription(self):
        pass

    @property
    @abstractmethod
    def identifierRegexp(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def objectType(self):
        pass

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

                save_thumb_from_thumb_count_to_index(new_thumb_index, obj, new_thumb)

                if existing_thumb_date:
                    logger.info("    Updating thumb #" + str(new_thumb_index) + " for " + str(obj))
                    self.updatedThumbs += new_thumb_index + 1
                else:
                    logger.info("    Creating thumb #" + str(new_thumb_index) + " for " + str(obj))
                    self.createdThumbs += new_thumb_index + 1

        except Exception as e:
            self.logEvent(LocalProviderEventType.SyncError, e.__class__.__name__)
            self.erroredThumbs += 1
            logger.info('ERROR during handle thumb: '
                        + e.__class__.__name__ + ' ' + str(e))
            traceback.print_tb(e.__traceback__)
            pprint(vars(e))

    def create_object(self, providable_info):
        logger.debug('  Creating ' + providable_info.type.__name__
                     + '# ' + providable_info.idAtProviders)
        obj = providable_info.type()
        obj.idAtProviders = providable_info.idAtProviders
        self.createdObjects += 1
        return obj

    def handle_update(self, obj, providable_info, is_new_obj):
        if not is_new_obj:
            logger.debug('  Updating ' + providable_info.type.__name__
                         + '# ' + providable_info.idAtProviders)
            self.updatedObjects += 1
        try:
            self.updateObject(obj)
            obj.lastProviderId = self.dbObject.id
            obj.dateModifiedAtLastProvider = providable_info.dateModifiedAtProvider
        except Exception as e:
            logger.info('ERROR during updateObject: '
                        + e.__class__.__name__ + ' ' + str(e))
            self.logEvent(LocalProviderEventType.SyncError, e.__class__.__name__)
            self.erroredObjects += 1
            traceback.print_tb(e.__traceback__)
            pprint(vars(e))

    def logEvent(self, event_type, event_payload=None):
        local_provider_event = LocalProviderEvent()
        local_provider_event.type = event_type
        local_provider_event.payload = str(event_payload)
        local_provider_event.provider = self.dbObject
        db.session.add(local_provider_event)
        db.session.commit()

    def updateObjects(self, limit=None):
        """Update venue's objects with this provider."""
        if self.venueProvider is not None:
            if not self.venueProvider.isActive:
                logger.info("VenueProvider is not active. Stopping")
                return
            db.session.add(self.venueProvider)  # FIXME: we should not need this
        provider_name = self.__class__.__name__

        if not self.dbObject.isActive:
            logger.info("Provider " + provider_name + " is inactive")
            return

        logger.debug("Updating "
                     + inflect_engine.plural(self.objectType.__name__)
                     + " from provider " + self.name)
        self.logEvent(LocalProviderEventType.SyncStart)

        if self.venueProvider is not None:
            logger.debug(" for venue " + self.venueProvider.venue.name
                         + " (#" + str(self.venueProvider.venueId) + " / "
                         + humanize(self.venueProvider.venueId) + ") "
                         + " venueIdAtOfferProvider="
                         + self.venueProvider.venueIdAtOfferProvider)
        else:
            logger.info("venueProvider not found")

        chunk_to_insert = {}
        chunk_to_update = {}

        try:
            for providable_infos in self:
                self.providables = []

                if isinstance(providable_infos, ProvidableInfo) \
                        or providable_infos is None:
                    providable_infos = [providable_infos]

                for providable_info in providable_infos:
                    if providable_info is not None:
                        chunk_key = providable_info.idAtProviders + '|' + str(providable_info.type.__name__)

                        pc_obj = get_existing_pc_obj(providable_info, chunk_to_insert, chunk_to_update)

                        date_modified_at_provider = None
                        is_new_obj = False

                        if pc_obj is None:
                            is_new_obj = True
                            if providable_info.dateModifiedAtProvider is None \
                                    or not self.canCreate:
                                logger.debug('  Not creating or updating ' + providable_info.type.__name__ +
                                             '# ' + providable_info.idAtProviders)
                                continue
                            pc_obj = self.create_object(providable_info)
                        else:
                            date_modified_at_provider = get_last_modification_date_for_provider(self.dbObject.id,
                                                                                                pc_obj)

                        self.providables.append(pc_obj)

                        object_need_update = date_modified_at_provider is None \
                                             or date_modified_at_provider < providable_info.dateModifiedAtProvider

                        if providable_info.dateModifiedAtProvider is not None \
                                and object_need_update:
                            self.handle_update(pc_obj, providable_info, is_new_obj)

                            errors = pc_obj.errors()
                            if errors and len(errors.errors) > 0:
                                self.logEvent(LocalProviderEventType.SyncError, 'ApiErrors')
                                continue

                            if is_new_obj:
                                chunk_to_insert[chunk_key] = pc_obj
                            else:
                                if chunk_key in chunk_to_insert:
                                    chunk_to_insert[chunk_key] = pc_obj
                                else:
                                    chunk_to_update[chunk_key] = pc_obj

                        else:
                            logger.debug('  Not creating or updating '
                                         + providable_info.type.__name__
                                         + '# ' + providable_info.idAtProviders)

                        if pc_obj is not None:
                            if isinstance(pc_obj, HasThumbMixin):
                                initial_thumb_count = pc_obj.thumbCount
                                self.handle_thumb(pc_obj)

                                if pc_obj.thumbCount != initial_thumb_count:
                                    errors = pc_obj.errors()
                                    if errors and len(errors.errors) > 0:
                                        self.logEvent(LocalProviderEventType.SyncError, 'ApiErrors')
                                        continue

                                    chunk_to_update[chunk_key] = pc_obj

                        if len(chunk_to_insert) + len(chunk_to_update) >= CHUNK_MAX_SIZE:
                            save_chunks(chunk_to_insert, chunk_to_update, providable_info)

                            chunk_to_insert = {}
                            chunk_to_update = {}

                    self.checkedObjects += 1

                if limit is not None and \
                        self.checkedObjects >= limit:
                    break
        except Exception as e:
            if len(chunk_to_insert) + len(chunk_to_update) > 0:
                save_chunks(chunk_to_insert, chunk_to_update, providable_info)
            raise e

        if len(chunk_to_insert) + len(chunk_to_update) > 0:
            save_chunks(chunk_to_insert, chunk_to_update, providable_info)

        logger.info("  Checked " + str(self.checkedObjects) + " objects")
        logger.info("  Created " + str(self.createdObjects) + " objects")
        logger.info("  Updated " + str(self.updatedObjects) + " objects")
        logger.info("  " + str(self.erroredObjects) + " errors in creations/updates")

        logger.info("  Checked " + str(self.checkedThumbs) + " thumbs")
        logger.info("  Created " + str(self.createdThumbs) + " thumbs")
        logger.info("  Updated " + str(self.updatedThumbs) + " thumbs")
        logger.info("  " + str(self.erroredThumbs) + " errors in thumb creations/updates")

        self.logEvent(LocalProviderEventType.SyncEnd)
        if self.venueProvider is not None:
            self.venueProvider.lastSyncDate = datetime.utcnow()
            PcObject.save(self.venueProvider)
