""" pc """
import os
from flask import Flask
from flask_script import Manager

from models.db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_app(env=None):
    app.env = env
    return app

app.manager = Manager(create_app)

with app.app_context():
    import scripts

if __name__ == "__main__":
    app.manager.run()
