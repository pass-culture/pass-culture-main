from flask import current_app as app
from postgresql_audit.flask import versioning_manager
from sqlalchemy import text


class VersionedMixin(object):
    __versioned__ = {}

    def activity(self):
        Activity = versioning_manager.activity_cls
        return Activity.query.filter(text("table_name='"+self.__tablename__
                                          + "' AND cast(changed_data->>'id' AS INT) = " + str(self.id)))\
                             .order_by(app.db.desc(Activity.id))


app.model.VersionedMixin = VersionedMixin
