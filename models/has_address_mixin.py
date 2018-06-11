from flask import current_app as app

db = app.db

# TODO: turn this into a custom type "Adress" ?


class HasAddressMixin(object):
    address = db.Column(db.String(200), nullable=True)

    postalCode = db.Column(db.String(6), nullable=True)

    city = db.Column(db.String(50), nullable=True)


app.model.HasAddressMixin = HasAddressMixin
