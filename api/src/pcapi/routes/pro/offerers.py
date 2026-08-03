import logging
import typing

import sqlalchemy.orm as sa_orm
from flask_login import current_user
from flask_login import login_required

import pcapi.core.educational.exceptions as educational_exceptions
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.exceptions as finance_exceptions
import pcapi.core.finance.repository as finance_repository
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.exceptions as offerers_exceptions
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offerers.repository as offerers_repository
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
from pcapi.connectors.entreprise import api as api_entreprise
from pcapi.core.offerers import api
from pcapi.core.offerers import repository
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import resource_not_found_error
from pcapi.models.utils import get_or_404
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import finance_serialize
from pcapi.routes.serialization import headline_offer_serialize
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import public_information_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import requests
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import check_user_has_access_to_venues
from pcapi.utils.transaction_manager import atomic

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/offerers/names", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=offerers_serialize.GetOfferersNamesResponseModel, api=blueprint.pro_private_schema)
def list_offerers_names() -> offerers_serialize.GetOfferersNamesResponseModel:
    offerers = api.get_user_pending_and_validated_offerers(current_user)
    return offerers_serialize.GetOfferersNamesResponseModel.build(
        offerers_names=offerers.validated, offerers_names_with_pending_validation=offerers.pending
    )


@private_api.route("/offerers/educational", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=offerers_serialize.GetEducationalOfferersResponseModel, api=blueprint.pro_private_schema
)
def list_educational_offerers(
    query: offerers_serialize.GetEducationalOfferersQueryModel,
) -> offerers_serialize.GetEducationalOfferersResponseModel:
    offerer_id = query.offerer_id

    try:
        offerers = api.get_educational_offerers(offerer_id, current_user)

        return offerers_serialize.GetEducationalOfferersResponseModel(
            educational_offerers=[
                offerers_serialize.GetEducationalOffererResponseModel.build(offerer) for offerer in offerers
            ]
        )

    except offerers_exceptions.MissingOffererIdQueryParameter:
        raise ApiErrors({"offerer_id": "Missing query parameter"})


@private_api.route("/offerers/<int:offerer_id>", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=offerers_serialize.GetOffererResponseModel, api=blueprint.pro_private_schema)
def get_offerer(offerer_id: int) -> offerers_serialize.GetOffererResponseModel:
    check_user_has_access_to_offerer(current_user, offerer_id)
    row = repository.get_offerer_and_extradata(offerer_id)
    if not row:
        raise resource_not_found_error()
    ids_of_venues_with_offers = offerers_repository.get_ids_of_venues_with_offers([row.Offerer.id])
    venues_with_non_free_offers_without_bank_accounts = (
        offerers_repository.get_venues_with_non_free_offers_without_bank_accounts(row.Offerer.id)
    )
    return offerers_serialize.GetOffererResponseModel.build(
        row,
        ids_of_venues_with_offers,
        venues_with_non_free_offers_without_bank_accounts,
    )


@private_api.route("/offerers/<int:offerer_id>/invite", methods=["POST"])
@atomic()
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def invite_member(offerer_id: int, body: offerers_serialize.InviteMemberQueryModel) -> None:
    check_user_has_access_to_offerer(current_user, offerer_id)
    offerer = get_or_404(offerers_models.Offerer, offerer_id)
    try:
        api.invite_member(offerer, body.email, current_user)
    except offerers_exceptions.EmailAlreadyInvitedException:
        raise ApiErrors({"email": "Une invitation a déjà été envoyée à ce collaborateur"})
    except offerers_exceptions.UserAlreadyAttachedToOffererException:
        raise ApiErrors({"email": "Ce collaborateur est déjà membre de votre structure"})


@private_api.route("/offerers/<int:offerer_id>/invite-again", methods=["POST"])
@atomic()
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def invite_member_again(offerer_id: int, body: offerers_serialize.InviteMemberQueryModel) -> None:
    check_user_has_access_to_offerer(current_user, offerer_id)
    offerer = get_or_404(offerers_models.Offerer, offerer_id)
    try:
        api.invite_member_again(offerer, body.email)
    except offerers_exceptions.InviteAgainImpossibleException:
        raise ApiErrors({"email": "Impossible de renvoyer une invitation pour ce collaborateur"})


@private_api.route("/offerers/<int:offerer_id>/members", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=offerers_serialize.GetOffererMembersResponseModel, api=blueprint.pro_private_schema)
def get_offerer_members(offerer_id: int) -> offerers_serialize.GetOffererMembersResponseModel:
    check_user_has_access_to_offerer(current_user, offerer_id)
    offerer = get_or_404(offerers_models.Offerer, offerer_id)
    members = api.get_offerer_members(offerer)
    return offerers_serialize.GetOffererMembersResponseModel(
        members=[
            offerers_serialize.GetOffererMemberResponseModel(email=member[0], status=member[1]) for member in members
        ]
    )


