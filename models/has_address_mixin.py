from flask import current_app as app

db = app.db

# TODO: turn this into a custom type "Adress" ?


class HasAddressMixin(object):
    address = db.Column(db.String(200), nullable=False)

    postalCode = db.Column(db.String(6), nullable=False)

    city = db.Column(db.String(50), nullable=False)


app.model.HasAddressMixin = HasAddressMixin
