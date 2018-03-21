from flask import current_app as app

db = app.db


class UserMediationBooking(app.model.PcObject, db.Model):
    userMediationId = db.Column(db.BigInteger,
                                db.ForeignKey('user_mediation.id'),
                                primary_key=True)

    userMediation = db.relationship(lambda: app.model.UserMediation,
                                    back_populates="userMediationBookings",
                                    foreign_keys=[userMediationId])

    bookingId = db.Column(db.BigInteger,
                          db.ForeignKey('booking.id'),
                          primary_key=True)

    booking = db.relationship(lambda: app.model.Booking,
                              foreign_keys=[bookingId])


app.model.UserMediationBooking = UserMediationBooking
