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
              app.model.ProvidableMixin,
              db.Model):
    id = db.Column(db.BigInteger, primary_key=True)

    name = db.Column(db.String(140), nullable=False)

    address = db.Column(db.String(200), nullable=True)

    users = db.relationship(lambda: app.model.User,
                            secondary='user_offerer')

    offererProviders = db.relationship(lambda: app.model.OffererProvider,
                                       back_populates="offerer")


    bookingEmail = db.Column(db.String(120), nullable=False)

    siren = db.Column(db.String(9))

Offerer.__ts_vector__ = create_tsvector(
    cast(coalesce(Offerer.name, ''), TEXT),
    cast(coalesce(Offerer.address, ''), TEXT)
)

Offerer.__table_args__ = (
    Index(
        'idx_offerer_fts',
        Offerer.__ts_vector__,
        postgresql_using='gin'
    ),
)

app.model.Offerer = Offerer
