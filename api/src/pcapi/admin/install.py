from enum import Enum

from flask import Flask
from flask_admin.base import Admin
from sqlalchemy.orm.session import Session

from pcapi.admin.custom_views import inapp_messages
from pcapi.admin.custom_views import offer_view
from pcapi.admin.custom_views.admin_user_view import AdminUserView
from pcapi.admin.custom_views.allocine_pivot_view import AllocinePivotView
from pcapi.admin.custom_views.api_key_view import ApiKeyView
from pcapi.admin.custom_views.beneficiary_import_view import BeneficiaryImportView
from pcapi.admin.custom_views.beneficiary_user_view import BeneficiaryUserView
from pcapi.admin.custom_views.booking_view import BookingView
from pcapi.admin.custom_views.category_view import CategoryView
from pcapi.admin.custom_views.category_view import SubcategoryView
from pcapi.admin.custom_views.criteria_view import CriteriaView
from pcapi.admin.custom_views.cultural_survey_view import CulturalSurveyView
from pcapi.admin.custom_views.custom_reimbursement_rule_view import CustomReimbursementRuleView
from pcapi.admin.custom_views.feature_view import FeatureView
from pcapi.admin.custom_views.many_offers_operations_view import ManyOffersOperationsView
from pcapi.admin.custom_views.offerer_tag_view import OffererTagView
from pcapi.admin.custom_views.offerer_view import OffererView
from pcapi.admin.custom_views.partner_user_view import PartnerUserView
from pcapi.admin.custom_views.pro_user_view import ProUserView
from pcapi.admin.custom_views.provider_view import ProviderView
from pcapi.admin.custom_views.support_view import view
from pcapi.admin.custom_views.suspend_fraudulent_users_by_email_providers import (
    SuspendFraudulentUsersByEmailProvidersView,
)
from pcapi.admin.custom_views.user_email_history_view import UserEmailHistoryView
from pcapi.admin.custom_views.user_offerer_view import UserOffererView
from pcapi.admin.custom_views.venue_provider_view import VenueProviderView
from pcapi.admin.custom_views.venue_view import VenueForOffererSubview
from pcapi.admin.custom_views.venue_view import VenueView
import pcapi.core.criteria.models as criteria_models
from pcapi.core.educational import models as educational_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.core.offers.models import OfferValidationConfig
from pcapi.core.payments.models import CustomReimbursementRule
from pcapi.core.providers.models import AllocinePivot
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users.models import User
from pcapi.core.users.models import UserEmailHistory
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.feature import Feature

from . import base_configuration
from . import templating
from .custom_views.suspend_fraudulent_users_by_ids import SuspendFraudulentUsersByUserIdsView


class Category(Enum):
    def __str__(self) -> str:
        return str(self.value)

    OFFRES_STRUCTURES_LIEUX = "Offres, Lieux & Structures"
    USERS = "Utilisateurs"
    CUSTOM_OPERATIONS = "Autres fonctionnalités"
    SUPPORT = "Support"


def install_admin(app: Flask, session: Session) -> None:
    admin = Admin(
        name="Back Office du Pass Culture",
        url="/pc/back-office/",
        index_view=base_configuration.AdminIndexView(url="/pc/back-office/"),
        template_mode="bootstrap4",
    )
    admin.init_app(app)
    install_views(admin, session)


