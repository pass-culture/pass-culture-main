""" reference model """
from datetime import datetime
from flask import current_app as app

db = app.db


class Reference(app.model.PcObject,
                db.Model):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    token = db.Column(db.String(10),
                      nullable=False)

    dateModified = db.Column(db.DateTime,
                             nullable=False,
                             default=datetime.now)

    bookingId = db.Column(db.BigInteger,
                          db.ForeignKey('booking.id'))

    booking = db.relationship(lambda: app.model.Booking,
                              foreign_keys=[bookingId])


app.model.Reference = Reference
