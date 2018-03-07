from flask import current_app as app
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import coalesce

from utils.search import create_tsvector

db = app.db


class Venue(app.model.PcObject,
            app.model.HasThumbMixin,
            app.model.ProvidableMixin,
            db.Model):
    id = db.Column(db.BigInteger, primary_key=True)

    name = db.Column(db.String(140), nullable=False)

    address = db.Column(db.String(200), nullable=True)

    latitude = db.Column(db.Numeric(8, 5), nullable=True)

    longitude = db.Column(db.Numeric(8, 5), nullable=True)

Venue.__ts_vector__ = create_tsvector(
    cast(coalesce(Venue.name, ''), TEXT)
)

Venue.__table_args__ = (
    Index(
        'idx_venue_fts',
        Venue.__ts_vector__,
        postgresql_using='gin'
    ),
)

app.model.Venue = Venue
