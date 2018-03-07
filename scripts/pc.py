from flask import Flask
from flask_script import Manager

app = Flask(__name__)


def create_app(env=None):
    app.env = env
    return app


app.manager = Manager(create_app)

with app.app_context():
    import models
    import local_providers
    import scripts

if __name__ == "__main__":
    app.manager.run()
