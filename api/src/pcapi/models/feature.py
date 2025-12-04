"""Feature flip related models and tools

To create a feature flag, simply add it to the FeatureToggle
enumeration and to the FEATURES_DISABLED_BY_DEFAULT list if its default
value is False.
To remove one, delete all references to this feature flag, the removal
will be automatic."""

import enum
import logging

import flask
from alembic import op
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import text

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
    API_SIRENE_AVAILABLE = "Active les fonctionnalitées liées à l'API Sirene"
    APP_ENABLE_AUTOCOMPLETE = "Active l'autocomplete sur la barre de recherche relative au rework de la homepage"
    BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS = "Active la validation d'un bénéficiaire via les contrôles de sécurité"
    DISABLE_BOOST_EXTERNAL_BOOKINGS = "Désactiver les réservations externes Boost"
    DISABLE_CDS_EXTERNAL_BOOKINGS = "Désactiver les réservations externes CDS"
    DISABLE_CGR_EXTERNAL_BOOKINGS = "Désactiver les réservations externes CGR"
    DISABLE_EMS_EXTERNAL_BOOKINGS = "Désactiver les réservations externes EMS"
    DISCORD_ENABLE_NEW_ACCESS = "Activer/Désactiver l'accès au serveur Discord à des nouveaux utilisateurs"
    DISABLE_SIRET_CHECK = "Désactiver la validation de SIRET"
    DISPLAY_DMS_REDIRECTION = "Affiche une redirection vers DMS si ID Check est KO"
    EMS_CANCEL_PENDING_EXTERNAL_BOOKING = "Annuler les réservations externes EMS qui ont échouées"
    ENABLE_ALL_CRON = "Si faux, aucune cron ne sera lancé"
    ENABLE_RECURRENT_CRON = "Si faux, aucune cron de synchronization, indexation et pricing ne sera lancé"
    ENABLE_ARTIST_INDEXATION = "Activer l'indexation des artistes depuis les offres et des offres depuis les artistes"
    ENABLE_AUTO_CLOSE_CLOSED_OFFERERS = "Fermer automatiquement les entités juridiques cessées à l'INSEE"
    ENABLE_AUTO_VALIDATION_FOR_EXTERNAL_BOOKING = (
        "Valide automatiquement après 48h les offres issues de l'api billeterie cinéma"
    )
    ENABLE_BANK_ACCOUNT_SYNC = (
        "Active la synchronisation des comptes bancaires avec l'outil finance externe (Cegid XRP Flex)"
    )
    ENABLE_BEAMER = "Active Beamer, le système de notifs du portail pro"
    ENABLE_CDS_IMPLEMENTATION = "Permet la réservation de place de cinéma avec l'API CDS"
    ENABLE_CODIR_OFFERERS_REPORT = "Active le rapport sur les entités juridiques actives pour le CODIR (tourne la nuit)"
    ENABLE_CRON_TO_UPDATE_OFFERER_STATS = "Active la mise à jour des statistiques des entités juridiques avec un cron"
    ENABLE_CHRONICLES_SYNC = "Activer la synchronisation des chroniques"
    ENABLE_CULTURAL_SURVEY = "Activer l'affichage du questionnaire des pratiques initiales pour les bénéficiaires"
    ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18 = (
        "Permet l'affichage du lien vers DMS sur la page de maintenance pour les 18 ans"
    )
    ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE = (
        "Permet l'affichage du lien vers DMS sur la page de maintenance pour les 15-17 ans"
    )
    ENABLE_DS_APPLICATION_REFUSED_FROM_ANNOTATION = "Active le refus automatique des dossiers Démarche Numérique (ex-DMS) de crédit en fonction de l'annotation d'un instructeur"
    ENABLE_DS_SYNC_FOR_USER_ACCOUNT_UPDATE_REQUESTS = (
        "Active la synchronisation des demandes de modifications avec Démarche Numérique (ex-DMS)"
    )
    ENABLE_EDUCONNECT_AUTHENTICATION = "Active l'authentification via educonnect sur l'app native"
    ENABLE_FRONT_IMAGE_RESIZING = "Active le redimensionnement sur demande des images par l'app et le web"
    ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION = "Active l'utilisation du lien avec redirection pour les offres (nécessaires pour contourner des restrictions d'iOS)"
    ENABLE_INVOICE_SYNC = (
        "Active la synchronisation des justificatifs de remboursement avec l'outil finance externe (Cegid XRP Flex)"
    )
    ENABLE_MARSEILLE = "Activer Marseille en grand dans le front"
    ENABLE_NATIVE_APP_RECAPTCHA = "Active le reCaptacha sur l'API native"
    ENABLE_NATIVE_CULTURAL_SURVEY = (
        "Active le Questionnaire des pratiques initiales natif (non TypeForm) sur l'app native et décli web"
    )
    ENABLE_OFFERS_AUTO_CLEANUP = "Active la suppression automatique des offres obsolètes"
    ENABLE_PHONE_VALIDATION = "Active la validation du numéro de téléphone"
    ENABLE_PRO_ACCOUNT_CREATION = "Permettre l'inscription des comptes professionels"
    ENABLE_SPECIAL_EVENTS_SYNC = "Activer la synchronisation des réponses aux opérations spéciales"
    ENABLE_UBBLE = "Active la vérification d'identité par Ubble"
    ENABLE_UBBLE_SUBSCRIPTION_LIMITATION = "Active la limitation en fonction de l'âge lors de pic d'inscription"
    ENABLE_VIRUSTOTAL = "Active la vérification des liens externes par VirusTotal"
    GENERATE_CASHFLOWS_BY_CRON = (
        "Active la génération automatique (via cron) des flux monétaires et fichiers de remboursement"
    )
    ID_CHECK_ADDRESS_AUTOCOMPLETION = "Autocomplétion de l'adresse lors du parcours IDCheck"
    PRICE_FINANCE_EVENTS = "Active la valorisation des évènements de finance"
    SEND_ALL_EMAILS_TO_EHP = (
        "Envoyer tous les emails en testing et staging. À activer temporairement lors de phase de test"
    )
    SYNCHRONIZE_ALLOCINE = "Permettre la synchronisation journalière avec Allociné"
    SYNCHRONIZE_TITELIVE_PRODUCTS = "Permettre limport journalier du référentiel des livres"
    SYNCHRONIZE_TITELIVE_BOOK_PRODUCTS_FROM_BIGQUERY_TABLES = (
        "Permet la synchronisation des produits livre Titelive via les tables BigQuery fournies par l'équipe Data"
    )
    SYNCHRONIZE_TITELIVE_MUSIC_PRODUCTS_FROM_BIGQUERY_TABLES = (
        "Permet la synchronisation des produits musique de Titelive via les tables BigQuery fournies par l'équipe Data"
    )
    SYNCHRONIZE_TITELIVE_API_MUSIC_PRODUCTS = (
        "Permettre l'import journalier du référentiel de la musique à travers l'API Titelive"
    )
    UPDATE_BOOKING_USED = "Permettre la validation automatique des contremarques 48h après la fin de lévènement"
    ENABLE_VENUE_STRICT_SEARCH = (
        "Active le fait d'indiquer si un lieu a un moins une offre éligible lors de l'indexation (Algolia)"
    )
    ENABLE_ZENDESK_SELL_CREATION = "Activer la création de nouvelles entrées dans Zendesk Sell (structures et lieux)"
    ENABLE_BOOST_API_INTEGRATION = "Active la réservation de places de cinéma via l'API Boost"
    ENABLE_EMS_INTEGRATION = "Active la synchronisation de stocks et la réservation via EMS"
    ENABLE_CGR_INTEGRATION = "Active la synchonisation de stocks et la réservation via CGR"
    LOG_EMS_CINEMAS_AVAILABLE_FOR_SYNC = "Stocker dans Google Drive les cinémas EMS activables"
    ENABLE_PRO_FEEDBACK = "Activer l'envoi des commentaires du portail pro vers Harvestr"
    ENABLE_MOVIE_FESTIVAL_RATE = "Activer les tarifs spéciaux pour un festival cinéma"
    USE_UNIVERSAL_LINKS = (
        "Utiliser les Universal Links au lieu des Firebase dynamic links (déprécié à partir du 25/08/2025)"
    )
    VENUE_REGULARIZATION = "Déplacement de n'importe quelle offre vers une autre venue"
    # For features under construction, a temporary feature flag must be named with the `WIP_` prefix
    WIP_ASYNCHRONOUS_CELERY_MAILS = (
        "Activer le backend de tâches asynchrones Celery pour les tâches liées à l'envoi de mails"
    )
    WIP_ASYNCHRONOUS_CELERY_BATCH_UPDATE_STATUSES = "Activer le backend de tâches asynchrones Celery pour les tâches liées à la mise à jour du statut actif des offres"
    WIP_ASYNCHRONOUS_CELERY_SPECIAL_EVENT_TYPEFORM = "Activer le backend de tâches asynchrones Celery pour les tâches liées à la mise à jour des opérations spéciales"
    WIP_ASYNCHRONOUS_CELERY_UBBLE = "Active le backend de tâches asynchrones Celery pour les tâches liées à Ubble"
    WIP_FREE_ELIGIBILITY = (
        "Activer la nouvelle éligibilité qui permet aux jeunes de 15 à 16 ans de réserver des offres gratuites"
    )
    WIP_RESTRICT_VENUE_CREATION_TO_COLLECTIVITY = (
        "Autoriser l'ajout de nouvelle structure seulement pour les collectivités"
    )
    WIP_SWITCH_VENUE = "Activer la gestion de l'espace partenaire par venue sans passer par l'offerer"
    WIP_ENABLE_FINANCE_SETTLEMENTS = "Active le workflow finance des règlements"
    WIP_ENABLE_OHO = "Activer la création d'offre individuelle sur plages horaires"
    WIP_OFFER_ARTISTS = "Active la suggestion d'artistes à la création d'une offre"
    WIP_PRO_AUTONOMOUS_ANONYMIZATION = (
        "Activer la fonctionnalité d'anonymisation autonome des données personnelles depuis le portail pro"
    )
    WIP_ENABLE_NEW_PRO_HOME = "Activer la nouvelle page d'accueil du portail pro"
    WIP_LLM_OFFER_SEARCH = "Activer la recherche par LLM dans le BO"

    def is_active(self) -> bool:
        if flask.has_request_context():
            if not hasattr(flask.request, "_cached_features"):
                setattr(
                    flask.request,
                    "_cached_features",
                    {f.name: f.isActive for f in db.session.query(Feature.name, Feature.isActive)},
                )
            return flask.request._cached_features[self.name]  # type: ignore[attr-defined]
        return db.session.query(Feature).filter_by(name=self.name).one().isActive

    def __bool__(self) -> bool:
        return self.is_active()


