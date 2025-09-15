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
    ENABLE_DS_APPLICATION_REFUSED_FROM_ANNOTATION = (
        "Active le refus automatique des dossiers DS (DMS) de crédit en fonction de l'annotation d'un instructeur"
    )
    ENABLE_DS_SYNC_FOR_USER_ACCOUNT_UPDATE_REQUESTS = (
        "Active la synchronisation des demandes de modifications avec DS (DMS)"
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
    SYNCHRONIZE_TITELIVE_PRODUCTS_FROM_BIGQUERY_TABLES = (
        "Permettre la synchronisation des produits Titelive via les tables BigQuery fournies par l'équipe data"
    )
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
    WIP_2025_AUTOLOGIN = "Activer l’autologin par lien lors de l’inscription au portail pro"
    WIP_2025_SIGN_UP_PARTIALLY_DIFFUSIBLE = "Activer l'inscription de structures en diffusion partielle"
    WIP_ADD_VIDEO = "Permettre aux pros d'avoir des vidéos sur leurs offres"
    WIP_ASYNCHRONOUS_CELERY_MAILS = (
        "Activer le backend de tâches asynchrones Celery pour les tâches liées à l'envoi de mails"
    )
    WIP_ASYNCHRONOUS_CELERY_CREATE_UPDATE_EAN_OFFERS = (
        "Activer le backend de tâches asynchrones Celery pour les tâches liées à la mise à jour d'offres EAN"
    )
    WIP_DISABLE_CANCEL_BOOKING_NOTIFICATION = (
        "Désactiver la notification push Batch pour l'annulation d'une réservation"
    )
    WIP_DISABLE_NOTIFY_USERS_BOOKINGS_NOT_RETRIEVED = (
        "Désactiver la notification push Batch pour les réservations sur le point d'expirer"
    )
    WIP_DISABLE_SEND_NOTIFICATIONS_FAVORITES_NOT_BOOKED = (
        "Désactiver la notification push Batch pour les favoris non-réservés"
    )
    WIP_DISABLE_TODAY_STOCK_NOTIFICATION = (
        "Désactiver la notification push Batch pour les réservations se déroulant le jour même"
    )
    WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE = (
        "Activer la nouvelle structure des offres et réservations collectives"
    )
    WIP_ENABLE_NEW_COLLECTIVE_OFFER_DETAIL_PAGE = "Activer la nouvelle page détail de l'offre réservable"
    WIP_ENABLE_NEW_FINANCE_WORKFLOW = "Active le nouveau workflow finance"
    WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE = "Activer l'association des offres collectives à des adresses."
    WIP_ENABLE_COLLECTIVE_NEW_STATUS_PUBLIC_API = (
        "Activer les autorisations liées au nouveau statut des offres collectives sur l'api publique."
    )
    WIP_ENABLE_PRO_DIDACTIC_ONBOARDING = "Activer le parcours d'onboarding didactique des acteurs culturels"
    WIP_ENABLE_PRO_DIDACTIC_ONBOARDING_AB_TEST = "Activer l'A/B test du parcours d'onboarding didactique"
    WIP_FREE_ELIGIBILITY = (
        "Activer la nouvelle éligibilité qui permet aux jeunes de 15 à 16 ans de réserver des offres gratuites"
    )
    WIP_REFACTO_FUTURE_OFFER = "Activer la nouvelle gestion des publications dans le futur"
    WIP_RESTRICT_VENUE_ATTACHMENT_TO_COLLECTIVITY = "Autoriser le rattachement seulement pour les collectivités"
    WIP_RESTRICT_VENUE_CREATION_TO_COLLECTIVITY = (
        "Autoriser l'ajout de nouvelle structure seulement pour les collectivités"
    )
    WIP_ENABLE_NEW_OFFER_CREATION_FLOW = "Activer le nouveau parcours de création d'offre"
    WIP_ENABLE_OHO = "Activer la création d'offre individuelle sur plages horaires"

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


class Feature(PcObject, Base, Model, DeactivableMixin):
    __tablename__ = "feature"
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
    FeatureToggle.ENABLE_EAC_FINANCIAL_PROTECTION,
    FeatureToggle.ENABLE_EMS_INTEGRATION,
    FeatureToggle.ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION,
    FeatureToggle.ENABLE_MOVIE_FESTIVAL_RATE,
    FeatureToggle.ENABLE_OFFERS_AUTO_CLEANUP,
    FeatureToggle.ENABLE_PHONE_VALIDATION,
    FeatureToggle.ENABLE_PRO_FEEDBACK,
    FeatureToggle.ENABLE_UBBLE_SUBSCRIPTION_LIMITATION,
    FeatureToggle.ENABLE_VIRUSTOTAL,
    FeatureToggle.ENABLE_ZENDESK_SELL_CREATION,
    FeatureToggle.LOG_EMS_CINEMAS_AVAILABLE_FOR_SYNC,
    FeatureToggle.VENUE_REGULARIZATION,
    FeatureToggle.SEND_ALL_EMAILS_TO_EHP,
    FeatureToggle.SYNCHRONIZE_TITELIVE_API_MUSIC_PRODUCTS,
    FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_FROM_BIGQUERY_TABLES,
    FeatureToggle.WIP_ADD_VIDEO,
    FeatureToggle.WIP_ASYNCHRONOUS_CELERY_MAILS,
    FeatureToggle.WIP_ASYNCHRONOUS_CELERY_CREATE_UPDATE_EAN_OFFERS,
    FeatureToggle.WIP_DISABLE_CANCEL_BOOKING_NOTIFICATION,
    FeatureToggle.WIP_DISABLE_NOTIFY_USERS_BOOKINGS_NOT_RETRIEVED,
    FeatureToggle.WIP_DISABLE_SEND_NOTIFICATIONS_FAVORITES_NOT_BOOKED,
    FeatureToggle.WIP_DISABLE_TODAY_STOCK_NOTIFICATION,
    FeatureToggle.WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE,
    FeatureToggle.WIP_ENABLE_NEW_COLLECTIVE_OFFER_DETAIL_PAGE,
    FeatureToggle.WIP_ENABLE_NEW_FINANCE_WORKFLOW,
    FeatureToggle.WIP_ENABLE_NEW_OFFER_CREATION_FLOW,
    FeatureToggle.WIP_ENABLE_OHO,
    FeatureToggle.WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE,
    FeatureToggle.WIP_ENABLE_COLLECTIVE_NEW_STATUS_PUBLIC_API,
    FeatureToggle.WIP_ENABLE_PRO_DIDACTIC_ONBOARDING_AB_TEST,
    FeatureToggle.WIP_RESTRICT_VENUE_ATTACHMENT_TO_COLLECTIVITY,
    FeatureToggle.WIP_RESTRICT_VENUE_CREATION_TO_COLLECTIVITY,
    # Please keep alphabetic order
)

if settings.IS_PROD:
    FEATURES_DISABLED_BY_DEFAULT += (
        FeatureToggle.WIP_FREE_ELIGIBILITY,
        FeatureToggle.WIP_2025_SIGN_UP_PARTIALLY_DIFFUSIBLE,
    )
if settings.IS_STAGING:
    FEATURES_DISABLED_BY_DEFAULT += (FeatureToggle.WIP_FREE_ELIGIBILITY,)


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
