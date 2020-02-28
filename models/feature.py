import enum

from sqlalchemy import String, Column, Enum

from models.db import Model
from models.deactivable_mixin import DeactivableMixin
from models.pc_object import PcObject


class FeatureToggle(enum.Enum):
    WEBAPP_SIGNUP = 'Permettre aux bénéficiaires de créer un compte'
    DEGRESSIVE_REIMBURSEMENT_RATE = 'Permettre le remboursement avec un barème dégressif par lieu'
    QR_CODE = 'Permettre la validation d''une contremarque via QR code'
    FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE = 'Permet la recherche de mots-clés dans les tables structures' \
                                                ' et lieux en plus de celles des offres'
    SEARCH_ALGOLIA = 'Permettre la recherche via Algolia'
    SEARCH_LEGACY = "Permettre la recherche classique"

    SYNCHRONIZE_BANK_INFORMATION = 'Permettre la synchronisation journalière avec DMS' \
                                   ' pour récupérer les informations bancaires des acteurs'
    BENEFICIARIES_IMPORT = 'Permettre l''import des comptes jeunes depuis DMS'
    SYNCHRONIZE_TITELIVE_PRODUCTS = 'Permettre l''import journalier du référentiel des livres'
    SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION = 'Permettre l''import journalier des résumés des livres'
    SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS = 'Permettre l''import journalier des couvertures de livres'
    SYNCHRONIZE_TITELIVE = 'Permettre la synchronisation journalière avec TiteLive / Epagine'
    SYNCHRONIZE_ALLOCINE = 'Permettre la synchronisation journalière avec Allociné'
    SYNCHRONIZE_LIBRAIRES = 'Permettre la synchronisation journalière avec leslibraires.fr'
    UPDATE_DISCOVERY_VIEW = 'Permettre la mise à jour des données du carousel'
    UPDATE_BOOKING_USED = 'Permettre la validation automatique des contremarques 48h après la fin de l''évènement'
    RESEND_EMAIL_IN_ERROR = 'Permettre de renvoyer les emails en erreur'
    SYNCHRONIZE_ALGOLIA = 'Permettre la mise à jour des données pour la recherche via Algolia'


class Feature(PcObject, Model, DeactivableMixin):
    name = Column(Enum(FeatureToggle), index=True, unique=True, nullable=False)
    description = Column(String(300), nullable=False)

    @property
    def nameKey(self):
        return str(self.name).replace('FeatureToggle.', '')