def install_views(admin: Admin, session: Session) -> None:
    admin.add_view(
        offer_view.OfferView(offers_models.Offer, session, name="Offres", category=Category.OFFRES_STRUCTURES_LIEUX)
    )
    admin.add_view(
        view.BeneficiaryView(
            User, session, name="Bénéficiaires", endpoint="support_beneficiary", category=Category.SUPPORT
        )
    )
    admin.add_view(
        offer_view.OfferForVenueSubview(
            offers_models.Offer,
            session,
            name="Offres pour un lieu",
            endpoint="offer_for_venue",
        )
    )
    admin.add_view(
        CriteriaView(
            criteria_models.Criterion,
            session,
            name="Tags des offres et des lieux",
            category=Category.OFFRES_STRUCTURES_LIEUX,
        )
    )
    admin.add_view(
        OffererTagView(
            offerers_models.OffererTag, session, name="Tags des structures", category=Category.OFFRES_STRUCTURES_LIEUX
        )
    )
    admin.add_view(
        OffererView(offerers_models.Offerer, session, name="Structures", category=Category.OFFRES_STRUCTURES_LIEUX)
    )
    admin.add_view(VenueView(offerers_models.Venue, session, name="Lieux", category=Category.OFFRES_STRUCTURES_LIEUX))
    admin.add_view(
        VenueForOffererSubview(
            offerers_models.Venue,
            session,
            name="Lieux pour une structure",
            endpoint="venue_for_offerer",
        )
    )
    admin.add_view(
        UserOffererView(
            offerers_models.UserOfferer,
            session,
            name="Lien Utilisateurs/Structures",
            category=Category.OFFRES_STRUCTURES_LIEUX,
        )
    )
    admin.add_view(
        ProUserView(
            User,
            session,
            name="Comptes Pros",
            category=Category.USERS,
            endpoint="pro_users",
        )
    )
    admin.add_view(
        VenueProviderView(
            VenueProvider,
            session,
            name="Imports automatiques",
            endpoint="venue_providers",
            category=Category.CUSTOM_OPERATIONS,
        )
    )
    admin.add_view(
        AdminUserView(
            User,
            session,
            name="Comptes admin",
            category=Category.USERS,
            endpoint="admin_users",
        )
    )
    admin.add_view(
        BeneficiaryUserView(
            User,
            session,
            name="Comptes Bénéficiaires",
            category=Category.USERS,
            endpoint="beneficiary_users",
        )
    )
    admin.add_view(
        PartnerUserView(
            User, session, name="Comptes Jeune et Grand Public", category=Category.USERS, endpoint="partner_users"
        )
    )
    admin.add_view(FeatureView(Feature, session, name="Feature Flipping", category=None))
    admin.add_view(BeneficiaryImportView(BeneficiaryImport, session, name="Imports DMS", category=Category.USERS))
    admin.add_view(ApiKeyView(offerers_models.ApiKey, session, name="Clés API", category=Category.USERS))
    admin.add_view(
        UserEmailHistoryView(
            UserEmailHistory,
            session,
            name="Historique des modifications emails",
            category=Category.USERS,
            endpoint="user_email_history",
        )
    )
    admin.add_view(
        AllocinePivotView(AllocinePivot, session, name="Pivot Allocine", category=Category.OFFRES_STRUCTURES_LIEUX)
    )
    admin.add_view(
        ProviderView(
            Provider,
            session,
            name="Fournisseurs d'import",
            endpoint="providers",
            category=Category.CUSTOM_OPERATIONS,
        )
    )
    admin.add_view(
        ManyOffersOperationsView(
            name="Opérations sur plusieurs offres",
            endpoint="many_offers_operations",
            category=Category.CUSTOM_OPERATIONS,
        )
    )
    admin.add_view(
        BookingView(
            name="Réservations",
            endpoint="bookings",
            category=Category.CUSTOM_OPERATIONS,
        )
    )
    admin.add_view(
        offer_view.ValidationOfferView(
            offers_models.Offer,
            session,
            name="Validation",
            endpoint="validation",
            category=Category.CUSTOM_OPERATIONS,
        )
    )
    admin.add_view(
        offer_view.ValidationCollectiveOfferView(
            educational_models.CollectiveOffer,
            session,
            name="Validation d'offres collectives",
            endpoint="validation-collective-offer",
            category=Category.CUSTOM_OPERATIONS,
        )
    )

    admin.add_view(
        offer_view.ValidationCollectiveOfferTemplateView(
            educational_models.CollectiveOfferTemplate,
            session,
            name="Validation d'offres collectives vitrines",
            endpoint="validation-collective-offer-template",
            category=Category.CUSTOM_OPERATIONS,
        )
    )

    admin.add_view(
        offer_view.ImportConfigValidationOfferView(
            OfferValidationConfig,
            session,
            name="Configuration des règles de fraude",
            endpoint="fraud_rules_configuration",
            category=Category.CUSTOM_OPERATIONS,
        )
    )

    admin.add_view(
        SuspendFraudulentUsersByEmailProvidersView(
            name="Suspension d'utilisateurs via noms de domaine",
            endpoint="suspend_fraud_users_by_email_providers",
            category=Category.CUSTOM_OPERATIONS,
        )
    )

    admin.add_view(
        SuspendFraudulentUsersByUserIdsView(
            name="Suspension d'utilisateurs via identifiants",
            endpoint="suspend_fraud_users_by_user_ids",
            category=Category.CUSTOM_OPERATIONS,
        )
    )

    admin.add_view(
        CategoryView(
            name="Catégories",
            endpoint="categories",
            category=Category.CUSTOM_OPERATIONS,
        )
    )

    admin.add_view(
        CulturalSurveyView(
            name="Questionnaire de pratiques initiales",
            endpoint="cultural_survey_answers",
            category=Category.CUSTOM_OPERATIONS,
        )
    )

    admin.add_view(
        SubcategoryView(
            name="Sous-catégories",
            endpoint="subcategories",
            category=Category.CUSTOM_OPERATIONS,
        )
    )
    admin.add_view(
        inapp_messages.MessageView(
            subscription_models.SubscriptionMessage,
            session,
            name="Messages utilisateurs dans l'app",
            category=Category.CUSTOM_OPERATIONS,
        )
    )

    admin.add_view(
        CustomReimbursementRuleView(
            CustomReimbursementRule,
            session,
            name="Règles de remboursement personnalisées",
            category=Category.CUSTOM_OPERATIONS,
        )
    )


def install_admin_autocomplete_views() -> None:
    from pcapi.admin import autocomplete  # pylint: disable=unused-import


def install_admin_template_filters(app: Flask) -> None:
    app.jinja_env.filters["yesno"] = templating.yesno
    app.jinja_env.filters["subscription_status_format"] = templating.subscription_status_format
    app.jinja_env.filters["fraud_check_status_format"] = templating.fraud_check_status_format
    app.jinja_env.filters["eligibility_format"] = templating.eligibility_format
    app.jinja_env.filters["suspension_event_format"] = templating.suspension_event_format
    app.jinja_env.filters["suspension_reason_format"] = templating.suspension_reason_format
    app.jinja_env.filters["account_state_format"] = templating.account_state_format
