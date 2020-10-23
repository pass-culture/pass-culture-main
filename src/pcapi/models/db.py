import os

from flask_sqlalchemy import SQLAlchemy
from postgresql_audit.flask import VersioningManager

db = SQLAlchemy(engine_options={
    'pool_size': int(os.environ.get('DATABASE_POOL_SIZE', 20)),
})

Model = db.Model

versioning_manager = VersioningManager(actor_cls='UserSQLEntity')
versioning_manager.init(Model)
