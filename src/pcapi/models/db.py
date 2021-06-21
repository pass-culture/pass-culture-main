from flask import json
from flask_sqlalchemy import SQLAlchemy

from pcapi import settings


engine_options = {"json_serializer": json.dumps, "pool_size": settings.DATABASE_POOL_SIZE}

db_options = []
if settings.DATABASE_LOCK_TIMEOUT:
    db_options.append("-c lock_timeout=%i" % settings.DATABASE_LOCK_TIMEOUT)
if settings.DATABASE_STATEMENT_TIMEOUT:
    db_options.append("-c statement_timeout=%i" % settings.DATABASE_STATEMENT_TIMEOUT)

if db_options:
    engine_options["connect_args"] = {"options": " ".join(db_options)}

db = SQLAlchemy(engine_options=engine_options)

Model = db.Model
