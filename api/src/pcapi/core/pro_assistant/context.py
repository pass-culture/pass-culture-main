"""Anonymous context about the user's situation, given to the assistant.

Only booleans and a page identifier are sent: no id, name, email, SIREN or bank
data ever leaves our servers.
"""

import dataclasses

from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.pro_assistant import portal_map


@dataclasses.dataclass(frozen=True)
class AssistantContext:
    current_route_id: str | None = None
    has_selected_offerer: bool = False
    is_validated: bool = False
    is_closed: bool = False
    is_onboarded: bool = False
    allowed_on_adage: bool = False
    has_valid_bank_account: bool = False
    has_pending_bank_account: bool = False
    has_bank_account_with_pending_corrections: bool = False
    has_non_free_offer: bool = False
    is_caledonian: bool = False


def build_context(offerer_id: int | None, current_path: str | None) -> AssistantContext:
    """`offerer_id` access must have been checked by the caller."""
    current_route_id = portal_map.find_route_id(current_path)
    row = offerers_repository.get_offerer_and_extradata(offerer_id) if offerer_id else None
    if not row:
        return AssistantContext(current_route_id=current_route_id)

    offerer = row.Offerer
    return AssistantContext(
        current_route_id=current_route_id,
        has_selected_offerer=True,
        is_validated=offerer.isValidated or offerer.isClosed,
        is_closed=offerer.isClosed,
        is_onboarded=row.isOnboarded,
        allowed_on_adage=offerer.allowedOnAdage,
        has_valid_bank_account=row.hasValidBankAccount,
        has_pending_bank_account=row.hasPendingBankAccount,
        has_bank_account_with_pending_corrections=row.hasBankAccountWithPendingCorrections,
        has_non_free_offer=row.hasNonFreeOffer,
        is_caledonian=offerer.is_caledonian,
    )


def _yes_no(value: bool) -> str:
    return "oui" if value else "non"


def render_for_prompt(context: AssistantContext) -> str:
    current_page = portal_map.PAGES_BY_ROUTE_ID.get(context.current_route_id or "")
    lines = [
        "Contexte de l'utilisateur, calculé par le portail (fiable, anonyme) :",
        f"- page actuelle : {f'{current_page.title} ({current_page.route_id})' if current_page else 'inconnue'}",
    ]
    if not context.has_selected_offerer:
        lines.append("- aucune entité juridique sélectionnée")
        return "\n".join(lines)
    lines += [
        f"- entité juridique validée par le pass Culture : {_yes_no(context.is_validated)}",
        f"- entité juridique fermée : {_yes_no(context.is_closed)}",
        f"- inscription terminée (onboarding) : {_yes_no(context.is_onboarded)}",
        f"- référencée sur ADAGE (peut proposer des offres collectives) : {_yes_no(context.allowed_on_adage)}",
        f"- compte bancaire validé : {_yes_no(context.has_valid_bank_account)}",
        f"- compte bancaire en cours de validation : {_yes_no(context.has_pending_bank_account)}",
        f"- compte bancaire avec corrections demandées : {_yes_no(context.has_bank_account_with_pending_corrections)}",
        f"- a au moins une offre payante : {_yes_no(context.has_non_free_offer)}",
        f"- située en Nouvelle-Calédonie : {_yes_no(context.is_caledonian)}",
    ]
    return "\n".join(lines)
