from flask_sqlalchemy import SQLAlchemy

from postgresql_audit.flask import versioning_manager

db = SQLAlchemy()

Model = db.Model

versioning_manager.init(Model)
