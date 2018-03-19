""" booking model """
from datetime import datetime
from flask import current_app as app

db = app.db


class Booking(app.model.PcObject,
              db.Model,
              app.model.DeactivableMixin):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    dateModified = db.Column(db.DateTime,
                             nullable=False,
                             default=datetime.now)

    offerId = db.Column(db.BigInteger,
                        db.ForeignKey("offer.id"),
                        nullable=True)

    offer = db.relationship(lambda: app.model.Offer,
                            foreign_keys=[offerId])

    quantity = db.Column(db.Numeric(10, 2),
                         nullable=False)

    referenceId = db.Column(db.BigInteger,
                            db.ForeignKey("reference.id"),
                            nullable=False)

    reference = db.relationship(lambda: app.model.Reference,
                                foreign_keys=[referenceId])

    userId = db.Column(db.BigInteger,
                       db.ForeignKey('user.id'),
                       nullable=False)

    user = db.relationship(lambda: app.model.User,
                           foreign_keys=[userId],
                           backref='userBookings')



app.model.Booking = Booking
