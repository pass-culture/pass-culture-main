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
    ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE = (
        "Autoriser la redirection vers Ubble (en backup) pour les utilisateurs éligibles à éduconnect"
    )
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
    DISPLAY_DMS_REDIRECTION = "Affiche une redirection vers DMS si ID Check est KO"
    ENABLE_AUTO_VALIDATION_FOR_EXTERNAL_BOOKING = (
        "Valide automatiquement après 48h les offres issues de l'api billeterie cinéma"
    )
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
    ENABLE_NEW_VENUE_PAGES = "Utiliser la nouvelle version des pages d'edition et de creation de lieux"
    ENABLE_PHONE_VALIDATION = "Active la validation du numéro de téléphone"
    ENABLE_PRO_ACCOUNT_CREATION = "Permettre l'inscription des comptes professionels"
    ENABLE_PRO_BOOKINGS_V2 = "Activer l'affichage de la page booking avec la nouvelle architecture."

    ENABLE_UBBLE = "Active la vérification d'identité par Ubble"
    ENABLE_UBBLE_SUBSCRIPTION_LIMITATION = "Active la limitation en fonction de l'âge lors de pic d'inscription"
    WIP_ENABLE_WITHDRAWAL_UPDATED_MAIL = (
        "Envoie un mail aux jeunes qui ont réservé lorsque les modalités de retrait d'une offre sont changées"
    )
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
    # For features under construction, a temporary feature flag must be named with the `WIP_` prefix
    WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY = "Nouveau parcours de creation d'offre optimisé"
    WIP_ENABLE_OFFER_CREATION_API_V1 = "Active la création d'offres via l'API v1"
    WIP_ENABLE_MULTI_PRICE_STOCKS = "Active la fonctionnalité multi-tarif pour les offres individuelles"
    ENABLE_CGR_INTEGRATION = "Active la synchonisation de stocks et la réservation via CGR"
    WIP_ADD_CLG_6_5_COLLECTIVE_OFFER = "Ouverture des offres collectives au 6ème et 5ème"
    WIP_ENABLE_LIKE_IN_ADAGE = "Active la possibilité de liker une offre sur adage"
    WIP_RECURRENCE = "Active l'ajout de dates récurrentes pour événements sur les offres individuelles"
    WIP_ENABLE_NEW_ONBOARDING = "Active le nouvel onboarding sans SIREN"
    WIP_ENABLE_COLLECTIVE_DMS_TRACKING = "Active le suivi du référencement DMS pour les acteurs EAC"
    WIP_ENABLE_REMINDER_MARKETING_MAIL_METADATA_DISPLAY = "Changer le template d'email de confirmation de réservation"
    WIP_ENABLE_EAC_CANCEL_30_DAYS = "EAC délai annulation 30 Jours par defaut au lieu de 15"
    WIP_ENABLE_TRUSTED_DEVICE = "Active la fonctionnalité d'appareil de confiance"
    WIP_EAC_ENABLE_NEW_AUTHENTICATION_PUBLIC_API = "Active la gestion des providers dans l'api publique EAC"
    WIP_ENABLE_COLLECTIVE_REQUEST = "Active la demande de création d'offre collective de la part des utilisateurs adage"
    WIP_ENABLE_NEW_ADAGE_HEADER = "Active le nouveau header dans l'iframe adage"
    WIP_ENABLE_COOKIES_BANNER = "Active la nouvelle bannière de cookies"
    WIP_RECURRENCE_FILTERS = "Ajoute les filtres et le tri sur la vue liste des récurrences"

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
    FeatureToggle.ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE,
    FeatureToggle.DISABLE_ENTERPRISE_API,
    FeatureToggle.DISABLE_BOOST_EXTERNAL_BOOKINGS,
    FeatureToggle.DISABLE_CDS_EXTERNAL_BOOKINGS,
    FeatureToggle.DISABLE_CGR_EXTERNAL_BOOKINGS,
    FeatureToggle.ENABLE_AUTO_VALIDATION_FOR_EXTERNAL_BOOKING,
    FeatureToggle.ENABLE_CULTURAL_SURVEY,
    FeatureToggle.ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE,
    FeatureToggle.ENABLE_DUPLICATE_USER_RULE_WITHOUT_BIRTHDATE,
    FeatureToggle.ENABLE_FRONT_IMAGE_RESIZING,
    FeatureToggle.ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION,
    FeatureToggle.ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION,
    FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING,
    FeatureToggle.ENABLE_NEW_VENUE_PAGES,
    FeatureToggle.ENABLE_PRO_BOOKINGS_V2,
    FeatureToggle.ENABLE_UBBLE_SUBSCRIPTION_LIMITATION,
    FeatureToggle.WIP_ENABLE_WITHDRAWAL_UPDATED_MAIL,
    FeatureToggle.GENERATE_CASHFLOWS_BY_CRON,
    FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION,
    FeatureToggle.PRO_DISABLE_EVENTS_QRCODE,
    FeatureToggle.ENABLE_EAC_FINANCIAL_PROTECTION,
    FeatureToggle.ENABLE_ZENDESK_SELL_CREATION,
    FeatureToggle.ENABLE_OFFERER_STATS,
    FeatureToggle.WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY,
    FeatureToggle.ENABLE_CGR_INTEGRATION,
    FeatureToggle.WIP_ADD_CLG_6_5_COLLECTIVE_OFFER,
    FeatureToggle.WIP_ENABLE_LIKE_IN_ADAGE,
    FeatureToggle.WIP_ENABLE_NEW_ONBOARDING,
    FeatureToggle.WIP_ENABLE_COLLECTIVE_DMS_TRACKING,
    FeatureToggle.WIP_ENABLE_REMINDER_MARKETING_MAIL_METADATA_DISPLAY,
    FeatureToggle.WIP_ENABLE_EAC_CANCEL_30_DAYS,
    FeatureToggle.WIP_ENABLE_TRUSTED_DEVICE,
    FeatureToggle.WIP_EAC_ENABLE_NEW_AUTHENTICATION_PUBLIC_API,
    FeatureToggle.WIP_ENABLE_COLLECTIVE_REQUEST,
    FeatureToggle.WIP_ENABLE_NEW_ADAGE_HEADER,
    FeatureToggle.WIP_ENABLE_COOKIES_BANNER,
    FeatureToggle.WIP_RECURRENCE_FILTERS,
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
