from flask import current_app as app
from sqlalchemy.dialects.postgresql import ARRAY

db = app.db


class Offerer(app.model.PcObject,
              app.model.HasThumbMixin,
              app.model.ProvidableMixin,
              db.Model):
    id = db.Column(db.BigInteger, primary_key=True)

    name = db.Column(db.String(140), nullable=False)

    address = db.Column(db.String(200), nullable=True)

    userOfferers = db.relationship("UserOfferer", back_populates="offerer", lazy='dynamic')

    offererProviders = db.relationship(lambda: app.model.OffererProvider,
                                       back_populates="offerer")

    venueId = db.Column(db.BigInteger,
                        db.ForeignKey("venue.id"),
                        unique=True,
                        nullable=True)
    venue = db.relationship(lambda: app.model.Venue,
                            foreign_keys=[venueId],
                            backref='offerer')


app.model.Offerer = Offerer
