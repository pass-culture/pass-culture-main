import logging

import sqlalchemy.orm as sa_orm
from flask_login import current_user
from flask_login import login_required

import pcapi.core.educational.exceptions as educational_exceptions
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.exceptions as finance_exceptions
import pcapi.core.finance.repository as finance_repository
import pcapi.core.offerers.exceptions as offerers_exceptions
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.repository as offers_repository
from pcapi import settings
from pcapi.connectors.api_recaptcha import ReCaptchaException
from pcapi.connectors.api_recaptcha import check_web_recaptcha_token
from pcapi.connectors.big_query.queries.offerer_stats import DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE
from pcapi.connectors.big_query.queries.offerer_stats import TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE
from pcapi.connectors.entreprise import api as api_entreprise
from pcapi.core.offerers import api
from pcapi.core.offerers import repository
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.utils import get_or_404
from pcapi.repository.session_management import atomic
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import headline_offer_serialize
from pcapi.routes.serialization import offerers_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import requests
from pcapi.utils.rest import check_user_has_access_to_offerer

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/offerers/names", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(response_model=offerers_serialize.GetOfferersNamesResponseModel, api=blueprint.pro_private_schema)
def list_offerers_names(
    query: offerers_serialize.GetOfferersNamesQueryModel,
) -> offerers_serialize.GetOfferersNamesResponseModel:
    if query.offerer_id is not None:
        offerers = db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.id == query.offerer_id)
    else:
        offerers = repository.get_all_offerers_for_user(
            user=current_user,
            validated=query.validated,
            include_non_validated_user_offerers=not query.validated_for_user,
        )
        offerers = offerers.order_by(offerers_models.Offerer.name, offerers_models.Offerer.id)
        offerers = offerers.distinct(offerers_models.Offerer.name, offerers_models.Offerer.id)

    offerers = offerers.options(
        sa_orm.load_only(
            offerers_models.Offerer.id, offerers_models.Offerer.name, offerers_models.Offerer.allowedOnAdage
        )
    )

    return offerers_serialize.GetOfferersNamesResponseModel(
        offerersNames=[offerers_serialize.GetOffererNameResponseModel.from_orm(offerer) for offerer in offerers]
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
            educationalOfferers=[
                offerers_serialize.GetEducationalOffererResponseModel.from_orm(offerer) for offerer in offerers
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
        raise ResourceNotFoundError()
    return offerers_serialize.GetOffererResponseModel.from_orm(row)


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
@login_required
@spectree_serialize(
    on_success_status=201, response_model=offerers_serialize.PostOffererResponseModel, api=blueprint.pro_private_schema
)
def create_offerer(body: offerers_serialize.CreateOffererQueryModel) -> offerers_serialize.PostOffererResponseModel:
    siren_info = api_entreprise.get_siren_open_data(body.siren)
    if not siren_info.active:
        raise ApiErrors(errors={"siren": ["SIREN is no longer active"]})
    body.name = siren_info.name
    assert siren_info.address  # helps mypy
    body.postalCode = siren_info.address.postal_code
    if api.is_user_offerer_already_exist(current_user, body.siren):
        # As this endpoint does not only allow to create an offerer, but also handles
        # a large part of `user_offerer` business logic (see `api.create_offerer` below)
        # That check is needed here. Otherwise, we might try to create an already existing user_offerer
        raise ApiErrors(errors={"user_offerer": ["Votre compte est déjà rattaché à cette structure."]})

    try:
        user_offerer = api.create_offerer(current_user, body, insee_data=siren_info)
    except offerers_exceptions.NotACollectivity:
        raise ApiErrors(errors={"user_offerer": ["Le rattachement est permis seulement pour les collectivités"]})
    return offerers_serialize.PostOffererResponseModel.from_orm(user_offerer.offerer)


@private_api.route("/offerers/<int:offerer_id>/dashboard", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=offerers_serialize.OffererStatsResponseModel,
    api=blueprint.pro_private_schema,
)
def get_offerer_stats_dashboard_url(
    offerer_id: int,
) -> offerers_serialize.OffererStatsResponseModel:
    offerer = get_or_404(offerers_models.Offerer, offerer_id)
    check_user_has_access_to_offerer(current_user, offerer.id)
    url = api.get_metabase_stats_iframe_url(offerer, venues=offerer.managedVenues)
    return offerers_serialize.OffererStatsResponseModel(dashboardUrl=url)


@private_api.route("/offerers/new", methods=["POST"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=201, response_model=offerers_serialize.PostOffererResponseModel, api=blueprint.pro_private_schema
)
def save_new_onboarding_data(
    body: offerers_serialize.SaveNewOnboardingDataQueryModel,
) -> offerers_serialize.PostOffererResponseModel:
    try:
        check_web_recaptcha_token(
            body.token,
            settings.RECAPTCHA_SECRET,
            original_action="saveNewOnboardingData",
            minimal_score=settings.RECAPTCHA_MINIMAL_SCORE,
        )
    except ReCaptchaException:
        raise ApiErrors({"token": "The given token is invalid"})
    try:
        user_offerer = api.create_from_onboarding_data(current_user, body)
    except offerers_exceptions.InactiveSirenException:
        raise ApiErrors({"siret": "SIRET is no longer active"})
    except offerers_exceptions.NotACollectivity:
        raise ApiErrors({"siret": "SIRET doesn't belong to a collectivity"})
    return offerers_serialize.PostOffererResponseModel.from_orm(user_offerer.offerer)


@private_api.route("/offerers/<int:offerer_id>/bank-accounts", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=offerers_serialize.GetOffererBankAccountsResponseModel, api=blueprint.pro_private_schema
)
def get_offerer_bank_accounts_and_attached_venues(
    offerer_id: int,
) -> offerers_serialize.GetOffererBankAccountsResponseModel:
    check_user_has_access_to_offerer(current_user, offerer_id)
    offerer_bank_accounts = repository.get_offerer_bank_accounts(offerer_id)
    if not offerer_bank_accounts:
        raise ResourceNotFoundError()
    return offerers_serialize.GetOffererBankAccountsResponseModel.from_orm(offerer_bank_accounts)


@private_api.route("/offerers/<int:offerer_id>/bank-accounts/<int:bank_account_id>", methods=["PATCH"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def link_venue_to_bank_account(
    offerer_id: int, bank_account_id: int, body: offerers_serialize.LinkVenueToBankAccountBodyModel
) -> None:
    check_user_has_access_to_offerer(current_user, offerer_id)
    bank_account = finance_repository.get_bank_account_with_current_venues_links(offerer_id, bank_account_id)
    if bank_account is None:
        raise ResourceNotFoundError()
    try:
        finance_api.update_bank_account_venues_links(current_user, bank_account, body.venues_ids)
    except finance_exceptions.VenueAlreadyLinkedToAnotherBankAccount as exc:
        raise ApiErrors({"code": "VENUE_ALREADY_LINKED_TO_ANOTHER_BANK_ACCOUNT", "message": str(exc)}, status_code=400)


@private_api.route("/offerers/<int:offerer_id>/stats", methods=["GET"])
@login_required
@spectree_serialize(
    on_success_status=200,
    api=blueprint.pro_private_schema,
    response_model=offerers_serialize.GetOffererStatsResponseModel,
)
def get_offerer_stats(offerer_id: int) -> offerers_serialize.GetOffererStatsResponseModel:
    check_user_has_access_to_offerer(current_user, offerer_id)
    stats = api.get_offerer_stats_data(offerer_id)
    if not stats:
        return offerers_serialize.GetOffererStatsResponseModel(
            offererId=offerer_id,
            syncDate=None,
            jsonData=offerers_serialize.OffererStatsDataModel(dailyViews=[], topOffers=[], totalViewsLast30Days=0),
        )
    top_offers = next((el for el in stats if el.table == TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE), None)
    if top_offers:
        top_offers_data = top_offers.jsonData["top_offers"]
        top_offers_data = offers_repository.get_offers_data_from_top_offers(top_offers_data)
        total_views_last_30_days = top_offers.jsonData.get("total_views_last_30_days", 0)
    else:
        top_offers_data = []
        total_views_last_30_days = 0

    # It's impossible to have top offers data without daily offerer views data
    # So we can safely assume that the next call will not raise a StopIteration
    # If it does we want the error in Sentry
    daily_offerer_views = next(el for el in stats if el.table == DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE)
    daily_offerer_views_data = daily_offerer_views.jsonData["daily_views"]
    return offerers_serialize.GetOffererStatsResponseModel.build(
        offerer_id=offerer_id,
        syncDate=min(top_offers.syncDate, daily_offerer_views.syncDate) if top_offers else daily_offerer_views.syncDate,
        dailyViews=daily_offerer_views_data,
        topOffers=top_offers_data,
        total_views_last_30_days=total_views_last_30_days,
    )


@private_api.route("/offerers/<int:offerer_id>/v2/stats", methods=["GET"])
@login_required
@spectree_serialize(
    on_success_status=200,
    api=blueprint.pro_private_schema,
    response_model=offerers_serialize.GetOffererV2StatsResponseModel,
)
def get_offerer_v2_stats(offerer_id: int) -> offerers_serialize.GetOffererV2StatsResponseModel:
    check_user_has_access_to_offerer(current_user, offerer_id)
    try:
        stats = api.get_offerer_v2_stats(offerer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ResourceNotFoundError()
    return offerers_serialize.GetOffererV2StatsResponseModel.from_orm(stats)


@private_api.route("/offerers/<int:offerer_id>/offerer_addresses", methods=["GET"])
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
    offerer_addresses = repository.get_offerer_addresses(offerer_id, only_with_offers=query.onlyWithOffers)
    return offerers_serialize.GetOffererAddressesResponseModel(
        __root__=[
            offerers_serialize.GetOffererAddressResponseModel.from_orm(offerer_address)
            for offerer_address in offerer_addresses
        ]
    )


@private_api.route("/offerers/<int:offerer_id>/headline-offer", methods=["GET"])
@login_required
@atomic()
@spectree_serialize(
    response_model=headline_offer_serialize.HeadLineOfferResponseModel,
    api=blueprint.pro_private_schema,
    on_success_status=200,
)
def get_offerer_headline_offer(
    offerer_id: int,
) -> headline_offer_serialize.HeadLineOfferResponseModel:
    check_user_has_access_to_offerer(current_user, offerer_id)

    try:
        offerer_headline_offer = repository.get_offerer_headline_offer(offerer_id)
    except sa_orm.exc.MultipleResultsFound:
        raise ResourceNotFoundError({"global": "Une entité juridique ne peut avoir qu’une seule offre à la une"})
    except sa_orm.exc.NoResultFound:
        raise ResourceNotFoundError()

    return headline_offer_serialize.HeadLineOfferResponseModel.from_orm(offerer_headline_offer)


@private_api.route("/offerers/<int:offerer_id>/eligibility", methods=["GET"])
@login_required
@atomic()
@spectree_serialize(
    response_model=offerers_serialize.OffererEligibilityResponseModel,
    api=blueprint.pro_private_schema,
    on_success_status=200,
)
def get_offerer_eligibility(
    offerer_id: int,
) -> offerers_serialize.OffererEligibilityResponseModel:
    check_user_has_access_to_offerer(current_user, offerer_id)

    try:
        is_allowed_on_adage = api.is_allowed_on_adage(offerer_id)
        if is_allowed_on_adage:
            return offerers_serialize.OffererEligibilityResponseModel(
                offerer_id=offerer_id,
                has_adage_id=False,
                has_ds_application=None,
                is_onboarded=True,
            )
        has_adage_id = api.synchronize_from_adage_and_check_registration(offerer_id)
        if has_adage_id:
            return offerers_serialize.OffererEligibilityResponseModel(
                offerer_id=offerer_id,
                has_adage_id=has_adage_id,
                has_ds_application=None,
                is_onboarded=True,
            )
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

    return offerers_serialize.OffererEligibilityResponseModel(
        offerer_id=offerer_id,
        has_adage_id=has_adage_id,
        has_ds_application=has_ds_application,
        is_onboarded=is_allowed_on_adage or has_adage_id or has_ds_application,
    )
