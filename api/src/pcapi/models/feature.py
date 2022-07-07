import enum
import logging

from alembic import op
import flask
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql import text

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject


logger = logging.getLogger(__name__)


class DisabledFeatureError(Exception):
    pass


class FeatureToggle(enum.Enum):
    ALLOW_IDCHECK_REGISTRATION = "Autoriser les utilisateurs de 18 ans à suivre le parcours d inscription ID Check"
    ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE = (
        "Autoriser la redirection vers Ubble (en backup) pour les utilisateurs éligibles à éduconnect"
    )
    ALLOW_IDCHECK_UNDERAGE_REGISTRATION = (
        "Autoriser les utilisateurs de moins de 15 à 17 ans à suivre le parcours d inscription ID Check"
    )
    API_SIRENE_AVAILABLE = "Active les fonctionnalitées liées à l'API Sirene"
    APP_ENABLE_AUTOCOMPLETE = "Active l'autocomplete sur la barre de recherche relative au rework de la homepage"
    APP_ENABLE_SEARCH_HOMEPAGE_REWORK = "Active les modifications concernant le rework de la recherche de la homepage"
    BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS = "Active la validation d'un bénéficiaire via les contrôles de sécurité"
    DISABLE_ENTERPRISE_API = "Désactiver les appels à l'API entreprise"
    DISABLE_USER_NAME_AND_FIRST_NAME_VALIDATION_IN_TESTING_AND_STAGING = "Désactiver la validation des noms et prénoms"
    DISPLAY_DMS_REDIRECTION = "Affiche une redirection vers DMS si ID Check est KO"
    ENABLE_AUTO_VALIDATION_FOR_EXTERNAL_BOOKING = (
        "Valide automatiquement après 48h les offres issues de l'api billeterie cinéma"
    )
    ENABLE_BACKOFFICE_API = "Autorise l'accès à l'API backoffice"
    ENABLE_CDS_IMPLEMENTATION = "Permet la réservation de place de cinéma avec l'API CDS"
    ENABLE_CULTURAL_SURVEY = "Activer l'affichage du questionnaire des pratiques initiales pour les bénéficiaires"
    ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18 = (
        "Permet l'affichage du lien vers DMS sur la page de maintenance pour les 18 ans"
    )
    ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE = (
        "Permet l'affichage du lien vers DMS sur la page de maintenance pour les 15-17 ans"
    )
    ENABLE_DUPLICATE_USER_RULE_WITHOUT_BIRTHDATE = "Utiliser la nouvelle règle de détection d'utilisateur en doublon"
    ENABLE_EDUCONNECT_AUTHENTICATION = "Active l'authentification via educonnect sur l'app native"
    ENABLE_FRONT_IMAGE_RESIZING = "Active le redimensionnement sur demande des images par l'app et le web"
    ENABLE_IDCHECK_FRAUD_CONTROLS = "Active les contrôles de sécurité en sortie du process ID Check"
    ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION = "Active l'utilisation du lien avec redirection pour les offres (nécessaires pour contourner des restrictions d'iOS)"
    ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION = (
        "Active le champ isbn obligatoire lors de la création d'offre de type LIVRE_EDITION"
    )
    ENABLE_NATIVE_APP_RECAPTCHA = "Active le reCaptacha sur l'API native"
    ENABLE_NATIVE_CULTURAL_SURVEY = (
        "Active le Questionnaire des pratiques initiales natif (non TypeForm) sur l'app native et décli web"
    )
    ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING = (
        "Active le mode debug Firebase pour l'Id Check intégrée à l'application native"
    )
    ENABLE_BANNER_ONE_YEAR = "Active la bannière des 1 an du pass sur la Home"
    ENABLE_CSV_MULTI_DOWNLOAD_BUTTON = "Active le multi-téléchargement des réservations"
    ENABLE_EDUCATIONAL_INSTITUTION_ASSOCIATION = (
        "Active l'association d'une offre collective à un établissement scolaire"
    )
    ENABLE_NEW_BOOKING_FILTERS = "Active les nouveaux filtres sur les statuts pour la page de réservations"
    ENABLE_NEW_BANK_INFORMATIONS_CREATION = (
        "Active le nouveau parcours d'ajout de coordonnées bancaires sur la page lieu"
    )
    ENABLE_NEW_VENUE_PAGES = "Utiliser la nouvelle version des pages d'edition et de creation de lieux"
    ENABLE_PHONE_VALIDATION = "Active la validation du numéro de téléphone"  # TODO (viconnex) remove when FORCE_PHONE_VALIDATION is released in production
    ENABLE_PHONE_VALIDATION_IN_STEPPER = (
        "Déplace la validation du numéro de téléphone dans le flux du parcours d'inscription"
    )
    ENABLE_PRO_ACCOUNT_CREATION = "Permettre l'inscription des comptes professionels"
    ENABLE_PRO_BOOKINGS_V2 = "Activer l'affichage de la page booking avec la nouvelle architecture."
    ENABLE_PRO_NEW_VENUE_PROVIDER_UI = "Activer le nouveau affichage de la section synchronisation sur la page lieu"
    ENABLE_UBBLE = "Active la vérification d'identité par Ubble"
    ENABLE_UBBLE_SUBSCRIPTION_LIMITATION = "Active la limitation en fonction de l'âge lors de pic d'inscription"
    ENABLE_USER_PROFILING = "Active l'étape USER_PROFILING dans le parcours d'inscription des jeunes de 18 ans"
    ENFORCE_BANK_INFORMATION_WITH_SIRET = "Forcer les informations banquaires à être liées à un SIRET."
    FORCE_PHONE_VALIDATION = "Forcer la validation du numéro de téléphone pour devenir bénéficiaire"
    GENERATE_CASHFLOWS_BY_CRON = (
        "Active la génération automatique (via cron) des flux monétaires et fichiers de remboursement"
    )
    ID_CHECK_ADDRESS_AUTOCOMPLETION = "Autocomplétion de l'adresse lors du parcours IDCheck"
    INCLUDE_LEGACY_PAYMENTS_FOR_REIMBURSEMENTS = (
        "Inclure les anciens modèles de données pour le téléchargement des remboursements "
    )
    PRICE_BOOKINGS = "Active la valorisation des réservations"
    PRO_DISABLE_EVENTS_QRCODE = "Active la possibilité de différencier le type d’envoi des billets sur une offre et le retrait du QR code sur la réservation"
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
    OFFER_FORM_V3 = "Afficher la version 3 du formulaire d'offre"
    OFFER_FORM_SUMMARY_PAGE = "Afficher la page de récapitulatif de l'offre dans le formulaire V2"
    ALLOW_ACCOUNT_UNSUSPENSION = "Activer le nouveau parcours de réactivation de compte"
    ENABLE_NEW_ALGOLIA_INDEX_ON_ADAGE = "Active l'utilisation des nouveaux indexes algolia sur adage"
    ENABLE_VENUE_STRICT_SEARCH = (
        "Active le fait d'indiquer si un lieu a un moins une offre éligible lors de l'indexation (Algolia)"
    )
    ENABLE_EDUCATIONAL_DOMAINS = "Active l'utilisation du champs domaines sur les offres collectives"
    OFFER_DRAFT_ENABLED = "Active la fonctionnalités de création d'offre en brouillon"
    ENABLE_IN_PAGE_PROFILE_FORM = "Active le formulaire d'édition de profile dans une page séparée"
    ENABLE_ADAGE_VENUE_INFORMATION = "Active la page acteur culturel"
    USE_PRICING_POINT_FOR_PRICING = "Utilise le modèle VenuePricingPointLink pour la valorisation"
    USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS = "Utilise le modèle VenueReimbursementPointLink pour les cashflows"
    ENABLE_INTERVENTION_ZONE_COLLECTIVE_OFFER = "Ajoute la gestion des zones de mobilité/intervention pour les AC."

    def is_active(self) -> bool:
        if flask.has_request_context():
            if not hasattr(flask.request, "_cached_features"):
                setattr(flask.request, "_cached_features", {})

            cached_value = flask.request._cached_features.get(self.name)  # type: ignore [attr-defined]
            if cached_value is not None:
                return cached_value

        value = Feature.query.filter_by(name=self.name).one().isActive

        if flask.has_request_context():
            flask.request._cached_features[self.name] = value  # type: ignore [attr-defined]

        return value


