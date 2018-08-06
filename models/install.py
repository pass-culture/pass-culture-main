""" install """
from sqlalchemy import orm
from sqlalchemy.exc import ProgrammingError
from postgresql_audit.flask import versioning_manager

from models.db import db, Model
from models.mediation import upsertTutoMediations

def install_models():

    versioning_manager.init(Model)

    orm.configure_mappers()
    # FIXME: This is seriously ugly... (based on https://github.com/kvesteri/postgresql-audit/issues/21)
    try:
        versioning_manager.transaction_cls.__table__.create(db.session.get_bind())
    except ProgrammingError:
        pass
    try:
        versioning_manager.activity_cls.__table__.create(db.session.get_bind())
    except ProgrammingError:
        pass
    db.create_all()
    db.engine.execute("CREATE INDEX IF NOT EXISTS idx_activity_objid ON activity(cast(changed_data->>'id' AS INT));")
    db.session.commit()

    upsertTutoMediations()
