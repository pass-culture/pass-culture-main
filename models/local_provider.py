from abc import abstractproperty
from collections import Iterator
from datetime import datetime, timedelta
from postgresql_audit.flask import versioning_manager
from pprint import pprint
from flask import current_app as app
from sqlalchemy import text
import sys
import traceback

from utils.human_ids import humanize
from utils.object_storage import delete_public_object,\
                                 get_public_object_date,\
                                 store_public_object
from utils.string_processing import inflect_engine


def read_json_date(date):
    if '.' not in date:
        date = date + '.0'
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")


class ProvidableInfo(object):
    def type():
        pass

    def idAtProviders():
        pass

    def dateModifiedAtProvider():
        pass


app.model.ProvidableInfo = ProvidableInfo


LocalProviderEvent = app.model.LocalProviderEvent
LocalProviderEventType = app.model.LocalProviderEventType


class LocalProvider(Iterator):
    def __init__(self, offererProvider=None, **options):
        self.offererProvider = offererProvider
        self.updatedObjects = 0
        self.createdObjects = 0
        self.checkedObjects = 0
        self.erroredObjects = 0
        self.createdThumbs = 0
        self.updatedThumbs = 0
        self.checkedThumbs = 0
        self.erroredThumbs = 0
        self.dbObject = app.model.Provider.getByClassName(self.__class__.__name__)

    @abstractproperty
    def canCreate():
        pass

    @abstractproperty
    def help():
        pass

    def getDeactivatedObjectIds(self):
        return []

    def updateObject(self, obj):
        pass

    def getObjectThumb(self, obj, index):
        return None

    def getObjectThumbDates(self, obj):
        return []

    @abstractproperty
    def identifierDescription():
        pass

    @abstractproperty
    def identifierRegexp():
        pass

    @abstractproperty
    def name():
        pass

    @abstractproperty
    def objectType():
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
                                        .order_by(app.db.desc(Activity.id))\
                                        .limit(1)\
                                        .one_or_none()
        if latest_activity is None:
            return None
        else:
            return read_json_date(latest_activity.changed_data['dateModifiedAtLastProvider'])

    def latestSyncPartEndEvent(self):
        return LocalProviderEvent\
                  .query\
                  .filter((LocalProviderEvent.provider == self.dbObject) &
                          (LocalProviderEvent.type == LocalProviderEventType.SyncPartEnd) &
                          (LocalProviderEvent.date > datetime.now() - timedelta(days=25)))\
                  .order_by(LocalProviderEvent.date.desc())\
                  .first()

    def handleThumb(self, obj):
        if not hasattr(obj, 'thumbCount'):
            return
        try:
            thumb_dates = self.getObjectThumbDates(obj)
            for index, thumb_date in enumerate(thumb_dates):
                self.checkedThumbs += 1
                thumb_storage_id = inflect_engine.plural(obj.__class__.__name__.lower()) + "/"\
                                   + humanize(obj.id)\
                                   + (('_' + str(index)) if index > 0 else '')
                if thumb_date is None:
                    continue
                existing_date = get_public_object_date("thumbs", thumb_storage_id)
                if existing_date is None\
                   or existing_date < thumb_date:
                    thumb = self.getObjectThumb(obj, index)
                    if thumb is None:
                        continue
                    if existing_date is not None:
                        delete_public_object("thumbs", thumb_storage_id)
                        print("    Updating thumb #"+str(index)+" for "+str(obj))
                        self.updatedThumbs += 1
                    else:
                        print("    Creating thumb #"+str(index)+" for "+str(obj))
                        self.createdThumbs += 1
                    store_public_object("thumbs",
                                        thumb_storage_id,
                                        thumb,
                                        "image/jpeg")
            if (len(thumb_dates) > (obj.thumbCount or 0)):
                obj.thumbCount = len(thumb_dates)
                app.model.PcObject.check_and_save(obj)
        except Exception as e:
            self.logEvent(LocalProviderEventType.SyncError, e.__class__.__name__)
            self.erroredThumbs += 1
            print('ERROR during handleThumb: '
                  + e.__class__.__name__ + ' ' + str(e))
            traceback.print_tb(e.__traceback__)
            pprint(vars(e))

    def existingObjectOrNone(self, providable_info):
        with app.db.session.no_autoflush:
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
            obj.dateModifiedAtLastProvider = providable_info.dateModifiedAtProvider
            obj.lastProvider = self.dbObject
            if self.offererProvider is not None:
                obj.offerer = self.offererProvider.offerer
            app.model.PcObject.check_and_save(obj)
        except Exception as e:
            self.logEvent(LocalProviderEventType.SyncError, e.__class__.__name__)
            print('ERROR during updateObject: '
                  + e.__class__.__name__+' '+str(e))
            self.erroredObjects += 1
            traceback.print_tb(e.__traceback__)
            pprint(vars(e))

    def logEvent(self, eventType, eventPayload=None):
        pe = LocalProviderEvent()
        pe.type = eventType
        pe.payload = str(eventPayload)
        pe.provider = self.dbObject
        app.db.session.add(pe)
        app.db.session.commit()

    def updateObjects(self, limit=None):
        """Update offerer's objects with this provider."""
        if self.offererProvider is not None:
            app.db.session.add(self.offererProvider)  # FIXME: we should not need this
        providerName = self.__class__.__name__
        if not self.isActive:
            print("Provider "+providerName+" is inactive")
            return
        sys.stdout.write("Updating "
                         + inflect_engine.plural(self.objectType.__name__)
                         + " from provider " + self.name)
        self.logEvent(LocalProviderEventType.SyncStart)
        if self.offererProvider is not None:
            print(" for offerer " + self.offererProvider.offerer.name
                  + " (#" + str(self.offererProvider.offererId) + " / "
                  + humanize(self.offererProvider.offererId) + ") "
                  + " offererIdAtOfferProvider="
                  + self.offererProvider.offererIdAtOfferProvider)
        else:
            print("")
        for providable_infos in self:
            if isinstance(providable_infos, app.model.ProvidableInfo)\
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

            app.db.session.close()
            if self.offererProvider is not None:
                app.db.session.add(self.offererProvider)
            app.db.session.add(self.dbObject)

            if limit is not None and\
               self.checkedObjects >= limit:
                break

        #with app.db.session.no_autoflush:
        #    update = sa.update(self.objectType)\
        #               .where((self.objectType.provider == self.offerer.provider) &\
        #                      ~self.objectType.idAtProviders.in_(self.getDeactivatedObjectIds()))\
        #               .values({'deactivated': True})
        #    app.db.session.execute(update)
        #app.db.session.commit()

        print("  Checked " + str(self.checkedObjects) + " objects")
        print("  Created " + str(self.createdObjects) + " objects")
        print("  Updated " + str(self.updatedObjects) + " objects")
        print("  " + str(self.erroredObjects) + " errors in creations/updates")

        print("  Checked " + str(self.checkedThumbs) + " thumbs")
        print("  Created " + str(self.createdThumbs) + " thumbs")
        print("  Updated " + str(self.updatedThumbs) + " thumbs")
        print("  " + str(self.erroredThumbs) + " errors in thumb creations/updates")
        self.logEvent(LocalProviderEventType.SyncEnd)

app.model.LocalProvider = LocalProvider
