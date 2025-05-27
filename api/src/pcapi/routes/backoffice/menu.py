import dataclasses
import typing

from flask import request
from flask import url_for
from flask_login import current_user

from pcapi.routes.backoffice import utils


@dataclasses.dataclass
class MenuItem:
    label: str
    url_name: str
    permissions: list[str] | None = None
    url_kwargs_getter: typing.Callable | None = None
    settings: list[str] | None = None

    @property
    def is_available(self) -> bool:
        if not getattr(current_user, "backoffice_profile", None):
            return False

        conditions: list[bool] = []
        for permission in self.permissions or []:
            conditions.append(utils.has_current_user_permission(permission))

        for setting in self.settings or []:
            conditions.append(utils.get_setting(setting))

        # If no conditions then return True as there is no check for the menu item
        return all(conditions)

    @property
    def url(self) -> str:
        kwargs = {}
        if self.url_kwargs_getter:
            kwargs = self.url_kwargs_getter()
        return url_for(self.url_name, **kwargs)

    @property
    def is_active(self) -> bool:
        return request.path == self.url


@dataclasses.dataclass
class MenuSection:
    label: str
    all_items: list[MenuItem]

    @property
    def is_available(self) -> bool:
        return any(item.is_available for item in self.all_items)

    @property
    def items(self) -> list[MenuItem]:
        return [item for item in self.all_items if item.is_available]


