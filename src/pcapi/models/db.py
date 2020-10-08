import os
from contextlib import ContextDecorator

from flask_sqlalchemy import SQLAlchemy
from postgresql_audit.flask import VersioningManager

db = SQLAlchemy(engine_options={
    'pool_size': int(os.environ.get('DATABASE_POOL_SIZE', 20)),
})

Model = db.Model

versioning_manager = VersioningManager(actor_cls='UserSQLEntity')
versioning_manager.init(Model)


class auto_close_db_transaction(ContextDecorator):
    def __enter__(self, *exc):
        pass

    def __exit__(self, *exc):
        if len(db.session.dirty) > 0:
            raise Exception('Session was left dirty')
        db.session.commit()
        return False
