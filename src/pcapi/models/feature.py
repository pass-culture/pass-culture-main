import enum

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text

from pcapi.models.db import Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject


class FeatureToggle(enum.Enum):
    BENEFICIARIES_IMPORT = "Permettre limport des comptes jeunes depuis DMS"
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
    PARALLEL_SYNCHRONIZATION_OF_VENUE_PROVIDER = (
        "Active la parallèlisation des opérations de synchronisation pour les VenueProvider"
    )
    ENABLE_WHOLE_VENUE_PROVIDER_ALGOLIA_INDEXATION = "Active la réindexation globale sur Algolia des VenueProvider"
    SYNCHRONIZE_VENUE_PROVIDER_IN_WORKER = "Effectue la première synchronisation des venue_provider dans le worker"
    ENABLE_NATIVE_APP_RECAPTCHA = "Active le reCaptacha sur l'API native"
    FNAC_SYNCHRONIZATION_V2 = "Active la synchronisation FNAC v2 : synchronisation par batch"


class Feature(PcObject, Model, DeactivableMixin):
    name = Column(Text, unique=True, nullable=False)
    description = Column(String(300), nullable=False)

    @property
    def nameKey(self) -> str:
        return str(self.name).replace("FeatureToggle.", "")


FEATURES_DISABLED_BY_DEFAULT = (
    FeatureToggle.APPLY_BOOKING_LIMITS_V2,
    FeatureToggle.WHOLE_FRANCE_OPENING,
    FeatureToggle.PRO_HOMEPAGE,
)
