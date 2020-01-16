""" pc """
import os

from flask import Flask
from flask_script import Manager
from mailjet_rest import Client

from models.db import db
from scripts.install import install_scripts
from utils.mailing import MAILJET_API_KEY, MAILJET_API_SECRET

app = Flask(__name__, template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


def create_app(env=None):
    app.env = env
    return app


app.manager = Manager(create_app)

with app.app_context():
    install_scripts()

    app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')

if __name__ == "__main__":
    app.manager.run()
