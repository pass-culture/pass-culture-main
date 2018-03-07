from flask import current_app as app

db = app.db

class HasThumbMixin(object):
    thumbCount = db.Column(db.Integer(), nullable=False, default=0)
    firstThumbDominantColor = db.Column(db.Binary(3), nullable=True)

app.model.HasThumbMixin = HasThumbMixin