@private_api.route("/offerers", methods=["POST"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=201,
    response_model=public_information_serialize.PostOffererResponseModel,
    api=blueprint.pro_private_schema,
)
def create_offerer(
    body: offerers_serialize.CreateOffererBodyModel,
) -> public_information_serialize.PostOffererResponseModel:
    siren_info = api_entreprise.get_siren_open_data(body.siren)
    if not siren_info.active:
        raise ApiErrors(errors={"siren": ["SIREN is no longer active"]})
    body.name = siren_info.name
    assert siren_info.address  # helps mypy
    body.postal_code = siren_info.address.postal_code
    if api.is_user_offerer_already_exist(current_user, body.siren):
        # As this endpoint does not only allow to create an offerer, but also handles
        # a large part of `user_offerer` business logic (see `api.create_offerer` below)
        # That check is needed here. Otherwise, we might try to create an already existing user_offerer
        raise ApiErrors(errors={"user_offerer": ["Votre compte est déjà rattaché à cette structure."]})

    try:
        user_offerer = api.create_offerer(current_user, body, insee_data=siren_info)
    except offerers_exceptions.NotACollectivity:
        raise ApiErrors(errors={"user_offerer": ["Le rattachement est permis seulement pour les collectivités"]})

    return public_information_serialize.PostOffererResponseModel.model_validate(user_offerer.offerer)


@private_api.route("/offerers/<int:offerer_id>/bank-accounts", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=offerers_serialize.GetOffererBankAccountsResponseModel, api=blueprint.pro_private_schema
)
def get_offerer_bank_accounts_and_attached_venues(
    offerer_id: int,
) -> offerers_serialize.GetOffererBankAccountsResponseModel:
    check_user_has_access_to_offerer(current_user, offerer_id)
    offerer = repository.get_offerer_with_bank_accounts(offerer_id)
    if not offerer:
        raise resource_not_found_error()

    return offerers_serialize.GetOffererBankAccountsResponseModel(
        id=offerer.id,
        bank_accounts=[
            finance_serialize.BankAccountResponseModel.model_validate(bank_account)
            for bank_account in offerer.bankAccounts
        ],
        managed_venues=[
            finance_serialize.ManagedVenue(
                id=venue.id,
                name=venue.name,
                common_name=venue.publicName,
                siret=venue.siret,
                has_pricing_point=bool(venue.pricing_point_links),
                bank_account_id=venue.bankAccountLinks[0].bankAccountId if venue.bankAccountLinks else None,
                state=venue.state,
            )
            for venue in offerer.managedVenues
        ],
    )


@private_api.route("/offerers/<int:offerer_id>/bank-accounts/<int:bank_account_id>", methods=["PATCH"])
@atomic()
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def link_venue_to_bank_account(
    offerer_id: int, bank_account_id: int, body: offerers_serialize.LinkVenueToBankAccountBodyModel
) -> None:
    check_user_has_access_to_offerer(current_user, offerer_id)
    bank_account = finance_repository.get_bank_account_with_current_venues_links(offerer_id, bank_account_id)
    if bank_account is None:
        raise resource_not_found_error()
    try:
        finance_api.update_bank_account_venues_links(current_user, bank_account, body.venues_ids)
    except finance_exceptions.VenueAlreadyLinkedToAnotherBankAccount:
        raise ApiErrors(
            errors={
                "venuesIds": [
                    "Une ou plusieurs structures sélectionnées sont déjà rattachées à un autre compte bancaire."
                ]
            }
        )


def get_offers_with_headlines_and_mediations(
    ids: typing.Collection[int],
) -> typing.Collection[offers_models.Offer]:
    return (
        db.session.query(offers_models.Offer)
        .filter(offers_models.Offer.id.in_(ids))
        .options(
            sa_orm.selectinload(offers_models.Offer.mediations),
            sa_orm.joinedload(offers_models.Offer.product).selectinload(offers_models.Product.productMediations),
            sa_orm.selectinload(offers_models.Offer.headlineOffers),
        )
        .distinct()
        .all()
    )


def _map_top_offers_to_existing_offers(
    top_offers: typing.Collection[offerers_api.OfferViewsModel],
) -> dict[offerers_api.OfferViewsModel, offers_models.Offer]:
    offers = get_offers_with_headlines_and_mediations([int(o.offer_id) for o in top_offers])
    offers_mapping = {offer.id: offer for offer in offers}

    top_offers_to_offers_mapping = {top_offer: offers_mapping.get(int(top_offer.offer_id)) for top_offer in top_offers}

    return {top_offer: offer for top_offer, offer in top_offers_to_offers_mapping.items() if offer is not None}


def _is_headline_offer(offer: offers_models.Offer) -> bool:
    return len([ho for ho in offer.headlineOffers if ho.isActive]) > 0


@private_api.route("/venues/<int:venue_id>/offers-statistics", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=200,
    api=blueprint.pro_private_schema,
    response_model=offerers_serialize.GetVenueStatsResponseModel,
)
def get_venue_offers_stats(venue_id: int) -> offerers_serialize.GetVenueStatsResponseModel:
    venue = get_or_404(offerers_models.Venue, venue_id)
    check_user_has_access_to_venues(current_user, [venue.id])

    stats = api.get_venue_offers_statistics(venue_id)

    # top offers come from ClickHouse but need extra data from Postgres
    # offers for serialization.
    offers_mapping = _map_top_offers_to_existing_offers(stats.top_offers)

    # filter top offer without a known offer, just in case.
    # -> a missing offer is very (very) unlikely but it can happen
    top_offers = [to for to in stats.top_offers if to in offers_mapping]
    top_offers = sorted(top_offers, key=lambda o: o.rank)

    return offerers_serialize.GetVenueStatsResponseModel(
        venue_id=venue_id,
        json_data=offerers_serialize.VenueStatsDataModel(
            total_views_last_30_days=stats.total_views_last_30_days,
            top_offers=[
                offerers_serialize.TopOffersResponseData(
                    offerId=offers_mapping[top_offer].id,
                    numberOfViews=top_offer.views,
                    offerName=offers_mapping[top_offer].name,
                    image=offers_api.build_offer_image(offers_mapping[top_offer]),
                    isHeadlineOffer=_is_headline_offer(offers_mapping[top_offer]),
                )
                for top_offer in top_offers
            ],
            daily_views=[
                offerers_serialize.VenueDailyViewModel(day=row.day, views=row.views) for row in stats.daily_views
            ],
        ),
    )


@private_api.route("/offerers/<int:offerer_id>/v2/stats", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=200,
    api=blueprint.pro_private_schema,
    response_model=offerers_serialize.GetOffererV2StatsResponseModel,
    deprecated=True,
)
def get_offerer_v2_stats(offerer_id: int) -> offerers_serialize.GetOffererV2StatsResponseModel:
    """
    Deprecated.
    Please use GET /venues/<venue_id>/offers-statistics instead.
    """
    check_user_has_access_to_offerer(current_user, offerer_id)
    try:
        stats = api.get_offerer_v2_stats(offerer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise resource_not_found_error()

    return offerers_serialize.GetOffererV2StatsResponseModel.model_validate(stats)


@private_api.route("/offerers/<int:offerer_id>/offerer_addresses", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=200,
    api=blueprint.pro_private_schema,
    response_model=offerers_serialize.GetOffererAddressesResponseModel,
)
def get_offerer_addresses(
    offerer_id: int, query: offerers_serialize.GetOffererAddressesQueryModel
) -> offerers_serialize.GetOffererAddressesResponseModel:
    check_user_has_access_to_offerer(current_user, offerer_id)

    offerer_addresses = repository.get_offerer_addresses(offerer_id, with_offers_option=query.with_offers_option)

    return offerers_serialize.GetOffererAddressesResponseModel(
        [
            offerers_serialize.GetOffererAddressResponseModel.model_validate(offerer_address)
            for offerer_address in offerer_addresses
        ]
    )


@private_api.route("/venues/<int:venue_id>/headline-offer", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=headline_offer_serialize.HeadLineOfferResponseModel,
    api=blueprint.pro_private_schema,
    on_success_status=200,
)
def get_venue_headline_offer(
    venue_id: int,
) -> headline_offer_serialize.HeadLineOfferResponseModel:
    check_user_has_access_to_venues(current_user, [venue_id])

    try:
        venue_headline_offer = repository.get_venue_headline_offer(venue_id)
    except sa_orm.exc.NoResultFound:
        raise resource_not_found_error()

    return headline_offer_serialize.HeadLineOfferResponseModel.model_validate(venue_headline_offer)


@private_api.route("/offerers/<int:offerer_id>/synchronize-onboarding", methods=["POST"])
@atomic()
@login_required
@spectree_serialize(
    api=blueprint.pro_private_schema,
    on_success_status=204,
)
def synchronize_offerer_onboarding(offerer_id: int) -> None:
    check_user_has_access_to_offerer(current_user, offerer_id)

    try:
        if api.is_allowed_on_adage(offerer_id):
            return
        has_adage_id: bool | None = api.synchronize_from_adage_and_check_registration(offerer_id)
        if has_adage_id:
            return
    except (educational_exceptions.AdageException, requests.exceptions.RequestException) as exception:
        has_adage_id = None
        logger.error(
            "Error while checking Adage status",
            extra={
                "offerer_id": offerer_id,
                "error": str(exception),
            },
        )

    try:
        has_ds_application = api.synchronize_from_ds_and_check_application(offerer_id)
    except Exception as exception:
        has_ds_application = None
        logger.error(
            "Error while checking Adage status",
            extra={
                "offerer_id": offerer_id,
                "error": str(exception),
            },
        )

    if has_adage_id is None and has_ds_application is None:
        raise ApiErrors(errors={"eligibility": ["Le statut de la structure n'a pas pu être vérifié"]}, status_code=400)