MENU_SECTIONS = [
    MenuSection(
        label="Jeunes et grand public",
        all_items=[
            MenuItem(
                label="Jeunes bénéficiaires ou à venir",
                url_name="backoffice_web.public_accounts.search_public_accounts",
                permissions=["READ_PUBLIC_ACCOUNT"],
            ),
            MenuItem(
                label="Demandes de modifications DS",
                url_name="backoffice_web.account_update.list_account_update_requests",
                permissions=["MANAGE_ACCOUNT_UPDATE_REQUEST"],
            ),
            MenuItem(
                label="Extraction des données jeunes",
                url_name="backoffice_web.gdpr_extract.list_gdpr_user_data_extract",
                permissions=["MANAGE_PUBLIC_ACCOUNT"],
            ),
            MenuItem(
                label="Opérations spéciales",
                url_name="backoffice_web.operations.list_events",
                permissions=["READ_SPECIAL_EVENTS"],
            ),
            MenuItem(
                label="Chroniques",
                url_name="backoffice_web.chronicles.list_chronicles",
                permissions=["READ_CHRONICLE"],
            ),
            MenuItem(
                label="Tags des jeunes",
                url_name="backoffice_web.account_tag.list_account_tags",
                permissions=["READ_TAGS"],
            ),
        ],
    ),
    MenuSection(
        label="Acteurs culturels",
        all_items=[
            MenuItem(
                label="Liste des acteurs culturels",
                url_name="backoffice_web.pro.search_pro",
                permissions=["READ_PRO_ENTITY"],
            ),
            MenuItem(
                label="Entités juridiques à valider",
                url_name="backoffice_web.validation.list_offerers_to_validate",
                permissions=["READ_PRO_ENTITY"],
            ),
            MenuItem(
                label="Rattachements à valider",
                url_name="backoffice_web.validation.list_offerers_attachments_to_validate",
                permissions=["READ_PRO_ENTITY"],
            ),
            MenuItem(
                label="Tags des entités juridiques",
                url_name="backoffice_web.offerer_tag.list_offerer_tags",
                permissions=["READ_TAGS"],
            ),
            MenuItem(
                label="Offres individuelles",
                url_name="backoffice_web.offer.list_offers",
                permissions=["READ_OFFERS"],
            ),
            MenuItem(
                label="Offres collectives",
                url_name="backoffice_web.collective_offer.list_collective_offers",
                permissions=["READ_OFFERS"],
            ),
            MenuItem(
                label="Offres collectives vitrine",
                url_name="backoffice_web.collective_offer_template.list_collective_offer_templates",
                permissions=["READ_OFFERS"],
            ),
            MenuItem(
                label="Opérations sur plusieurs offres",
                url_name="backoffice_web.multiple_offers.multiple_offers_home",
                permissions=["READ_OFFERS"],
            ),
            MenuItem(
                label="Recherche EAN via Tite Live",
                url_name="backoffice_web.titelive.search_titelive",
                permissions=["READ_OFFERS"],
            ),
            MenuItem(
                label="Tags des offres et partenaires culturels",
                url_name="backoffice_web.tags.list_tags",
                permissions=["READ_TAGS"],
            ),
            MenuItem(
                label="Actions sur les partenaires culturels",
                url_name="backoffice_web.venue.list_venues",
                permissions=["READ_PRO_ENTITY", "MANAGE_PRO_ENTITY"],
            ),
            MenuItem(
                label="Préférences",
                url_name="backoffice_web.preferences.edit_preferences",
                permissions=["READ_PRO_ENTITY"],
            ),
        ],
    ),
    MenuSection(
        label="Support Pro",
        all_items=[
            MenuItem(
                label="Déplacer un SIRET",
                url_name="backoffice_web.move_siret.move_siret",
                permissions=["MOVE_SIRET"],
            ),
            MenuItem(
                label="Synchronisation Pivot",
                url_name="backoffice_web.pivots.get_pivots",
                permissions=["READ_TECH_PARTNERS"],
            ),
            MenuItem(
                label="Synchronisation partenaires techniques",
                url_name="backoffice_web.providers.list_providers",
                permissions=["READ_TECH_PARTNERS"],
            ),
            MenuItem(
                label="Tarifs dérogatoires",
                url_name="backoffice_web.reimbursement_rules.list_custom_reimbursement_rules",
                permissions=["READ_REIMBURSEMENT_RULES"],
            ),
        ],
    ),
    MenuSection(
        label="Réservations",
        all_items=[
            MenuItem(
                label="Réservations individuelles",
                url_name="backoffice_web.individual_bookings.list_individual_bookings",
                permissions=["READ_BOOKINGS"],
            ),
            MenuItem(
                label="Réservations collectives",
                url_name="backoffice_web.collective_bookings.list_collective_bookings",
                permissions=["READ_BOOKINGS"],
            ),
        ],
    ),
    MenuSection(
        label="Finance",
        all_items=[
            MenuItem(
                label="Gestion des incidents",
                url_name="backoffice_web.finance_incidents.list_incidents",
                permissions=["READ_INCIDENTS"],
            ),
        ],
    ),
    MenuSection(
        label="Fraude et conformité",
        all_items=[
            MenuItem(
                label="Règles de validation d'offres",
                url_name="backoffice_web.offer_validation_rules.list_rules",
                permissions=["PRO_FRAUD_ACTIONS"],
            ),
            MenuItem(
                label="Règles de modification de prix d'offres",
                url_name="backoffice_web.offer_price_limitation_rules.list_rules",
                permissions=["PRO_FRAUD_ACTIONS"],
            ),
            MenuItem(
                label="Suspension de comptes jeunes",
                url_name="backoffice_web.fraud.list_blacklisted_domain_names",
                permissions=["BENEFICIARY_FRAUD_ACTIONS"],
            ),
        ],
    ),
    MenuSection(
        label="Admin",
        all_items=[
            MenuItem(
                label="Mon compte backoffice",
                url_name="backoffice_web.bo_users.get_bo_user",
                url_kwargs_getter=lambda: {"user_id": current_user.id, "active_tab": "roles"},
            ),
            MenuItem(
                label="Rôles et permissions",
                url_name="backoffice_web.get_roles",
                permissions=["READ_PERMISSIONS"],
            ),
            MenuItem(
                label="Utilisateurs BackOffice",
                url_name="backoffice_web.bo_users.search_bo_users",
                permissions=["READ_ADMIN_ACCOUNTS"],
            ),
            MenuItem(
                label="Feature flipping",
                url_name="backoffice_web.list_feature_flags",
            ),
            MenuItem(
                label="Liste des sous-catégories",
                url_name="backoffice_web.get_subcategories",
            ),
        ],
    ),
    MenuSection(
        label="Dev",
        all_items=[
            MenuItem(
                label="Générateur d'utilisateurs de test",
                url_name="backoffice_web.dev.generate_user",
                settings=["ENABLE_TEST_USER_GENERATION"],
            ),
            MenuItem(
                label="Suppression d'utilisateur",
                url_name="backoffice_web.dev.delete_user",
                settings=["ENABLE_TEST_USER_GENERATION"],
            ),
            MenuItem(
                label="Liste des composants",
                url_name="backoffice_web.dev.components",
                settings=["ENABLE_BO_COMPONENT_PAGE"],
            ),
        ],
    ),
]


def get_menu_sections() -> list[MenuSection]:
    return [menu_section for menu_section in MENU_SECTIONS if menu_section.is_available]
