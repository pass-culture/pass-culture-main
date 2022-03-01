import enum
import logging

from alembic import op
import flask
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql import text

from pcapi.models import Model
from pcapi.models import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject


logger = logging.getLogger(__name__)


class FeatureToggle(enum.Enum):
    ALLOW_EMPTY_USER_PROFILING = "Autorise les inscriptions de bénéficiaires sans profile Threat Metrix"
    ALLOW_IDCHECK_REGISTRATION = "Autoriser les utilisateurs de 18 ans à suivre le parcours d inscription ID Check"
    ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE = (
        "Autoriser la redirection vers Ubble (en backup) pour les utilisateurs éligibles à éduconnect"
    )
    ALLOW_IDCHECK_UNDERAGE_REGISTRATION = (
        "Autoriser les utilisateurs de moins de 15 à 17 ans à suivre le parcours d inscription ID Check"
    )
    API_SIRENE_AVAILABLE = "Active les fonctionnalitées liées à l'API Sirene"
    AUTO_ACTIVATE_DIGITAL_BOOKINGS = (
        "Activer (marquer comme utilisée) les réservations dès leur création pour les offres digitales"
    )
    BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS = "Active la validation d'un bénéficiaire via les contrôles de sécurité"
    DISPLAY_DMS_REDIRECTION = "Affiche une redirection vers DMS si ID Check est KO"
    ENABLE_ACTIVATION_CODES = "Permet la création de codes d'activation"
    ENABLE_CULTURAL_SURVEY = "Activer l'affichage du questionnaire des pratiques initiales pour les bénéficiaires"
    ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18 = (
        "Permet l'affichage du lien vers DMS sur la page de maintenance pour les 18 ans"
    )
    ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE = (
        "Permet l'affichage du lien vers DMS sur la page de maintenance pour les 15-17 ans"
    )
    ENABLE_DUPLICATE_USER_RULE_WITHOUT_BIRTHDATE = "Utiliser la nouvelle règle de détection d'utilisateur en doublon"
    ENABLE_EDUCONNECT_AUTHENTICATION = "Active l'authentification via educonnect sur l'app native"
    ENABLE_ID_CHECK_RETENTION = "Active le mode bassin de retention dans Id Check V2"
    ENABLE_IDCHECK_FRAUD_CONTROLS = "Active les contrôles de sécurité en sortie du process ID Check"
    ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION = (
        "Active le champ isbn obligatoire lors de la création d'offre de type LIVRE_EDITION"
    )
    ENABLE_NATIVE_APP_RECAPTCHA = "Active le reCaptacha sur l'API native"
    ENABLE_NATIVE_CULTURAL_SURVEY = (
        "Active le Questionnaire des pratiques initiales natif (non TypeForm) sur l'app native et décli web"
    )
    ENABLE_NATIVE_ID_CHECK_VERSION = "Utilise la version d'ID-Check intégrée à l'application native"
    ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING = (
        "Active le mode debug Firebase pour l'Id Check intégrée à l'application native"
    )
    ENABLE_NEW_BOOKING_FILTERS = "Active les nouveaux filtres sur les statuts pour la page de réservations"
    ENABLE_NEW_VENUE_PAGES = "Utiliser la nouvelle version des pages d'edition et de creation de lieux"
    ENABLE_PHONE_VALIDATION = "Active la validation du numéro de téléphone"  # TODO (viconnex) remove when FORCE_PHONE_VALIDATION is released in production
    ENABLE_PRO_BOOKINGS_V2 = "Activer l'affichage de la page booking avec la nouvelle architecture."
    ENABLE_UBBLE = "Active la vérification d'identité par Ubble"
    ENABLE_UBBLE_SUBSCRIPTION_LIMITATION = "Active la limitation en fonction de l'âge lors de pic d'inscription"
    ENFORCE_BANK_INFORMATION_WITH_SIRET = "Forcer les informations banquaires à être liées à un SIRET."
    FORCE_PHONE_VALIDATION = "Forcer la validation du numéro de téléphone pour devenir bénéficiaire"
    GENERATE_CASHFLOWS_BY_CRON = (
        "Active la génération automatique (via cron) des flux monétaires et fichiers de remboursement"
    )
    ID_CHECK_ADDRESS_AUTOCOMPLETION = "Autocomplétion de l'adresse lors du parcours IDCheck"
    PRICE_BOOKINGS = "Active la valorisation des réservations"
    PRO_ENABLE_UPLOAD_VENUE_IMAGE = "Active la fonctionnalité d'upload des images des lieux permanents"
    SYNCHRONIZE_ALLOCINE = "Permettre la synchronisation journalière avec Allociné"
    SYNCHRONIZE_TITELIVE_PRODUCTS = "Permettre limport journalier du référentiel des livres"
    SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION = "Permettre limport journalier des résumés des livres"
    SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS = "Permettre limport journalier des couvertures de livres"
    UPDATE_BOOKING_USED = "Permettre la validation automatique des contremarques 48h après la fin de lévènement"
    USER_PROFILING_FRAUD_CHECK = "Détection de la fraude basée sur le profil de l'utilisateur"
    # FIXME (dbaty, 2022-02-21): remove WEBAPP_V2_ENABLED when no user
    # accessed the old webapp (through its old URL) anymore. Until
    # then, this flag musty be kept because it is still fetched by the
    # old webapp.
    WEBAPP_V2_ENABLED = "Utiliser la nouvelle web app (décli web/v2) au lieu de l'ancienne"
    SHOW_INVOICES_ON_PRO_PORTAL = "Activer l'affichage des remboursements sur le portail pro"
    INCLUDE_LEGACY_PAYMENTS_FOR_REIMBURSEMENTS = (
        "Inclure les anciens modèles de données pour le téléchargement des remboursements "
    )
    ENABLE_PRO_ACCOUNT_CREATION = "Permettre l'inscription des comptes professionels"
    DISABLE_ENTERPRISE_API = "Désactiver les appels à l'API entreprise"
    ENABLE_EAC_SHOWCASE_OFFER = (
        "Permet de créer des offres collectives sans date ni prix depuis le formulaire de création d’offres collectives"
    )
    ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION = "Active l'utilisation du lien avec redirection pour les offres (nécessaires pour contourner des restrictions d'iOS)"

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
    FeatureToggle.ALLOW_EMPTY_USER_PROFILING,
    FeatureToggle.ALLOW_IDCHECK_UNDERAGE_REGISTRATION,
    FeatureToggle.ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE,
    FeatureToggle.ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE,
    FeatureToggle.ENABLE_DUPLICATE_USER_RULE_WITHOUT_BIRTHDATE,
    FeatureToggle.ENABLE_EDUCONNECT_AUTHENTICATION,
    FeatureToggle.ENABLE_ID_CHECK_RETENTION,
    FeatureToggle.ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION,
    FeatureToggle.ENABLE_NATIVE_CULTURAL_SURVEY,
    FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING,
    FeatureToggle.ENABLE_NEW_VENUE_PAGES,
    FeatureToggle.ENABLE_PRO_BOOKINGS_V2,
    FeatureToggle.ENABLE_UBBLE_SUBSCRIPTION_LIMITATION,
    FeatureToggle.ENFORCE_BANK_INFORMATION_WITH_SIRET,
    FeatureToggle.FORCE_PHONE_VALIDATION,
    FeatureToggle.GENERATE_CASHFLOWS_BY_CRON,
    FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION,
    FeatureToggle.PRO_ENABLE_UPLOAD_VENUE_IMAGE,
    FeatureToggle.USER_PROFILING_FRAUD_CHECK,
    FeatureToggle.SHOW_INVOICES_ON_PRO_PORTAL,
    FeatureToggle.DISABLE_ENTERPRISE_API,
    FeatureToggle.ENABLE_EAC_SHOWCASE_OFFER,
    FeatureToggle.ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION,
)


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
