""" local provider """
import traceback
from abc import abstractmethod
from collections import Iterator
from datetime import datetime
from io import BytesIO
from pprint import pprint
from typing import Dict, Optional

from postgresql_audit.flask import versioning_manager
from sqlalchemy import text
from sqlalchemy.sql import select

import models
from connectors.thumb import save_thumb
from models.db import db
from models.has_thumb_mixin import HasThumbMixin
from models.local_provider_event import LocalProviderEvent, LocalProviderEventType
from models.pc_object import PcObject
from models.product import Product
from models.providable_mixin import ProvidableMixin
from repository.provider_queries import get_provider_by_local_class
from utils.date import read_json_date
from utils.human_ids import humanize
from utils.inflect_engine import inflect_engine
from utils.logger import logger

CHUNK_MAX_SIZE = 1000


class ProvidableInfo(object):
    def type(self):
        pass

    def idAtProviders(self):
        pass

    def dateModifiedAtProvider(self):
        pass


class LocalProvider(Iterator):
    def __init__(self, venueProvider=None, **options):
        self.venueProvider = venueProvider
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

    def latestActivityDate(self):
        Activity = versioning_manager.activity_cls
        sql = text("table_name='" + self.objectType.__tablename__ + "'"
                   + " AND cast(changed_data->>'lastProviderId' AS int)"
                   + " = " + str(self.dbObject.id)
                   + " AND (NOT old_data ? 'dateModifiedAtLastProvider'"
                   + " OR NOT changed_data->>'dateModifiedAtLastProvider'"
                   + " = old_data->>'dateModifiedAtLastProvider')")
        latest_activity = Activity.query.filter(sql) \
            .order_by(db.desc(Activity.id)) \
            .limit(1) \
            .one_or_none()
        if latest_activity is None:
            return None
        else:
            return read_json_date(latest_activity.changed_data['dateModifiedAtLastProvider'])

    def handleThumb(self, obj):
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
            self.logEvent(LocalProviderEventType.SyncError, e.__class__.__name__)
            self.erroredThumbs += 1
            logger.info('ERROR during handleThumb: '
                        + e.__class__.__name__ + ' ' + str(e))
            traceback.print_tb(e.__traceback__)
            pprint(vars(e))

    def save_thumb_from_thumb_count_to_index(self, index: int, obj: PcObject, thumb: BytesIO):
        counter = obj.thumbCount
        while obj.thumbCount <= index:
            save_thumb(obj, thumb, counter, need_save=False)
            counter += 1

    def existingObjectOrNone(self, providable_info):
        conn = db.engine.connect()
        model_to_query = providable_info.type
        query = select([model_to_query]). \
            where(model_to_query.idAtProviders == providable_info.idAtProviders)
        db_object_dict = conn.execute(query).fetchone()

        if db_object_dict is not None:
            return dict_to_object(db_object_dict, model_to_query)
        return None

    def createObject(self, providable_info):
        logger.debug('  Creating ' + providable_info.type.__name__
                     + '# ' + providable_info.idAtProviders)
        obj = providable_info.type()
        obj.idAtProviders = providable_info.idAtProviders
        self.createdObjects += 1
        return obj

    def dateModifiedAtProvider(self, obj):
        if obj.lastProviderId == self.dbObject.id:
            return obj.dateModifiedAtLastProvider
        for change in obj.activity():
            if change.changed_data['lastProviderId'] == self.dbObject.id:
                return read_json_date(change.changed_data['dateModifiedAtLastProvider'])

    def handleUpdate(self, obj, providable_info, is_new_obj):
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
        providerName = self.__class__.__name__

        if not self.dbObject.isActive:
            logger.info("Provider " + providerName + " is inactive")
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

                        pc_obj = self.get_existing_pc_obj(providable_info, chunk_to_insert, chunk_to_update)

                        date_modified_at_provider = None
                        is_new_obj = False

                        if pc_obj is None:
                            is_new_obj = True
                            if providable_info.dateModifiedAtProvider is None \
                                    or not self.canCreate:
                                logger.debug('  Not creating or updating ' + providable_info.type.__name__ +
                                             '# ' + providable_info.idAtProviders)
                                continue
                            pc_obj = self.createObject(providable_info)
                        else:
                            date_modified_at_provider = self.dateModifiedAtProvider(pc_obj)

                        self.providables.append(pc_obj)

                        object_need_update = date_modified_at_provider is None \
                                             or date_modified_at_provider < providable_info.dateModifiedAtProvider

                        if providable_info.dateModifiedAtProvider is not None \
                                and object_need_update:
                            self.handleUpdate(pc_obj, providable_info, is_new_obj)

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
                                self.handleThumb(pc_obj)

                                if pc_obj.thumbCount != initial_thumb_count:
                                    errors = pc_obj.errors()
                                    if errors and len(errors.errors) > 0:
                                        self.logEvent(LocalProviderEventType.SyncError, 'ApiErrors')
                                        continue

                                    chunk_to_update[chunk_key] = pc_obj

                        if len(chunk_to_insert) + len(chunk_to_update) >= CHUNK_MAX_SIZE:
                            self.save_chunks(chunk_to_insert, chunk_to_update, providable_info)

                            chunk_to_insert = {}
                            chunk_to_update = {}

                    self.checkedObjects += 1

                if limit is not None and \
                        self.checkedObjects >= limit:
                    break
        except Exception as e:
            if len(chunk_to_insert) + len(chunk_to_update) > 0:
                self.save_chunks(chunk_to_insert, chunk_to_update, providable_info)
            raise e

        if len(chunk_to_insert) + len(chunk_to_update) > 0:
            self.save_chunks(chunk_to_insert, chunk_to_update, providable_info)

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

    def get_existing_pc_obj(self, providable_info, chunk_to_insert, chunk_to_update):
        object_in_current_chunk = self.get_object_from_current_chunks(providable_info,
                                                                      chunk_to_insert,
                                                                      chunk_to_update)
        if object_in_current_chunk is None:
            return self.existingObjectOrNone(providable_info)
        else:
            return object_in_current_chunk

    def save_chunks(self, chunk_to_insert: Dict[str, ProvidableMixin], chunk_to_update: Dict[str, ProvidableMixin],
                    providable_info: ProvidableInfo):
        if len(chunk_to_insert) > 0:
            db.session.bulk_save_objects(chunk_to_insert.values())
            db.session.commit()
        if len(chunk_to_update) > 0:
            self.save_chunk_to_update(chunk_to_update, providable_info)

    def save_chunk_to_update(self, chunk_to_update: dict, providable_info: ProvidableInfo):
        conn = db.engine.connect()

        for chunk_key, chunk_object in chunk_to_update.items():
            try:
                model_name = chunk_key.split('|')[1]
                model_object = getattr(models, model_name)
            except AttributeError:
                model_object = providable_info.type

            dict_to_update = build_dict_to_update(chunk_object)

            statement = model_object.__table__.update(). \
                where(model_object.id == dict_to_update['id']). \
                values(dict_to_update)
            try:
                conn.execute(statement)
            except ValueError as e:
                logger.error('ERROR during object update: '
                             + e.__class__.__name__ + ' ' + str(e))

    def get_object_from_current_chunks(self, providable_info: ProvidableInfo,
                                       chunk_to_insert: dict,
                                       chunk_to_update: dict) -> Optional[PcObject]:
        chunk_key = providable_info.idAtProviders + '|' + str(providable_info.type.__name__)
        if chunk_key in chunk_to_insert:
            pc_object = chunk_to_insert[chunk_key]
            if type(pc_object) == providable_info.type:
                return pc_object
        if chunk_key in chunk_to_update:
            pc_object = chunk_to_update[chunk_key]
            if type(pc_object) == providable_info.type:
                return pc_object
        return None


def dict_to_object(object_dict: dict, model_object: PcObject) -> PcObject:
    pc_object = {}
    for key, value in object_dict.items():
        if key.endswith('Id'):
            pc_object[key] = humanize(value)
        else:
            pc_object[key] = value
    pc_obj = model_object(from_dict=pc_object)
    pc_obj.id = pc_object['id']
    return pc_obj


def build_dict_to_update(object_to_update: PcObject) -> dict:
    dict_to_update = object_to_update.__dict__
    if '_sa_instance_state' in dict_to_update:
        del dict_to_update['_sa_instance_state']
    if 'datePublished' in dict_to_update:
        del dict_to_update['datePublished']
    if 'venue' in dict_to_update:
        del dict_to_update['venue']
    if 'offer' in dict_to_update:
        del dict_to_update['offer']
    if 'stocks' in dict_to_update:
        del dict_to_update['stocks']
    return dict_to_update
