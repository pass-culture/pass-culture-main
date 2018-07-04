""" offerer """
from datetime import datetime
from flask import current_app as app
from luhn import verify as verify_luhn
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import coalesce

from utils.search import create_tsvector

db = app.db


class Offerer(app.model.PcObject,
              app.model.HasThumbMixin,
              app.model.HasAddressMixin,
              app.model.ProvidableMixin,
              app.model.NeedsValidationMixin,
              app.model.DeactivableMixin,
              db.Model):
    id = db.Column(db.BigInteger, primary_key=True)

    dateCreated = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.utcnow)

    name = db.Column(db.String(140), nullable=False)

    users = db.relationship(lambda: app.model.User,
                            secondary='user_offerer')

    siren = db.Column(db.String(9), nullable=True, unique=True)  # FIXME: should not be nullable, is until we have all SIRENs filled in the DB

    def give_rights(self, user, rights):
        if user:
            user_offerer = app.model.UserOfferer()
            user_offerer.offerer = self
            user_offerer.user = user
            user_offerer.rights = rights
            return user_offerer

    def errors(self):
        errors = super(Offerer, self).errors()
        errors.errors.update(app.model.HasAddressMixin.errors(self).errors)
        if self.siren is not None\
           and (not len(self.siren) == 9):
                #TODO: or not verify_luhn(self.siren)):
            errors.addError('siren', 'Ce code SIREN est invalide')
        return errors

    @property
    def nOccasions(self):
        return app.model.Occasion.query\
                  .filter(app.model.Occasion.venueId.in_(list(map(lambda v: v.id,
                                                                  self.managedVenues)))).count()


Offerer.__ts_vector__ = create_tsvector(
    cast(coalesce(Offerer.name, ''), TEXT),
    cast(coalesce(Offerer.address, ''), TEXT),
    cast(coalesce(Offerer.siren, ''), TEXT)
)

Offerer.__table_args__ = (
    Index(
        'idx_offerer_fts',
        Offerer.__ts_vector__,
        postgresql_using='gin'
    ),
)

app.model.Offerer = Offerer
