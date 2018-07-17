from models.deactivable_mixin import DeactivableMixin
from models.has_address_mixin import HasAddressMixin
from models.has_thumb_mixin import HasThumbMixin
from models.needs_validation_mixin import NeedsValidationMixin
from models.occasion import Occasion
from models.offerer import Offerer
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from models.user_offerer import UserOfferer

""" offerer """
from datetime import datetime
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import coalesce

from utils.search import create_tsvector
import sqlalchemy as db


class Offerer(PcObject,
              HasThumbMixin,
              HasAddressMixin,
              ProvidableMixin,
              NeedsValidationMixin,
              DeactivableMixin,
              db.Model):
    id = db.Column(db.BigInteger, primary_key=True)

    dateCreated = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.utcnow)

    name = db.Column(db.String(140), nullable=False)

    users = db.relationship('User',
                            secondary='user_offerer')

    siren = db.Column(db.String(9), nullable=True, unique=True)  # FIXME: should not be nullable, is until we have all SIRENs filled in the DB

    def give_rights(self, user, rights):
        if user:
            user_offerer = UserOfferer()
            user_offerer.offerer = self
            user_offerer.user = user
            user_offerer.rights = rights
            return user_offerer

    def errors(self):
        errors = super(Offerer, self).errors()
        errors.errors.update(HasAddressMixin.errors(self).errors)
        if self.siren is not None\
           and (not len(self.siren) == 9):
                #TODO: or not verify_luhn(self.siren)):
            errors.addError('siren', 'Ce code SIREN est invalide')
        return errors

    @property
    def nOccasions(self):
        return Occasion.query\
                  .filter(Occasion.venueId.in_(list(map(lambda v: v.id,
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