class Feature(PcObject, Base, Model, DeactivableMixin):  # type: ignore [valid-type, misc]
    name = Column(Text, unique=True, nullable=False)
    description = Column(String(300), nullable=False)

    @property
    def nameKey(self) -> str:
        return str(self.name).replace("FeatureToggle.", "")


FEATURES_DISABLED_BY_DEFAULT = (
    FeatureToggle.ALLOW_ACCOUNT_UNSUSPENSION,
    FeatureToggle.ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE,
    FeatureToggle.APP_ENABLE_SEARCH_HOMEPAGE_REWORK,
    FeatureToggle.DISABLE_ENTERPRISE_API,
    FeatureToggle.ENABLE_ADAGE_VENUE_INFORMATION,
    FeatureToggle.ENABLE_AUTO_VALIDATION_FOR_EXTERNAL_BOOKING,
    FeatureToggle.ENABLE_BACKOFFICE_API,
    FeatureToggle.ENABLE_CDS_IMPLEMENTATION,
    FeatureToggle.ENABLE_CULTURAL_SURVEY,
    FeatureToggle.ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE,
    FeatureToggle.ENABLE_DUPLICATE_USER_RULE_WITHOUT_BIRTHDATE,
    FeatureToggle.ENABLE_FRONT_IMAGE_RESIZING,
    FeatureToggle.ENABLE_IN_PAGE_PROFILE_FORM,
    FeatureToggle.ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION,
    FeatureToggle.ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION,
    FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING,
    FeatureToggle.ENABLE_NEW_BANK_INFORMATIONS_CREATION,
    FeatureToggle.ENABLE_NEW_VENUE_PAGES,
    FeatureToggle.ENABLE_PRO_BOOKINGS_V2,
    FeatureToggle.ENABLE_PRO_NEW_VENUE_PROVIDER_UI,
    FeatureToggle.ENABLE_UBBLE_SUBSCRIPTION_LIMITATION,
    FeatureToggle.ENABLE_USER_PROFILING,
    FeatureToggle.FORCE_PHONE_VALIDATION,
    FeatureToggle.GENERATE_CASHFLOWS_BY_CRON,
    FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION,
    FeatureToggle.OFFER_DRAFT_ENABLED,
    FeatureToggle.OFFER_FORM_SUMMARY_PAGE,
    FeatureToggle.OFFER_FORM_V3,
    FeatureToggle.PRO_DISABLE_EVENTS_QRCODE,
    FeatureToggle.USER_PROFILING_FRAUD_CHECK,
    FeatureToggle.USE_PRICING_POINT_FOR_PRICING,
    FeatureToggle.USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS,
    FeatureToggle.ENABLE_INTERVENTION_ZONE_COLLECTIVE_OFFER,
)


