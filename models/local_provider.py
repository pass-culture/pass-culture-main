""" local provider """
import sys
import traceback
from abc import abstractmethod
from collections import Iterator
from datetime import datetime
from pprint import pprint
from sqlalchemy import text
from postgresql_audit.flask import versioning_manager

from models.db import db
from models.event import Event
from models.local_provider_event import LocalProviderEvent, LocalProviderEventType
from models.pc_object import PcObject
from models.provider import Provider
from models.thing import Thing
from utils.date import read_json_date
from utils.human_ids import humanize
from utils.inflect_engine import inflect_engine


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
        self.dbObject = Provider.getByClassName(self.__class__.__name__)

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
        latest_activity = Activity.query.filter(sql)\
                                        .order_by(db.desc(Activity.id))\
                                        .limit(1)\
                                        .one_or_none()
        if latest_activity is None:
            return None
        else:
            return read_json_date(latest_activity.changed_data['dateModifiedAtLastProvider'])


    def handleThumb(self, obj):
        if not hasattr(obj, 'thumbCount'):
            return
        try:
            thumb_dates = self.getObjectThumbDates(obj)
            need_save = False
            for index, thumb_date in enumerate(thumb_dates):
                self.checkedThumbs += 1
                if thumb_date is None:
                    continue
                existing_date = obj.thumb_date(index)
                if existing_date is None\
                   or existing_date < thumb_date:
                    thumb = self.getObjectThumb(obj, index)
                    if thumb is None:
                        continue
                    need_save = True
                    if existing_date is not None:
                        obj.delete_thumb(index)
                        print("    Updating thumb #"+str(index)+" for "+str(obj))
                    else:
                        print("    Creating thumb #"+str(index)+" for "+str(obj))
                    obj.save_thumb(thumb, index)
                    if existing_date is not None:
                        self.updatedThumbs += 1
                    else:
                        self.createdThumbs += 1
            if need_save:
                PcObject.check_and_save(obj)
        except Exception as e:
            self.logEvent(LocalProviderEventType.SyncError, e.__class__.__name__)
            self.erroredThumbs += 1
            print('ERROR during handleThumb: '
                  + e.__class__.__name__ + ' ' + str(e))
            traceback.print_tb(e.__traceback__)
            pprint(vars(e))

    def existingObjectOrNone(self, providable_info):
        with db.session.no_autoflush:
            query = providable_info.type.query.filter_by(
                idAtProviders=providable_info.idAtProviders
            )
            return query.one_or_none()

    def createObject(self, providable_info):
        print('  Creating ' + providable_info.type.__name__
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
            print('  Updating ' + providable_info.type.__name__
                  + '# ' + providable_info.idAtProviders)
            self.updatedObjects += 1
        try:
            self.updateObject(obj)
            # FIXME: keep this until we make type an ENUM again
            if isinstance(obj, Thing)\
               or isinstance(obj, Event):
                type_elems = str(obj.type).split('.')
                if len(type_elems) == 2:
                    obj.type = type_elems[1]
                else:
                    obj.type = type_elems[0]
            obj.dateModifiedAtLastProvider = providable_info.dateModifiedAtProvider
            obj.lastProvider = self.dbObject
            if self.venueProvider is not None:
                obj.venue = self.venueProvider.venue
            PcObject.check_and_save(obj)
        except Exception as e:
            print('ERROR during updateObject: '
                  + e.__class__.__name__+' '+str(e))
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
                print("VenueProvider is not active. Stopping")
                return
            db.session.add(self.venueProvider)  # FIXME: we should not need this
        providerName = self.__class__.__name__
        if not self.dbObject.isActive:
            print("Provider "+providerName+" is inactive")
            return
        sys.stdout.write("Updating "
                         + inflect_engine.plural(self.objectType.__name__)
                         + " from provider " + self.name)
        self.logEvent(LocalProviderEventType.SyncStart)
        if self.venueProvider is not None:
            print(" for venue " + self.venueProvider.venue.name
                  + " (#" + str(self.venueProvider.venueId) + " / "
                  + humanize(self.venueProvider.venueId) + ") "
                  + " venueIdAtOfferProvider="
                  + self.venueProvider.venueIdAtOfferProvider)
        else:
            print("venueProvider not found")
        for providable_infos in self:
            if isinstance(providable_infos, ProvidableInfo)\
               or providable_infos is None:
                providable_infos = [providable_infos]
            self.providables = []
            for providable_info in providable_infos:
                if providable_info is not None:
                    pc_obj = self.existingObjectOrNone(providable_info)
                    dateModifiedAtProvider = None
                    is_new_obj = pc_obj is None
                    if is_new_obj:
                        if providable_info.dateModifiedAtProvider is None\
                           or not self.canCreate:
                            print('  Not creating or updating '
                                  + providable_info.type.__name__
                                  + '# ' + providable_info.idAtProviders)
                            continue
                        pc_obj = self.createObject(providable_info)
                    elif pc_obj is not None:
                        dateModifiedAtProvider = self.dateModifiedAtProvider(pc_obj)

                    self.providables.append(pc_obj)

                    if providable_info.dateModifiedAtProvider is not None\
                       and (dateModifiedAtProvider is None
                            or dateModifiedAtProvider < providable_info.dateModifiedAtProvider):
                        self.handleUpdate(pc_obj, providable_info, is_new_obj)
                    else:
                        print('  Not creating or updating '
                              + providable_info.type.__name__
                              + '# ' + providable_info.idAtProviders)
                    if pc_obj is not None:
                        self.handleThumb(pc_obj)
                self.checkedObjects += 1

            db.session.close()
            if self.venueProvider is not None:
                db.session.add(self.venueProvider)
            db.session.add(self.dbObject)

            if limit is not None and\
               self.checkedObjects >= limit:
                break

        #with db.session.no_autoflush:
        #    update = sa.update(self.objectType)\
        #               .where((self.objectType.provider == self.offerer.provider) &\
        #                      ~self.objectType.idAtProviders.in_(self.getDeactivatedObjectIds()))\
        #               .values({'deactivated': True})
        #    db.session.execute(update)
        #db.session.commit()

        print("  Checked " + str(self.checkedObjects) + " objects")
        print("  Created " + str(self.createdObjects) + " objects")
        print("  Updated " + str(self.updatedObjects) + " objects")
        print("  " + str(self.erroredObjects) + " errors in creations/updates")

        print("  Checked " + str(self.checkedThumbs) + " thumbs")
        print("  Created " + str(self.createdThumbs) + " thumbs")
        print("  Updated " + str(self.updatedThumbs) + " thumbs")
        print("  " + str(self.erroredThumbs) + " errors in thumb creations/updates")
        self.logEvent(LocalProviderEventType.SyncEnd)
        if self.venueProvider is not None:
            self.venueProvider.lastSyncDate = datetime.utcnow()
            PcObject.check_and_save(self.venueProvider)