class Feature(PcObject, Model, DeactivableMixin):
    __tablename__ = "feature"
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False)

    @property
    def nameKey(self) -> str:
        return str(self.name).replace("FeatureToggle.", "")


FEATURES_DISABLED_BY_DEFAULT: tuple[FeatureToggle, ...] = (
    FeatureToggle.DISABLE_BOOST_EXTERNAL_BOOKINGS,
    FeatureToggle.DISABLE_CDS_EXTERNAL_BOOKINGS,
    FeatureToggle.DISABLE_CGR_EXTERNAL_BOOKINGS,
    FeatureToggle.DISABLE_EMS_EXTERNAL_BOOKINGS,
    FeatureToggle.DISPLAY_DMS_REDIRECTION,
    FeatureToggle.EMS_CANCEL_PENDING_EXTERNAL_BOOKING,
    FeatureToggle.ENABLE_AUTO_CLOSE_CLOSED_OFFERERS,
    FeatureToggle.ENABLE_AUTO_VALIDATION_FOR_EXTERNAL_BOOKING,
    FeatureToggle.ENABLE_BANK_ACCOUNT_SYNC,
    FeatureToggle.ENABLE_BEAMER,
    FeatureToggle.ENABLE_CODIR_OFFERERS_REPORT,  # only for production
    FeatureToggle.ENABLE_CRON_TO_UPDATE_OFFERER_STATS,  # only for production
    FeatureToggle.ENABLE_CULTURAL_SURVEY,
    FeatureToggle.ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18,
    FeatureToggle.ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE,
    FeatureToggle.ENABLE_DS_APPLICATION_REFUSED_FROM_ANNOTATION,
    FeatureToggle.ENABLE_DS_SYNC_FOR_USER_ACCOUNT_UPDATE_REQUESTS,
    FeatureToggle.ENABLE_EMS_INTEGRATION,
    FeatureToggle.ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION,
    FeatureToggle.ENABLE_MOVIE_FESTIVAL_RATE,
    FeatureToggle.ENABLE_OFFERS_AUTO_CLEANUP,
    FeatureToggle.ENABLE_PHONE_VALIDATION,
    FeatureToggle.ENABLE_UBBLE_SUBSCRIPTION_LIMITATION,
    FeatureToggle.ENABLE_VIRUSTOTAL,
    FeatureToggle.ENABLE_ZENDESK_SELL_CREATION,
    FeatureToggle.LOG_EMS_CINEMAS_AVAILABLE_FOR_SYNC,
    FeatureToggle.VENUE_REGULARIZATION,
    FeatureToggle.SEND_ALL_EMAILS_TO_EHP,
    FeatureToggle.SYNCHRONIZE_TITELIVE_API_MUSIC_PRODUCTS,
    FeatureToggle.WIP_ASYNCHRONOUS_CELERY_MAILS,
    FeatureToggle.WIP_ASYNCHRONOUS_CELERY_SPECIAL_EVENT_TYPEFORM,
    FeatureToggle.WIP_ASYNCHRONOUS_CELERY_BATCH_UPDATE_STATUSES,
    FeatureToggle.WIP_ENABLE_OHO,
    FeatureToggle.WIP_ENABLE_FINANCE_SETTLEMENTS,
    FeatureToggle.WIP_ENABLE_NEW_PRO_HOME,
    FeatureToggle.WIP_OFFER_ARTISTS,
    FeatureToggle.WIP_PRO_AUTONOMOUS_ANONYMIZATION,
    FeatureToggle.WIP_RESTRICT_VENUE_CREATION_TO_COLLECTIVITY,
    FeatureToggle.WIP_SWITCH_VENUE,
    FeatureToggle.WIP_LLM_OFFER_SEARCH,
    # Please keep alphabetic order
)


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
    installed_flag_names = {f[0] for f in db.session.query(Feature).with_entities(Feature.name).all()}
    defined_flag_name = {f.name for f in list(FeatureToggle)}

    to_install_flags = defined_flag_name - installed_flag_names

    for flag in to_install_flags:
        db.session.add(
            Feature(
                name=FeatureToggle[flag].name,
                description=FeatureToggle[flag].value,
                isActive=FeatureToggle[flag] not in FEATURES_DISABLED_BY_DEFAULT,
            ),
        )

    db.session.commit()


def clean_feature_flags() -> None:
    """Automatically remove old feature flags from database.

    This is done after each deployment and in tests.
    """
    installed_flag_names = {f[0] for f in db.session.query(Feature).with_entities(Feature.name).all()}
    defined_flag_name = {f.name for f in list(FeatureToggle)}

    to_remove_flags = installed_flag_names - defined_flag_name

    for flag in to_remove_flags:
        db.session.execute(text("DELETE FROM feature WHERE name = :name").bindparams(name=flag))
    db.session.commit()


def check_feature_flags_completeness() -> None:
    """Check if all feature flags are present in the database and in the code"""
    installed_flag_names = {f[0] for f in db.session.query(Feature).with_entities(Feature.name).all()}
    defined_flag_name = {f.name for f in FeatureToggle}
    extra_flags = installed_flag_names - defined_flag_name
    if extra_flags:
        logger.error(
            "The following feature flags are present in the database but not present in the code: %s",
            extra_flags,
        )
