from utils.config import IS_DEV
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from postgresql_audit.flask import versioning_manager
import sqlalchemy as sa

from utils.attr_dict import AttrDict
from sqlalchemy.exc import ProgrammingError


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pass_culture:passq@postgres/pass_culture'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_ECHO'] = IS_DEV
app.db = SQLAlchemy(app)
app.model = AttrDict()

versioning_manager.init(app.db.Model)
import models.versioned_mixin

import models.api_errors
import models.pc_object

import models.deactivable_mixin
import models.extra_data_mixin
import models.has_thumb_mixin
import models.providable_mixin

import models.event
import models.event_occurence
import models.mediation
import models.offer
import models.offerer
import models.offerer_provider
import models.local_provider_event
import models.local_provider
import models.provider
import models.thing
import models.user_mediation
import models.user_mediation_offer
import models.user_offerer
import models.user
import models.venue

sa.orm.configure_mappers()
# FIXME: This is seriously ugly... (based on https://github.com/kvesteri/postgresql-audit/issues/21)
try:
    versioning_manager.transaction_cls.__table__.create(app.db.session.get_bind())
except ProgrammingError:
    pass
try:
    versioning_manager.activity_cls.__table__.create(app.db.session.get_bind())
except ProgrammingError:
    pass
app.db.create_all()
app.db.engine.execute("CREATE INDEX IF NOT EXISTS idx_activity_objid ON activity(cast(changed_data->>'id' AS INT));")


app.db.session.commit()
