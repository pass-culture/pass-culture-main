import enum
import logging

from alembic import op
import flask
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql import text

from pcapi import settings
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject


logger = logging.getLogger(__name__)


class DisabledFeatureError(Exception):
    pass


class FeatureToggle(enum.Enum):
    ALGOLIA_BOOKINGS_NUMBER_COMPUTATION = (
        "Active le calcul du nombre des réservations lors de l'indexation des offres sur Algolia"
    )
    ALLOW_IDCHECK_REGISTRATION = "Autoriser les utilisateurs de 18 ans à suivre le parcours d inscription ID Check"
    ALLOW_IDCHECK_UNDERAGE_REGISTRATION = (
        "Autoriser les utilisateurs de moins de 15 à 17 ans à suivre le parcours d inscription ID Check"
    )
    API_ADRESSE_AVAILABLE = "Active les fonctionnalitées liées à l'API Adresse"
    API_SIRENE_AVAILABLE = "Active les fonctionnalitées liées à l'API Sirene"
    APP_ENABLE_AUTOCOMPLETE = "Active l'autocomplete sur la barre de recherche relative au rework de la homepage"
    BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS = "Active la validation d'un bénéficiaire via les contrôles de sécurité"
    DISABLE_ENTERPRISE_API = "Désactiver les appels à l'API entreprise"
    DISABLE_BOOST_EXTERNAL_BOOKINGS = "Désactiver les réservations externes Boost"
    DISABLE_CDS_EXTERNAL_BOOKINGS = "Désactiver les réservations externes CDS"
    DISABLE_CGR_EXTERNAL_BOOKINGS = "Désactiver les réservations externes CGR"
    DISABLE_EMS_EXTERNAL_BOOKINGS = "Désactiver les réservations externes EMS"
    DISPLAY_DMS_REDIRECTION = "Affiche une redirection vers DMS si ID Check est KO"
    ENABLE_AUTO_VALIDATION_FOR_EXTERNAL_BOOKING = (
        "Valide automatiquement après 48h les offres issues de l'api billeterie cinéma"
    )
    ENABLE_BEAMER = "Active Beamer, le système de notifs du portail pro"
    ENABLE_CDS_IMPLEMENTATION = "Permet la réservation de place de cinéma avec l'API CDS"
    ENABLE_CHARLIE_BOOKINGS_API = "Active la réservation via l'API Charlie"
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
    ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION = "Active l'utilisation du lien avec redirection pour les offres (nécessaires pour contourner des restrictions d'iOS)"
    ENABLE_NATIVE_APP_RECAPTCHA = "Active le reCaptacha sur l'API native"
    ENABLE_NATIVE_CULTURAL_SURVEY = (
        "Active le Questionnaire des pratiques initiales natif (non TypeForm) sur l'app native et décli web"
    )
    ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING = (
        "Active le mode debug Firebase pour l'Id Check intégrée à l'application native"
    )
    ENABLE_NEW_VENUE_PAGES = "Utiliser la nouvelle version des pages d'edition et de creation de lieux"
    ENABLE_PHONE_VALIDATION = "Active la validation du numéro de téléphone"
    ENABLE_PRO_ACCOUNT_CREATION = "Permettre l'inscription des comptes professionels"
    ENABLE_PRO_BOOKINGS_V2 = "Activer l'affichage de la page booking avec la nouvelle architecture."

    ENABLE_UBBLE = "Active la vérification d'identité par Ubble"
    ENABLE_UBBLE_SUBSCRIPTION_LIMITATION = "Active la limitation en fonction de l'âge lors de pic d'inscription"
    GENERATE_CASHFLOWS_BY_CRON = (
        "Active la génération automatique (via cron) des flux monétaires et fichiers de remboursement"
    )
    ID_CHECK_ADDRESS_AUTOCOMPLETION = "Autocomplétion de l'adresse lors du parcours IDCheck"
    INCLUDE_LEGACY_PAYMENTS_FOR_REIMBURSEMENTS = (
        "Inclure les anciens modèles de données pour le téléchargement des remboursements "
    )
    PRICE_BOOKINGS = "Active la valorisation des réservations"
    PRICE_FINANCE_EVENTS = "Active la valorisation des événements de finance"
    PRO_DISABLE_EVENTS_QRCODE = "Active la possibilité de différencier le type d’envoi des billets sur une offre et le retrait du QR code sur la réservation"
    SYNCHRONIZE_ALLOCINE = "Permettre la synchronisation journalière avec Allociné"
    SYNCHRONIZE_TITELIVE_PRODUCTS = "Permettre limport journalier du référentiel des livres"
    SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION = "Permettre limport journalier des résumés des livres"
    SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS = "Permettre limport journalier des couvertures de livres"
    SYNCHRONIZE_TITELIVE_API_MUSIC_PRODUCTS = (
        "Permettre l'import journalier du référentiel de la musique à travers l'API Titelive"
    )
    UPDATE_BOOKING_USED = "Permettre la validation automatique des contremarques 48h après la fin de lévènement"
    ENABLE_VENUE_STRICT_SEARCH = (
        "Active le fait d'indiquer si un lieu a un moins une offre éligible lors de l'indexation (Algolia)"
    )
    ENABLE_EAC_FINANCIAL_PROTECTION = (
        "Protege le pass culture contre les ministeres qui dépenseraient plus que leur budget sur les 4 derniers mois "
        "de l'année"
    )
    ENABLE_ZENDESK_SELL_CREATION = "Activer la création de nouvelles entrées dans Zendesk Sell (structures et lieux)"
    ENABLE_BOOST_API_INTEGRATION = "Active la réservation de places de cinéma via l'API Boost"
    ENABLE_OFFERER_STATS = "Active l'affichage des statistiques d'une structure sur le portail pro"
    ENABLE_EMS_INTEGRATION = "Active la synchronisation de stocks et la réservation via EMS"
    ENABLE_CGR_INTEGRATION = "Active la synchonisation de stocks et la réservation via CGR"
    # For features under construction, a temporary feature flag must be named with the `WIP_` prefix
    WIP_ENABLE_OFFER_CREATION_API_V1 = "Active la création d'offres via l'API v1"
    WIP_ADD_CLG_6_5_COLLECTIVE_OFFER = "Ouverture des offres collectives au 6ème et 5ème"
    WIP_ENABLE_LIKE_IN_ADAGE = "Active la possibilité de liker une offre sur adage"
    WIP_ENABLE_REMINDER_MARKETING_MAIL_METADATA_DISPLAY = "Changer le template d'email de confirmation de réservation"
    WIP_ENABLE_TRUSTED_DEVICE = "Active la fonctionnalité d'appareil de confiance"
    WIP_ENABLE_SUSPICIOUS_EMAIL_SEND = "Active l'envoie d'email lors de la détection d'une connexion suspicieuse"
    WIP_EAC_ENABLE_NEW_AUTHENTICATION_PUBLIC_API = "Active la gestion des providers dans l'api publique EAC"
    WIP_ENABLE_COLLECTIVE_REQUEST = "Active la demande de création d'offre collective de la part des utilisateurs adage"
    WIP_ENABLE_NEW_ADAGE_HEADER = "Active le nouveau header dans l'iframe adage"
    WIP_ENABLE_COOKIES_BANNER = "Active la nouvelle bannière de cookies"
    WIP_ENABLE_SATISFACTION_SURVEY = "Activer l'affichage du questionnaire de satisfaction adage"
    WIP_ENABLE_NEW_ADAGE_FILTERS = "Active les nouveaux filtres adage"
    WIP_MANDATORY_BOOKING_CONTACT = "Rend obligatoire offer.bookingContact pour les offres retirables"
    WIP_ENABLE_BOOST_PREFIXED_EXTERNAL_BOOKING = "Active les réservations externe boost avec préfix"
    WIP_ENABLE_NEW_USER_OFFERER_LINK = "Activer le nouvel ajout des collaborateurs"
    WIP_ENABLE_DIFFUSE_HELP = "Activer l'affichage de l'aide diffuse adage"
    WIP_ENABLE_EVENTS_WITH_TICKETS_FOR_PUBLIC_API = "Activer la création événements avec tickets dans l'API publique"
    WIP_OFFER_TO_INSTITUTION = "Activer le fléchage d'une offre à un établissement"
    WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY = "Activer le nouveau parcours de dépôt de coordonnées bancaires"
    WIP_CATEGORY_SELECTION = "Activer la nouvelle sélection de catégories"
    WIP_ENABLE_ADAGE_GEO_LOCATION = "Activer le filtre d'offres adage par géolocalisation"
    WIP_BACKOFFICE_ENABLE_REDIRECT_SINGLE_RESULT = (
        "Backoffice : Afficher directement les détails lorsque la recherche ne renvoie qu'un seul résultat"
    )
    WIP_ENABLE_SEARCH_HISTORY_ADAGE = "Activer la possibilité de voir l'historique des recherches sur adage"
    WIP_ENABLE_OFFER_RESERVATION_TAB = "Activer l'onglet réservation depuis les offres"
    WIP_ENABLE_MOCK_UBBLE = "Utiliser le mock Ubble à la place du vrai Ubble"

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


