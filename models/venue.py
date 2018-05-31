""" venue """
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

    siret = db.Column(db.String(14))

    address = db.Column(db.String(200), nullable=True)

    departementCode = db.Column(db.String(3), nullable=False, index=True)

    latitude = db.Column(db.Numeric(8, 5), nullable=True)

    longitude = db.Column(db.Numeric(8, 5), nullable=True)

    managingOffererId = db.Column(db.BigInteger,
                                  db.ForeignKey("offerer.id"),
                                  unique=True,
                                  nullable=True)
    managingOfferer = db.relationship(lambda: app.model.Offerer,
                                      foreign_keys=[managingOffererId],
                                      backref='managedVenues')

    #openingHours = db.Column(ARRAY(TIME))
    # Ex: [['09:00', '18:00'], ['09:00', '19:00'], null,  ['09:00', '18:00']]
    # means open monday 9 to 18 and tuesday 9 to 19, closed wednesday,
    # open thursday 9 to 18, closed the rest of the week

Venue.__ts_vector__ = create_tsvector(
    cast(coalesce(Venue.name, ''), TEXT),
    cast(coalesce(Venue.address, ''), TEXT)
)

Venue.__table_args__ = (
    Index(
        'idx_venue_fts',
        Venue.__ts_vector__,
        postgresql_using='gin'
    ),
)

app.model.Venue = Venue
