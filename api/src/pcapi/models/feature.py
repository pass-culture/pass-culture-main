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
    ENABLE_CRON_TO_UPDATE_OFFERER_STATS = "Active la mise à jour des statistiques des offrers avec un cron"
    ENABLE_CULTURAL_SURVEY = "Activer l'affichage du questionnaire des pratiques initiales pour les bénéficiaires"
    ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18 = (
        "Permet l'affichage du lien vers DMS sur la page de maintenance pour les 18 ans"
    )
    ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE = (
        "Permet l'affichage du lien vers DMS sur la page de maintenance pour les 15-17 ans"
    )
    ENABLE_EDUCONNECT_AUTHENTICATION = "Active l'authentification via educonnect sur l'app native"
    ENABLE_FRONT_IMAGE_RESIZING = "Active le redimensionnement sur demande des images par l'app et le web"
    ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION = "Active l'utilisation du lien avec redirection pour les offres (nécessaires pour contourner des restrictions d'iOS)"
    ENABLE_NATIVE_APP_RECAPTCHA = "Active le reCaptacha sur l'API native"
    ENABLE_NATIVE_CULTURAL_SURVEY = (
        "Active le Questionnaire des pratiques initiales natif (non TypeForm) sur l'app native et décli web"
    )
    ENABLE_PHONE_VALIDATION = "Active la validation du numéro de téléphone"
    ENABLE_PRO_ACCOUNT_CREATION = "Permettre l'inscription des comptes professionels"
    ENABLE_PRO_BOOKINGS_V2 = "Activer l'affichage de la page booking avec la nouvelle architecture."

    ENABLE_UBBLE = "Active la vérification d'identité par Ubble"
    ENABLE_UBBLE_SUBSCRIPTION_LIMITATION = "Active la limitation en fonction de l'âge lors de pic d'inscription"
    GENERATE_CASHFLOWS_BY_CRON = (
        "Active la génération automatique (via cron) des flux monétaires et fichiers de remboursement"
    )
    ID_CHECK_ADDRESS_AUTOCOMPLETION = "Autocomplétion de l'adresse lors du parcours IDCheck"
    PRICE_FINANCE_EVENTS = "Active la valorisation des évènements de finance"
    SYNCHRONIZE_ALLOCINE = "Permettre la synchronisation journalière avec Allociné"
    SYNCHRONIZE_TITELIVE_PRODUCTS = "Permettre limport journalier du référentiel des livres"
    SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION = "Permettre l'import journalier des résumés des livres"
    SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS = "Permettre l'import journalier des couvertures de livres"
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
    ENABLE_SWITCH_ALLOCINE_SYNC_TO_EMS_SYNC = "Activer le passage automatique des synchronisations Allociné à EMS"
    LOG_EMS_CINEMAS_AVAILABLE_FOR_SYNC = "Stocker dans Google Drive les cinémas EMS activables"
    # For features under construction, a temporary feature flag must be named with the `WIP_` prefix
    WIP_BEHIND_L7_LOAD_BALANCER = "À activer/désactiver en même temps que le load balancer L7"
    WIP_ENABLE_OFFER_CREATION_API_V1 = "Active la création d'offres via l'API v1"
    WIP_ENABLE_REMINDER_MARKETING_MAIL_METADATA_DISPLAY = "Changer le template d'email de confirmation de réservation"
    WIP_ENABLE_TRUSTED_DEVICE = "Active la fonctionnalité d'appareil de confiance"
    WIP_ENABLE_SUSPICIOUS_EMAIL_SEND = "Active l'envoie d'email lors de la détection d'une connexion suspicieuse"
    WIP_ENABLE_SATISFACTION_SURVEY = "Activer l'affichage du questionnaire de satisfaction adage"
    WIP_MANDATORY_BOOKING_CONTACT = "Rend obligatoire offer.bookingContact pour les offres retirables"
    WIP_ENABLE_BOOST_PREFIXED_EXTERNAL_BOOKING = "Active les réservations externes boost avec préfixe"
    WIP_ENABLE_DIFFUSE_HELP = "Activer l'affichage de l'aide diffuse adage"
    WIP_ENABLE_EVENTS_WITH_TICKETS_FOR_PUBLIC_API = "Activer la création d'évènements avec tickets dans l'API publique"
    WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY = "Activer le nouveau parcours de dépôt de coordonnées bancaires"
    WIP_ENABLE_DOUBLE_MODEL_WRITING = "Activer la double écriture des coordonnées bancaires"
    WIP_CATEGORY_SELECTION = "Activer la nouvelle sélection de catégories"
    WIP_ENABLE_RATE_LIMITING = "Active le rate limiting"
    WIP_ENABLE_SEARCH_HISTORY_ADAGE = "Activer la possibilité de voir l'historique des recherches sur adage"
    WIP_ENABLE_COMPLIANCE_CALL = "Activer les appels à l'API Compliance pour donner un score aux offres"
    WIP_ENABLE_MOCK_UBBLE = "Utiliser le mock Ubble à la place du vrai Ubble"
    WIP_ENABLE_BOOST_SHOWTIMES_FILTER = "Activer le filtre pour les requêtes showtimes Boost"
    WIP_ENABLE_FORMAT = "Activer le remplacement des catégories/sous-catégories par les formats"
    WIP_ENABLE_DISCOVERY = "Activer la page de découverte dans adage"
    WIP_ENABLE_GOOGLE_SSO = "Activer la connexion SSO pour les jeunes"
    WIP_ENABLE_FINANCE_INCIDENT = "Active les incidents de finance"
    WIP_ENABLE_MARSEILLE = "Activer Marseille en grand"
    WIP_GOOGLE_MAPS_VENUE_IMAGES = "Activer l'affichage des images des lieux importées depuis Google Maps"
    WIP_PARTNER_PAGE = 'Activer la nouvelle version des pages "Partenaire"'
    WIP_ENABLE_PRO_SIDE_NAV = "Refonte de la navigation de l'app pro"

    def is_active(self) -> bool:
        if flask.has_request_context():
            if not hasattr(flask.request, "_cached_features"):
                setattr(
                    flask.request,
                    "_cached_features",
                    {f.name: f.isActive for f in db.session.query(Feature.name, Feature.isActive)},
                )
            return flask.request._cached_features[self.name]  # type: ignore [attr-defined]
        return Feature.query.filter_by(name=self.name).one().isActive


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
    FeatureToggle.ENABLE_CHARLIE_BOOKINGS_API,
    FeatureToggle.ENABLE_CULTURAL_SURVEY,
    FeatureToggle.ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE,
    FeatureToggle.ENABLE_EAC_FINANCIAL_PROTECTION,
    FeatureToggle.ENABLE_EMS_INTEGRATION,
    FeatureToggle.ENABLE_FRONT_IMAGE_RESIZING,
    FeatureToggle.ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION,
    FeatureToggle.ENABLE_PRO_BOOKINGS_V2,
    FeatureToggle.ENABLE_UBBLE_SUBSCRIPTION_LIMITATION,
    FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION,
    FeatureToggle.ENABLE_EAC_FINANCIAL_PROTECTION,
    FeatureToggle.ENABLE_ZENDESK_SELL_CREATION,
    FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION,
    FeatureToggle.SYNCHRONIZE_TITELIVE_API_MUSIC_PRODUCTS,
    FeatureToggle.LOG_EMS_CINEMAS_AVAILABLE_FOR_SYNC,
    FeatureToggle.ENABLE_SWITCH_ALLOCINE_SYNC_TO_EMS_SYNC,
    FeatureToggle.WIP_CATEGORY_SELECTION,
    FeatureToggle.WIP_ENABLE_COMPLIANCE_CALL,
    FeatureToggle.WIP_ENABLE_DIFFUSE_HELP,
    FeatureToggle.WIP_ENABLE_EVENTS_WITH_TICKETS_FOR_PUBLIC_API,
    FeatureToggle.WIP_ENABLE_MOCK_UBBLE,
    FeatureToggle.WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY,
    FeatureToggle.WIP_ENABLE_REMINDER_MARKETING_MAIL_METADATA_DISPLAY,
    FeatureToggle.WIP_ENABLE_SATISFACTION_SURVEY,
    FeatureToggle.WIP_ENABLE_SEARCH_HISTORY_ADAGE,
    FeatureToggle.WIP_ENABLE_SUSPICIOUS_EMAIL_SEND,
    FeatureToggle.WIP_ENABLE_TRUSTED_DEVICE,
    FeatureToggle.WIP_ENABLE_BOOST_SHOWTIMES_FILTER,
    FeatureToggle.WIP_BEHIND_L7_LOAD_BALANCER,
    FeatureToggle.WIP_ENABLE_FORMAT,
    FeatureToggle.WIP_ENABLE_DISCOVERY,
    FeatureToggle.WIP_ENABLE_GOOGLE_SSO,
    FeatureToggle.WIP_ENABLE_MARSEILLE,
    FeatureToggle.WIP_GOOGLE_MAPS_VENUE_IMAGES,  # FIXME Abdelmoujib: remove when feature is ready https://passculture.atlassian.net/browse/PC-26459
    FeatureToggle.WIP_PARTNER_PAGE,
    FeatureToggle.ENABLE_CRON_TO_UPDATE_OFFERER_STATS,
    FeatureToggle.WIP_ENABLE_PRO_SIDE_NAV,
)

if settings.IS_PROD or settings.IS_STAGING:
    FEATURES_DISABLED_BY_DEFAULT += (FeatureToggle.WIP_ENABLE_OFFER_CREATION_API_V1,)
    FEATURES_DISABLED_BY_DEFAULT += (FeatureToggle.WIP_ENABLE_FINANCE_INCIDENT,)

if settings.IS_TESTING:
    testing_features_disabled_by_default = set(FEATURES_DISABLED_BY_DEFAULT)
    features_to_enable = {
        FeatureToggle.ENABLE_CHARLIE_BOOKINGS_API,
        FeatureToggle.WIP_CATEGORY_SELECTION,
        FeatureToggle.WIP_ENABLE_EVENTS_WITH_TICKETS_FOR_PUBLIC_API,
        FeatureToggle.WIP_ENABLE_OFFER_CREATION_API_V1,
    }

    FEATURES_DISABLED_BY_DEFAULT = tuple(testing_features_disabled_by_default - features_to_enable)


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
