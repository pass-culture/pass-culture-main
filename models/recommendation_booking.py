""" recommendation booking """
from flask import current_app as app

db = app.db


class RecommendationBooking(app.model.PcObject, db.Model):
    recommendationId = db.Column(db.BigInteger,
                                 db.ForeignKey('recommendation.id'),
                                 primary_key=True)

    recommendation = db.relationship(lambda: app.model.Recommendation,
                                     back_populates="recommendationBookings",
                                     foreign_keys=[recommendationId])

    bookingId = db.Column(db.BigInteger,
                          db.ForeignKey('booking.id'),
                          primary_key=True)

    booking = db.relationship(lambda: app.model.Booking,
                              foreign_keys=[bookingId])


app.model.RecommendationBooking = RecommendationBooking
