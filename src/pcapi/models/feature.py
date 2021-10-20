import enum
import logging

from alembic import op
import flask
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql import text

from pcapi import settings
from pcapi.models.db import Model
from pcapi.models.db import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject


logger = logging.getLogger(__name__)


class FeatureToggle(enum.Enum):
    BENEFICIARIES_IMPORT = "Permettre limport des comptes jeunes depuis DMS"
    QR_CODE = "Permettre la validation dune contremarque via QR code"
    SYNCHRONIZE_ALLOCINE = "Permettre la synchronisation journalière avec Allociné"
    SYNCHRONIZE_BANK_INFORMATION = (
        "Permettre la synchronisation journalière avec DMS pour récupérer les informations bancaires des acteurs"
    )
    SYNCHRONIZE_TITELIVE_PRODUCTS = "Permettre limport journalier du référentiel des livres"
    SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION = "Permettre limport journalier des résumés des livres"
    SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS = "Permettre limport journalier des couvertures de livres"
    UPDATE_BOOKING_USED = "Permettre la validation automatique des contremarques 48h après la fin de lévènement"
    WEBAPP_SIGNUP = "Permettre aux bénéficiaires de créer un compte"
    API_SIRENE_AVAILABLE = "Active les fonctionnalitées liées à l'API Sirene"
    WEBAPP_HOMEPAGE = "Permettre l affichage de la nouvelle page d accueil de la webapp"
    ALLOW_IDCHECK_REGISTRATION = "Autoriser les utilisateurs de 18 ans à suivre le parcours d inscription ID Check"
    ALLOW_IDCHECK_UNDERAGE_REGISTRATION = (
        "Autoriser les utilisateurs de moins de 15 à 17 ans à suivre le parcours d inscription ID Check"
    )
    ENABLE_NATIVE_APP_RECAPTCHA = "Active le reCaptacha sur l'API native"
    OFFER_VALIDATION_MOCK_COMPUTATION = "Active le calcul automatique de validation d'offre depuis le nom de l'offre"
    AUTO_ACTIVATE_DIGITAL_BOOKINGS = (
        "Activer (marquer comme utilisée) les réservations dès leur création pour les offres digitales"
    )
    ENABLE_ACTIVATION_CODES = "Permet la création de codes d'activation"
    ENABLE_PHONE_VALIDATION = "Active la validation du numéro de téléphone"  # TODO (viconnex) remove when FORCE_PHONE_VALIDATION is released in production
    FORCE_PHONE_VALIDATION = "Forcer la validation du numéro de téléphone pour devenir bénéficiaire"
    ENABLE_NATIVE_ID_CHECK_VERSION = "Utilise la version d'ID-Check intégrée à l'application native"
    ENABLE_NEW_VENUE_PAGES = "Utiliser la nouvelle version des pages d'edition et de creation de lieux"
    ENABLE_IDCHECK_FRAUD_CONTROLS = "Active les contrôles de sécurité en sortie du process ID Check"
    DISPLAY_DMS_REDIRECTION = "Affiche une redirection vers DMS si ID Check est KO"
    ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING = (
        "Active le mode debug Firebase pour l'Id Check intégrée à l'application native"
    )
    ENABLE_ID_CHECK_RETENTION = "Active le mode bassin de retention dans Id Check V2"
    ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION = (
        "Active le champ isbn obligatoire lors de la création d'offre de type LIVRE_EDITION"
    )
    USE_APP_SEARCH_ON_NATIVE_APP = "Utiliser App Search au lieu d'Algolia sur l'app native"
    USE_APP_SEARCH_ON_WEBAPP = "Utiliser App Search au lieu d'Algolia sur la webapp"
    ID_CHECK_ADDRESS_AUTOCOMPLETION = "Autocomplétion de l'adresse lors du parcours IDCheck"
    USER_PROFILING_FRAUD_CHECK = "Détection de la fraude basée sur le profil de l'utilisateur"
    BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS = "Active la validation d'un bénéficiaire via les contrôles de sécurité"
    ENABLE_VENUE_WITHDRAWAL_DETAILS = "Active les modalités de retrait sur la page lieu"
    PERF_VENUE_STATS = "Permet de basculer vers une nouvelle implémentation performante de la page d'accueil pro contenant les indicateurs statistiques par venue"
    WEBAPP_V2_ENABLED = "Utiliser la nouvelle web app (décli web/v2) au lieu de l'ancienne"
    PRO_REIMBURSEMENTS_FILTERS = "Permet de filtrer la liste de remboursements"
    ENABLE_NATIVE_EAC_INDIVIDUAL = "Active l'EAC individuel sur l'app native"
    ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS = "Active le nouveau délai de rétractation pour les livres"
    ENABLE_DMS_GRAPHQL_API = "Utilise l'API GraphQL de DMS"
    ENABLE_EDUCONNECT_AUTHENTICATION = "Active l'authentification via educonnect sur l'app native"
    ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS = (
        "Utiliser Sendinblue pour envoyer les emails transactionnels (Ceux qui ont été migrés)"
    )

    def is_active(self) -> bool:
        if flask.has_request_context():
            if not hasattr(flask.request, "_cached_features"):
                setattr(flask.request, "_cached_features", {})

            cached_value = flask.request._cached_features.get(self.name)
            if cached_value is not None:
                return cached_value

        value = Feature.query.filter_by(name=self.name).one().isActive

        if flask.has_request_context():
            flask.request._cached_features[self.name] = value

        return value


