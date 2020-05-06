import os

from functools import wraps
from models.db import db
from flask import Flask
from sqlalchemy import orm


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
orm.configure_mappers()

def job_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        worker_application = app
        with worker_application.app_context():
            return func(*args, **kwargs)
    return wrapper