# FIXME (dbaty, 2022-03-15): remove this function once migrations have
# been squashed and we don't need this function anymore.
def legacy_add_feature_to_database(feature: FeatureToggle) -> None:
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


def add_feature_to_database(feature: Feature) -> None:
    """This function is to be used in the "downgrade" function of a
    migration when removing a new feature flag (so that it's added
    back if we revert the migration).
    """
    statement = text(
        """
        INSERT INTO feature (name, description, "isActive")
        VALUES (:name, :description, :is_active)
        """
    )
    statement = statement.bindparams(
        name=feature.name,
        description=feature.description,
        is_active=feature.isActive,
    )
    op.execute(statement)


def remove_feature_from_database(feature: Feature) -> None:
    """This function is to be used in the "upgrade" function of a
    migration when removing a feature flag.
    """
    statement = text("DELETE FROM feature WHERE name = :name").bindparams(name=feature.name)
    op.execute(statement)


def install_feature_flags() -> None:
    """Automatically add new feature flags to the database.

    This is done before each deployment and in tests.
    """
    installed_flag_names = {f[0] for f in Feature.query.with_entities(Feature.name).all()}
    defined_flag_name = {f.name for f in list(FeatureToggle)}

    to_install_flags = defined_flag_name - installed_flag_names
    to_remove_flags = installed_flag_names - defined_flag_name

    for flag in to_install_flags:
        db.session.add(
            Feature(  # type: ignore [call-arg]
                name=FeatureToggle[flag].name,
                description=FeatureToggle[flag].value,
                isActive=FeatureToggle[flag] not in FEATURES_DISABLED_BY_DEFAULT,
            ),
        )

    db.session.commit()

    if to_remove_flags:
        logger.error("The following feature flags are present in database but not present in code: %s", to_remove_flags)
