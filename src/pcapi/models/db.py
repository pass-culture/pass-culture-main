from flask_sqlalchemy import SQLAlchemy
from postgresql_audit.flask import VersioningManager

from pcapi import settings


db = SQLAlchemy(
    engine_options={
        "pool_size": settings.DATABASE_POOL_SIZE,
    }
)

Model = db.Model

versioning_manager = VersioningManager(actor_cls="User")
versioning_manager.init(Model)