class Feature(PcObject, Base, Model, DeactivableMixin):
    name: str = Column(Text, unique=True, nullable=False)
    description: str = Column(String(300), nullable=False)

    @property
    def nameKey(self) -> str:
        return str(self.name).replace("FeatureToggle.", "")


FEATURES_DISABLED_BY_DEFAULT: tuple[FeatureToggle, ...] = (
    FeatureToggle.DISABLE_BOOST_EXTERNAL_BOOKINGS,
    FeatureToggle.DISABLE_CDS_EXTERNAL_BOOKINGS,
    FeatureToggle.DISABLE_CGR_EXTERNAL_BOOKINGS,
    FeatureToggle.DISABLE_EMS_EXTERNAL_BOOKINGS,
    FeatureToggle.DISABLE_ENTERPRISE_API,
    FeatureToggle.ENABLE_AUTO_VALIDATION_FOR_EXTERNAL_BOOKING,
    FeatureToggle.ENABLE_BEAMER,
    FeatureToggle.ENABLE_CGR_INTEGRATION,
    FeatureToggle.ENABLE_CHARLIE_BOOKINGS_API,
    FeatureToggle.ENABLE_CULTURAL_SURVEY,
    FeatureToggle.ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE,
    FeatureToggle.ENABLE_DUPLICATE_USER_RULE_WITHOUT_BIRTHDATE,
    FeatureToggle.ENABLE_EAC_FINANCIAL_PROTECTION,
    FeatureToggle.ENABLE_EMS_INTEGRATION,
    FeatureToggle.ENABLE_FRONT_IMAGE_RESIZING,
    FeatureToggle.ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION,
    FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING,
    FeatureToggle.ENABLE_NEW_VENUE_PAGES,
    FeatureToggle.ENABLE_PRO_BOOKINGS_V2,
    FeatureToggle.ENABLE_UBBLE_SUBSCRIPTION_LIMITATION,
    FeatureToggle.ENABLE_ZENDESK_SELL_CREATION,
    FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION,
    FeatureToggle.PRICE_FINANCE_EVENTS,
    FeatureToggle.PRO_DISABLE_EVENTS_QRCODE,
    FeatureToggle.SYNCHRONIZE_TITELIVE_API_MUSIC_PRODUCTS,
    FeatureToggle.WIP_ADD_CLG_6_5_COLLECTIVE_OFFER,
    FeatureToggle.WIP_BACKOFFICE_ENABLE_REDIRECT_SINGLE_RESULT,
    FeatureToggle.WIP_CATEGORY_SELECTION,
    FeatureToggle.WIP_EAC_ENABLE_NEW_AUTHENTICATION_PUBLIC_API,
    FeatureToggle.WIP_ENABLE_ADAGE_GEO_LOCATION,
    FeatureToggle.WIP_ENABLE_BOOST_PREFIXED_EXTERNAL_BOOKING,
    FeatureToggle.WIP_ENABLE_COLLECTIVE_REQUEST,
    FeatureToggle.WIP_ENABLE_DIFFUSE_HELP,
    FeatureToggle.WIP_ENABLE_EVENTS_WITH_TICKETS_FOR_PUBLIC_API,
    FeatureToggle.WIP_ENABLE_LIKE_IN_ADAGE,
    FeatureToggle.WIP_ENABLE_MOCK_UBBLE,
    FeatureToggle.WIP_ENABLE_NEW_ADAGE_FILTERS,
    FeatureToggle.WIP_ENABLE_NEW_ADAGE_HEADER,
    FeatureToggle.WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY,
    FeatureToggle.WIP_ENABLE_NEW_USER_OFFERER_LINK,
    FeatureToggle.WIP_ENABLE_OFFER_RESERVATION_TAB,
    FeatureToggle.WIP_ENABLE_REMINDER_MARKETING_MAIL_METADATA_DISPLAY,
    FeatureToggle.WIP_ENABLE_SATISFACTION_SURVEY,
    FeatureToggle.WIP_ENABLE_SEARCH_HISTORY_ADAGE,
    FeatureToggle.WIP_ENABLE_SUSPICIOUS_EMAIL_SEND,
    FeatureToggle.WIP_ENABLE_TRUSTED_DEVICE,
    FeatureToggle.WIP_OFFER_TO_INSTITUTION,
)

if settings.IS_PROD or settings.IS_STAGING:
    FEATURES_DISABLED_BY_DEFAULT += (FeatureToggle.WIP_ENABLE_OFFER_CREATION_API_V1,)


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
            Feature(
                name=FeatureToggle[flag].name,
                description=FeatureToggle[flag].value,
                isActive=FeatureToggle[flag] not in FEATURES_DISABLED_BY_DEFAULT,
            ),
        )

    db.session.commit()

    if to_remove_flags:
        logger.error("The following feature flags are present in database but not present in code: %s", to_remove_flags)
