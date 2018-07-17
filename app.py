""" app """
import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import orm
from postgresql_audit.flask import versioning_manager

from models.mediation import Mediation
from models.pc_object import PcObject
from utils.config import IS_DEV

app = Flask(__name__, static_url_path='/static')

app.secret_key = os.environ.get('FLASK_SECRET', '+%+3Q23!zbc+!Dd@')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

PcObject.db = SQLAlchemy(app)

import utils.events
import utils.ts_vectors

print("PcObject.db.Model", PcObject.db.Model)

versioning_manager.init(PcObject.db.Model)

orm.configure_mappers()
# FIXME: This is seriously ugly... (based on https://github.com/kvesteri/postgresql-audit/issues/21)
try:
    versioning_manager.transaction_cls.__table__.create(PcObject.db.session.get_bind())
except ProgrammingError:
    pass
try:
    versioning_manager.activity_cls.__table__.create(PcObject.db.session.get_bind())
except ProgrammingError:
    pass
PcObject.db.create_all()
PcObject.db.engine.execute("CREATE INDEX IF NOT EXISTS idx_activity_objid ON activity(cast(changed_data->>'id' AS INT));")

PcObject.db.session.commit()

Mediation.upsertTutoMediations()

cors = CORS(app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

# make Werkzeug match routing rules with or without a trailing slash
app.url_map.strict_slashes = False

with app.app_context():
    import utils.login_manager
    import utils.logger
    import local_providers
    import routes


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=IS_DEV, use_reloader=True)
