import enum

from sqlalchemy import String, Column, Enum

from models.pc_object import PcObject
from models.deactivable_mixin import DeactivableMixin
from models.db import Model


class FeatureToggle(enum.Enum):
    WEBAPP_SIGNUP = 'Permettre aux bénéficiaires de créer un compte'
    FAVORITE_OFFER = 'Permettre aux bénéficiaires d''ajouter des offres en favoris'


class Feature(PcObject, Model, DeactivableMixin):
    name = Column(Enum(FeatureToggle), unique=True, nullable=False)
    description = Column(String(300), nullable=False)

    def as_dict(self, include=None):
        dict_feature = PcObject.as_dict(self, include=include)
        dict_feature['nameKey'] = str(self.name).replace('FeatureToggle.', '')
        return dict_feature
