import secrets

from flask import current_app as app

db = app.db


def generate_token():
    return secrets.token_urlsafe(20)


class NeedsValidationMixin(object):
    def __init__(self, *args, **kwargs):
        super(NeedsValidationMixin, self).__init__(*args, **kwargs)
        self.validationToken = generate_token()

    validationToken = db.Column(db.String(27),
                                unique=True,
                                nullable=True)

    @property
    def queryValidated(self):
        return self.query.filter(NeedsValidationMixin.validationToken == None)

    @property
    def isValidated(self):
        return (self.validationToken is None)



app.model.NeedsValidationMixin = NeedsValidationMixin
