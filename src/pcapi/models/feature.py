import contextlib
import enum
from typing import Generator

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text

from pcapi.models.db import Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject


class FeatureToggle(enum.Enum):
    BENEFICIARIES_IMPORT = "Permettre limport des comptes jeunes depuis DMS"
    DEGRESSIVE_REIMBURSEMENT_RATE = "Permettre le remboursement avec un barème dégressif par lieu"
    FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE = (
        "Permet la recherche de mots-clés dans les tables structures et lieux en plus de celles des offres"
    )
    QR_CODE = "Permettre la validation dune contremarque via QR code"
    SEARCH_ALGOLIA = "Permettre la recherche via Algolia"
    SYNCHRONIZE_ALGOLIA = "Permettre la mise à jour des données pour la recherche via Algolia"
    SYNCHRONIZE_ALLOCINE = "Permettre la synchronisation journalière avec Allociné"
    SYNCHRONIZE_BANK_INFORMATION = (
        "Permettre la synchronisation journalière avec DMS pour récupérer les informations bancaires des acteurs"
    )
    SYNCHRONIZE_LIBRAIRES = "Permettre la synchronisation journalière avec leslibraires.fr"
    SYNCHRONIZE_TITELIVE = "Permettre la synchronisation journalière avec TiteLive / Epagine"
    SYNCHRONIZE_TITELIVE_PRODUCTS = "Permettre limport journalier du référentiel des livres"
    SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION = "Permettre limport journalier des résumés des livres"
    SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS = "Permettre limport journalier des couvertures de livres"
    UPDATE_BOOKING_USED = "Permettre la validation automatique des contremarques 48h après la fin de lévènement"
    WEBAPP_SIGNUP = "Permettre aux bénéficiaires de créer un compte"
    API_SIRENE_AVAILABLE = "Active les fonctionnalitées liées à l'API Sirene"
    WEBAPP_HOMEPAGE = "Permettre l affichage de la nouvelle page d accueil de la webapp"
    WEBAPP_PROFILE_PAGE = "Permettre l affichage de la page profil (route dédiée + navbar)"
    APPLY_BOOKING_LIMITS_V2 = "Permettre l affichage des nouvelles règles de génération de portefeuille des jeunes"
    ALLOW_IDCHECK_REGISTRATION = "Autoriser les utilisateurs à suivre le parcours d inscription ID Check"
    WHOLE_FRANCE_OPENING = "Ouvre le service à la France entière"
    PRO_HOMEPAGE = "Permettre l affichage de la nouvelle page d accueil du portail pro"


class Feature(PcObject, Model, DeactivableMixin):
    name = Column(Text, unique=True, nullable=False)
    description = Column(String(300), nullable=False)

    @property
    def nameKey(self) -> str:
        return str(self.name).replace("FeatureToggle.", "")


FEATURES_DISABLED_BY_DEFAULT = (
    FeatureToggle.APPLY_BOOKING_LIMITS_V2,
    FeatureToggle.WHOLE_FRANCE_OPENING,
)


@contextlib.contextmanager
def override_features(**overrides) -> Generator:
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
    state = dict(Feature.query.filter(Feature.name.in_(overrides)).with_entities(Feature.name, Feature.isActive).all())
    # Yes, the following may perform multiple SQL queries. It's fine,
    # we will probably not toggle thousands of features in each call.
    apply_to_revert = {}
    for name, status in overrides.items():
        if status != state[name]:
            apply_to_revert[name] = not status
            Feature.query.filter_by(name=name).update({"isActive": status})

    try:
        yield
    finally:
        for name, status in apply_to_revert.items():
            Feature.query.filter_by(name=name).update({"isActive": status})