class Feature(PcObject, Model, DeactivableMixin):
    name = Column(Text, unique=True, nullable=False)
    description = Column(String(300), nullable=False)

    @property
    def nameKey(self) -> str:
        return str(self.name).replace("FeatureToggle.", "")


FEATURES_DISABLED_BY_DEFAULT = (
    FeatureToggle.ALLOW_IDCHECK_UNDERAGE_REGISTRATION,
    FeatureToggle.FORCE_PHONE_VALIDATION,
    FeatureToggle.ENABLE_NEW_VENUE_PAGES,
    FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING,
    FeatureToggle.ENABLE_ID_CHECK_RETENTION,
    FeatureToggle.ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION,
    FeatureToggle.USE_APP_SEARCH_ON_NATIVE_APP,
    FeatureToggle.USE_APP_SEARCH_ON_WEBAPP,
    FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION,
    FeatureToggle.USER_PROFILING_FRAUD_CHECK,
    FeatureToggle.ENABLE_VENUE_WITHDRAWAL_DETAILS,
    FeatureToggle.PERF_VENUE_STATS,
    FeatureToggle.WEBAPP_V2_ENABLED,
    FeatureToggle.PRO_REIMBURSEMENTS_FILTERS,
    FeatureToggle.ENABLE_NEW_AUTO_EXPIRY_DELAY_BOOKS_BOOKINGS,
    FeatureToggle.ENABLE_DMS_GRAPHQL_API,
    FeatureToggle.ENABLE_EDUCONNECT_AUTHENTICATION,
    FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS,
)

if not settings.IS_DEV:
    FEATURES_DISABLED_BY_DEFAULT += (FeatureToggle.ENABLE_NATIVE_EAC_INDIVIDUAL,)


def add_feature_to_database(feature: FeatureToggle) -> None:
    """This function is to be used as the "upgrade" function of a
    migration when introducing a new feature flag.
    """
    statement = text(
        """
        INSERT INTO feature (name, description, "isActive")
        VALUES (:name, :description, :initial_value)
        """
    )
    statement = statement.bindparams(
        name=feature.name,
        description=feature.value,
        initial_value=feature not in FEATURES_DISABLED_BY_DEFAULT,
    )
    op.execute(statement)


def remove_feature_from_database(feature: FeatureToggle) -> None:
    """This function is to be used as the "downgrade" function of a
    migration when introducing a new feature flag.
    """
    statement = text("DELETE FROM feature WHERE name = :name").bindparams(name=feature.name)
    op.execute(statement)


def install_feature_flags() -> None:
    installed_flag_names = {f[0] for f in Feature.query.with_entities(Feature.name).all()}
    defined_flag_name = {f.name for f in list(FeatureToggle)}

    to_install_flags = defined_flag_name - installed_flag_names
    to_remove_flags = installed_flag_names - defined_flag_name

    for flag in to_install_flags:
        db.session.add(
            Feature(
                name=FeatureToggle[flag].name,
                description=FeatureToggle[flag].value,
                isActive=FeatureToggle[flag] not in FEATURES_DISABLED_BY_DEFAULT,
            ),
        )

    db.session.commit()

    if to_remove_flags:
        logger.error("The following feature flags are present in database but not present in code: %s", to_remove_flags)
