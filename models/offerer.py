""" offerer """
from datetime import datetime
from flask_sqlalchemy import Model
from sqlalchemy import BigInteger, Column, DateTime, String
from sqlalchemy.orm import relationship

from models.deactivable_mixin import DeactivableMixin
from models.has_address_mixin import HasAddressMixin
from models.has_thumb_mixin import HasThumbMixin
from models.needs_validation_mixin import NeedsValidationMixin
from models.occasion import Occasion
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from models.user_offerer import UserOfferer


class Offerer(PcObject,
              HasThumbMixin,
              HasAddressMixin,
              ProvidableMixin,
              NeedsValidationMixin,
              DeactivableMixin,
              Model):

    id = Column(BigInteger, primary_key=True)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    name = Column(String(140), nullable=False)

    users = relationship('User',
                         secondary='user_offerer')

    siren = Column(String(9), nullable=True, unique=True)  # FIXME: should not be nullable, is until we have all SIRENs filled in the DB

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
