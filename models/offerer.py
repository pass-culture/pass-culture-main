""" offerer """
from flask import current_app as app
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import coalesce

from utils.search import create_tsvector

db = app.db


class Offerer(app.model.PcObject,
              app.model.HasThumbMixin,
              app.model.HasAddressMixin,
              app.model.ProvidableMixin,
              app.model.DeactivableMixin,
              db.Model):
    id = db.Column(db.BigInteger, primary_key=True)

    name = db.Column(db.String(140), nullable=False)

    address = db.Column(db.String(200), nullable=True)

    users = db.relationship(lambda: app.model.User,
                            secondary='user_offerer')

    bookingEmail = db.Column(db.String(120), nullable=False)

    siren = db.Column(db.String(9), nullable=False)

    def make_admin(self, admin):
        if admin:
            user_offerer = app.model.UserOfferer()
            user_offerer.offerer = self
            user_offerer.user = admin
            user_offerer.rights = app.model.RightsType.admin
            return user_offerer


Offerer.__ts_vector__ = create_tsvector(
    cast(coalesce(Offerer.name, ''), TEXT),
    cast(coalesce(Offerer.address, ''), TEXT),
    cast(coalesce(Offerer.siren, ''), TEXT)
)

Offerer.__table_args__ = (
    Index(
        'idx_offerer_fts',
        Offerer.__ts_vector__,
        postgresql_using='gin'
    ),
)

app.model.Offerer = Offerer
