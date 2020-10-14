import contextlib
import enum

from sqlalchemy import String, Column, Enum

from pcapi.models.db import Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject


class FeatureToggle(enum.Enum):
    BENEFICIARIES_IMPORT = 'Permettre l''import des comptes jeunes depuis DMS'
    DEGRESSIVE_REIMBURSEMENT_RATE = 'Permettre le remboursement avec un barème dégressif par lieu'
    FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE = 'Permet la recherche de mots-clés dans les tables structures' \
                                                ' et lieux en plus de celles des offres'
    QR_CODE = 'Permettre la validation d''une contremarque via QR code'
    SEARCH_ALGOLIA = 'Permettre la recherche via Algolia'
    SYNCHRONIZE_ALGOLIA = 'Permettre la mise à jour des données pour la recherche via Algolia'
    SYNCHRONIZE_ALLOCINE = 'Permettre la synchronisation journalière avec Allociné'
    SYNCHRONIZE_BANK_INFORMATION = 'Permettre la synchronisation journalière avec DMS' \
                                   ' pour récupérer les informations bancaires des acteurs'
    SYNCHRONIZE_LIBRAIRES = 'Permettre la synchronisation journalière avec leslibraires.fr'
    SYNCHRONIZE_TITELIVE = 'Permettre la synchronisation journalière avec TiteLive / Epagine'
    SYNCHRONIZE_TITELIVE_PRODUCTS = 'Permettre l''import journalier du référentiel des livres'
    SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION = 'Permettre l''import journalier des résumés des livres'
    SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS = 'Permettre l''import journalier des couvertures de livres'
    UPDATE_DISCOVERY_VIEW = 'Permettre la mise à jour des données du carousel'
    UPDATE_BOOKING_USED = 'Permettre la validation automatique des contremarques 48h après la fin de l''évènement'
    WEBAPP_SIGNUP = 'Permettre aux bénéficiaires de créer un compte'
    RECOMMENDATIONS_WITH_GEOLOCATION = 'Permettre aux utilisateurs d''avoir accès aux offres à 100km de leur position'
    SAVE_SEEN_OFFERS = 'Enregistrer en base les offres déjà vues par les utilisateurs'
    API_SIRENE_AVAILABLE = 'Active les fonctionnalitées liées à l\'API Sirene'
    CLEAN_DISCOVERY_VIEW = 'Nettoyer les données en base de données liées à la mise à jour régulière'
    WEBAPP_HOMEPAGE = "Permettre l affichage de la nouvelle page d accueil de la webapp"
    WEBAPP_PROFILE_PAGE = "Permettre l affichage de la page profil (route dédiée + navbar)"


class Feature(PcObject, Model, DeactivableMixin):
    name = Column(Enum(FeatureToggle), index=True, unique=True, nullable=False)
    description = Column(String(300), nullable=False)

    @property
    def nameKey(self):
        return str(self.name).replace('FeatureToggle.', '')


@contextlib.contextmanager
def override_features(**overrides):
    """A context manager that temporarily enables and/or disables features.

    It can also be used as a function decorator.

    Usage:

        with override_features(QR_CODE=False):
            call_some_function()

        @override_features(
            SYNCHRONIZE_ALGOLIA=True,
            QR_CODE=False,
        )
        def test_something():
            pass  # [...]
    """
    state = {
        feature.name: is_active
        for feature, is_active in (
            Feature.query
            .filter(Feature.name.in_(overrides))
            .with_entities(Feature.name, Feature.isActive)
            .all()
        )
    }
    # Yes, the following may perform multiple SQL queries. It's fine,
    # we will probably not toggle thousands of features in each call.
    apply_to_revert = {}
    for name, status in overrides.items():
        if status != state[name]:
            apply_to_revert[name] = not status
            Feature.query.filter_by(name=name).update({'isActive': status})

    try:
        yield
    finally:
        for name, status in apply_to_revert.items():
            Feature.query.filter_by(name=name).update({'isActive': status})
