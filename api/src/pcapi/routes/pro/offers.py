import logging

from flask import request
from flask_login import current_user
from flask_login import login_required
import sqlalchemy as sqla

from pcapi import repository
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.categories.categories import TITELIVE_MUSIC_TYPES
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import exceptions
from pcapi.core.offers import models
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.repository as offers_repository
from pcapi.core.offers.validation import check_for_duplicated_price_categories
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import offers_serialize
from pcapi.routes.serialization.thumbnails_serialize import CreateThumbnailBodyModel
from pcapi.routes.serialization.thumbnails_serialize import CreateThumbnailResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import rest
from pcapi.workers.update_all_offers_active_status_job import update_all_offers_active_status_job

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/offers", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=offers_serialize.ListOffersResponseModel,
    api=blueprint.pro_private_schema,
)
def list_offers(query: offers_serialize.ListOffersQueryModel) -> offers_serialize.ListOffersResponseModel:
    paginated_offers = offers_repository.get_capped_offers_for_filters(
        user_id=current_user.id,
        user_is_admin=current_user.has_admin_role,
        offers_limit=offers_api.OFFERS_RECAP_LIMIT,
        offerer_id=query.offerer_id,
        status=query.status.value if query.status else None,
        venue_id=query.venue_id,
        category_id=query.categoryId,
        name_keywords_or_ean=query.name_or_ean,
        creation_mode=query.creation_mode,
        period_beginning_date=query.period_beginning_date,
        period_ending_date=query.period_ending_date,
        offerer_address_id=query.offerer_address_id,
    )

    return offers_serialize.ListOffersResponseModel(__root__=offers_serialize.serialize_capped_offers(paginated_offers))


@private_api.route("/offers/<int:offer_id>", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=offers_serialize.GetIndividualOfferWithAddressResponseModel,
    api=blueprint.pro_private_schema,
)
def get_offer(offer_id: int) -> offers_serialize.GetIndividualOfferWithAddressResponseModel:

    load_all: offers_repository.OFFER_LOAD_OPTIONS = [
        "mediations",
        "product",
        "price_category",
        "venue",
        "bookings_count",
        "offerer_address",
    ]
    try:
        offer = offers_repository.get_offer_by_id(offer_id, load_options=load_all)
    except exceptions.OfferNotFound:
        raise api_errors.ApiErrors(
            errors={
                "global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"],
            },
            status_code=404,
        )
    rest.check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    return offers_serialize.GetIndividualOfferWithAddressResponseModel.from_orm(offer)


@private_api.route("/offers/<int:offer_id>/stocks/", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=offers_serialize.GetStocksResponseModel,
    api=blueprint.pro_private_schema,
)
def get_stocks(offer_id: int, query: offers_serialize.StocksQueryModel) -> offers_serialize.GetStocksResponseModel:
    try:
        offer = offers_repository.get_offer_by_id(offer_id)
    except exceptions.OfferNotFound:
        raise api_errors.ApiErrors(
            errors={
                "global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"],
            },
            status_code=404,
        )
    rest.check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)
    has_stocks = offers_repository.offer_has_stocks(offer_id=offer_id)
    if has_stocks:
        filtered_stocks = offers_repository.get_filtered_stocks(
            offer_id=offer_id,
            date=query.date,
            time=query.time,
            price_category_id=query.price_category_id,
            order_by=query.order_by,
            order_by_desc=query.order_by_desc,
            venue=offer.venue,
        )
        stocks_count = filtered_stocks.count()
        filtered_and_paginated_stocks = offers_repository.get_paginated_stocks(
            stocks_query=filtered_stocks,
            page=query.page,
            stocks_limit_per_page=query.stocks_limit_per_page,
        )
        stocks = [
            offers_serialize.GetOfferStockResponseModel.from_orm(stock) for stock in filtered_and_paginated_stocks.all()
        ]
    else:
        stocks = []
        stocks_count = 0
    return offers_serialize.GetStocksResponseModel(stocks=stocks, stock_count=stocks_count, has_stocks=has_stocks)


@private_api.route("/offers/<int:offer_id>/stocks/delete", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def delete_stocks(offer_id: int, body: offers_serialize.DeleteStockListBody) -> None:
    try:
        offer = offers_repository.get_offer_by_id(offer_id)
    except exceptions.OfferNotFound:
        raise api_errors.ApiErrors(
            errors={
                "global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"],
            },
            status_code=404,
        )

    rest.check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)
    stocks_to_delete = [stock for stock in offer.stocks if stock.id in body.ids_to_delete]
    offers_api.batch_delete_stocks(stocks_to_delete)


@private_api.route("/offers/<int:offer_id>/stocks/all-delete", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def delete_all_filtered_stocks(offer_id: int, body: offers_serialize.DeleteFilteredStockListBody) -> None:
    try:
        offer = offers_repository.get_offer_by_id(offer_id)
    except exceptions.OfferNotFound:
        raise api_errors.ApiErrors(
            errors={
                "global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"],
            },
            status_code=404,
        )

    rest.check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)
    offers_repository.hard_delete_filtered_stocks(
        offer_id=offer_id,
        venue=offer.venue,
        date=body.date,
        time=body.time,
        price_category_id=body.price_category_id,
    )


@private_api.route("/offers/<int:offer_id>/stocks-stats", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=offers_serialize.StockStatsResponseModel,
    api=blueprint.pro_private_schema,
)
def get_stocks_stats(offer_id: int) -> offers_serialize.StockStatsResponseModel:
    try:
        offer = offers_repository.get_offer_by_id(offer_id)
    except exceptions.OfferNotFound:
        raise api_errors.ApiErrors(
            errors={
                "global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"],
            },
            status_code=404,
        )
    rest.check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)
    stocks_stats = offers_api.get_stocks_stats(offer_id=offer_id)
    return offers_serialize.StockStatsResponseModel(
        oldest_stock=stocks_stats.oldest_stock,
        newest_stock=stocks_stats.newest_stock,
        stock_count=stocks_stats.stock_count,
        remaining_quantity=stocks_stats.remaining_quantity,
    )


@private_api.route("/offers/delete-draft", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def delete_draft_offers(body: offers_serialize.DeleteOfferRequestBody) -> None:
    if not body.ids:
        raise api_errors.ApiErrors(
            errors={
                "global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"],
            },
            status_code=404,
        )
    query = offers_repository.get_offers_by_ids(current_user, body.ids)  # type: ignore[arg-type]
    offers_api.batch_delete_draft_offers(query)


@private_api.route("/offers", methods=["POST"])
@login_required
@spectree_serialize(
    response_model=offers_serialize.GetIndividualOfferResponseModel,
    on_success_status=201,
    api=blueprint.pro_private_schema,
)
def post_offer(body: offers_serialize.PostOfferBodyModel) -> offers_serialize.GetIndividualOfferResponseModel:
    venue: offerers_models.Venue = (
        offerers_models.Venue.query.filter(offerers_models.Venue.id == body.venue_id)
        .options(sqla.orm.joinedload(offerers_models.Venue.offererAddress))
        .first_or_404()
    )
    rest.check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    try:
        with repository.transaction():
            offer = offers_api.create_offer(
                audio_disability_compliant=body.audio_disability_compliant,
                booking_contact=body.booking_contact,
                booking_email=body.booking_email,
                description=body.description,
                duration_minutes=body.duration_minutes,
                external_ticket_office_url=body.external_ticket_office_url,
                extra_data=offers_serialize.deserialize_extra_data(body.extra_data),
                is_duo=body.is_duo,
                is_national=body.is_national,
                mental_disability_compliant=body.mental_disability_compliant,
                motor_disability_compliant=body.motor_disability_compliant,
                name=body.name,
                subcategory_id=body.subcategory_id,
                url=body.url,
                venue=venue,
                visual_disability_compliant=body.visual_disability_compliant,
                withdrawal_delay=body.withdrawal_delay,
                withdrawal_details=body.withdrawal_details,
                withdrawal_type=body.withdrawal_type,
                is_from_private_api=True,
            )

    except exceptions.OfferCreationBaseException as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return offers_serialize.GetIndividualOfferResponseModel.from_orm(offer)


@private_api.route("/offers/publish", methods=["PATCH"])
@login_required
@spectree_serialize(
    on_success_status=200,
    on_error_statuses=[404, 403],
    api=blueprint.pro_private_schema,
    response_model=offers_serialize.GetIndividualOfferResponseModel,
)
def patch_publish_offer(
    body: offers_serialize.PatchOfferPublishBodyModel,
) -> offers_serialize.GetIndividualOfferResponseModel:
    with repository.transaction():
        with db.session.no_autoflush:
            try:
                offerer = offerers_repository.get_by_offer_id(body.id)
            except offerers_exceptions.CannotFindOffererForOfferId:
                raise api_errors.ApiErrors(
                    {"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404
                )

            rest.check_user_has_access_to_offerer(current_user, offerer.id)

            offer = offers_repository.get_offer_and_extradata(body.id)
            if offer is None:
                raise api_errors.ApiErrors({"offer": ["Cette offre n’existe pas"]}, status_code=404)
            if not offers_repository.offer_has_bookable_stocks(offer.id):
                raise api_errors.ApiErrors({"offer": "Cette offre n’a pas de stock réservable"}, 400)
            offers_api.publish_offer(offer, current_user)
            return offers_serialize.GetIndividualOfferResponseModel.from_orm(offer)


@private_api.route("/offers/active-status", methods=["PATCH"])
@login_required
@spectree_serialize(
    response_model=None,
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def patch_offers_active_status(body: offers_serialize.PatchOfferActiveStatusBodyModel) -> None:
    query = offers_repository.get_offers_by_ids(current_user, body.ids)
    if body.is_active:
        query = offers_repository.exclude_offers_from_inactive_venue_provider(query)
    offers_api.batch_update_offers(query, {"isActive": body.is_active})


@private_api.route("/offers/all-active-status", methods=["PATCH"])
@login_required
@spectree_serialize(
    response_model=None,
    on_success_status=202,
    api=blueprint.pro_private_schema,
)
def patch_all_offers_active_status(
    body: offers_serialize.PatchAllOffersActiveStatusBodyModel,
) -> offers_serialize.PatchAllOffersActiveStatusResponseModel:
    filters = {
        "user_id": current_user.id,
        "is_user_admin": current_user.has_admin_role,
        "offerer_id": body.offerer_id,
        "status": body.status,
        "venue_id": body.venue_id,
        "category_id": body.category_id,
        "name_or_ean": body.name_or_ean,
        "creation_mode": body.creation_mode,
        "period_beginning_date": body.period_beginning_date,
        "period_ending_date": body.period_ending_date,
    }
    update_all_offers_active_status_job.delay(filters, body.is_active)
    return offers_serialize.PatchAllOffersActiveStatusResponseModel()


@private_api.route("/offers/<int:offer_id>", methods=["PATCH"])
@login_required
@spectree_serialize(
    response_model=offers_serialize.GetIndividualOfferResponseModel,
    api=blueprint.pro_private_schema,
)
def patch_offer(
    offer_id: int, body: offers_serialize.PatchOfferBodyModel
) -> offers_serialize.GetIndividualOfferResponseModel:
    offer = models.Offer.query.options(
        sqla.orm.joinedload(models.Offer.stocks).joinedload(models.Stock.bookings),
        sqla.orm.joinedload(models.Offer.venue).joinedload(offerers_models.Venue.managingOfferer),
        sqla.orm.joinedload(models.Offer.product),
    ).get(offer_id)
    if not offer:
        raise api_errors.ResourceNotFoundError

    rest.check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)
    update_body = body.dict(exclude_unset=True)
    try:
        with repository.transaction():
            offer = offers_api.update_offer(
                offer,
                audioDisabilityCompliant=update_body.get("audioDisabilityCompliant", offers_api.UNCHANGED),
                bookingContact=update_body.get("bookingContact", offers_api.UNCHANGED),
                bookingEmail=update_body.get("bookingEmail", offers_api.UNCHANGED),
                description=update_body.get("description", offers_api.UNCHANGED),
                durationMinutes=update_body.get("durationMinutes", offers_api.UNCHANGED),
                externalTicketOfficeUrl=update_body.get("externalTicketOfficeUrl", offers_api.UNCHANGED),
                extraData=(
                    offers_serialize.deserialize_extra_data(update_body["extraData"])
                    if update_body.get("extraData")
                    else offers_api.UNCHANGED
                ),
                isActive=update_body.get("isActive", offers_api.UNCHANGED),
                isDuo=update_body.get("isDuo", offers_api.UNCHANGED),
                isNational=update_body.get("isNational", offers_api.UNCHANGED),
                mentalDisabilityCompliant=update_body.get("mentalDisabilityCompliant", offers_api.UNCHANGED),
                motorDisabilityCompliant=update_body.get("motorDisabilityCompliant", offers_api.UNCHANGED),
                name=update_body.get("name", offers_api.UNCHANGED),
                url=update_body.get("url", offers_api.UNCHANGED),
                visualDisabilityCompliant=update_body.get("visualDisabilityCompliant", offers_api.UNCHANGED),
                withdrawalDelay=update_body.get("withdrawalDelay", offers_api.UNCHANGED),
                withdrawalDetails=update_body.get("withdrawalDetails", offers_api.UNCHANGED),
                withdrawalType=update_body.get("withdrawalType", offers_api.UNCHANGED),
                shouldSendMail=update_body.get("shouldSendMail") or False,
                is_from_private_api=True,
            )
    except (exceptions.OfferCreationBaseException, exceptions.OfferEditionBaseException) as error:
        raise api_errors.ApiErrors(error.errors, status_code=400)

    return offers_serialize.GetIndividualOfferResponseModel.from_orm(offer)


@private_api.route("/offers/thumbnails/", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=201,
    response_model=CreateThumbnailResponseModel,
    api=blueprint.pro_private_schema,
)
def create_thumbnail(form: CreateThumbnailBodyModel) -> CreateThumbnailResponseModel:
    try:
        offer = offers_repository.get_offer_by_id(form.offer_id)
    except exceptions.OfferNotFound:
        raise api_errors.ApiErrors(
            errors={
                "global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"],
            },
            status_code=404,
        )
    rest.check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    image_as_bytes = form.get_image_as_bytes(request)

    with transaction():
        thumbnail = offers_api.create_mediation(
            user=current_user,
            offer=offer,
            credit=form.credit,
            image_as_bytes=image_as_bytes,
            crop_params=form.crop_params,
        )

    return CreateThumbnailResponseModel(id=thumbnail.id, url=thumbnail.thumbUrl, credit=thumbnail.credit)  # type: ignore[arg-type]


@private_api.route("/offers/thumbnails/<int:offer_id>", methods=["DELETE"])
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def delete_thumbnail(offer_id: int) -> None:
    offer = models.Offer.query.get_or_404(offer_id)

    rest.check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    with transaction():
        offers_api.delete_mediation(offer=offer)


@private_api.route("/offers/categories", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=offers_serialize.CategoriesResponseModel,
    api=blueprint.pro_private_schema,
)
def get_categories() -> offers_serialize.CategoriesResponseModel:
    return offers_serialize.CategoriesResponseModel(
        categories=[
            offers_serialize.CategoryResponseModel.from_orm(category) for category in categories.ALL_CATEGORIES
        ],
        subcategories=[
            offers_serialize.SubcategoryResponseModel.from_orm(subcategory)
            for subcategory in subcategories.ALL_SUBCATEGORIES
        ],
    )


@private_api.route("/offers/music-types", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=offers_serialize.GetMusicTypesResponse,
    api=blueprint.pro_private_schema,
)
def get_music_types() -> offers_serialize.GetMusicTypesResponse:
    return offers_serialize.GetMusicTypesResponse(
        __root__=[
            offers_serialize.MusicTypeResponse(
                gtl_id=music_type.gtl_id, label=music_type.label, canBeEvent=music_type.can_be_event
            )
            for music_type in TITELIVE_MUSIC_TYPES
        ]
    )


def _get_offer_for_price_categories_upsert(
    offer_id: int, price_category_edition_payload: list[offers_serialize.EditPriceCategoryModel]
) -> models.Offer | None:
    return (
        models.Offer.query.outerjoin(models.Offer.stocks.and_(sqla.not_(models.Stock.isEventExpired)))
        .outerjoin(
            models.Offer.priceCategories.and_(
                models.PriceCategory.id.in_([price_category.id for price_category in price_category_edition_payload])
            )
        )
        .outerjoin(models.PriceCategoryLabel, models.PriceCategory.priceCategoryLabel)
        .options(sqla.orm.contains_eager(models.Offer.stocks))
        .options(
            sqla.orm.contains_eager(models.Offer.priceCategories).contains_eager(
                models.PriceCategory.priceCategoryLabel
            )
        )
        .filter(models.Offer.id == offer_id)
        .one_or_none()
    )


@private_api.route("/offers/<int:offer_id>/price_categories", methods=["POST"])
@login_required
@spectree_serialize(
    response_model=offers_serialize.GetIndividualOfferResponseModel,
    api=blueprint.pro_private_schema,
)
def post_price_categories(
    offer_id: int, body: offers_serialize.PriceCategoryBody
) -> offers_serialize.GetIndividualOfferResponseModel:
    price_categories_to_create = [
        price_category
        for price_category in body.price_categories
        if isinstance(price_category, offers_serialize.CreatePriceCategoryModel)
    ]
    price_categories_to_edit = [
        price_category
        for price_category in body.price_categories
        if isinstance(price_category, offers_serialize.EditPriceCategoryModel)
    ]

    new_labels_and_prices = {(p.label, p.price) for p in price_categories_to_create}
    check_for_duplicated_price_categories(new_labels_and_prices, offer_id)

    offer = _get_offer_for_price_categories_upsert(offer_id, price_categories_to_edit)
    if not offer:
        raise api_errors.ApiErrors({"offer_id": ["L'offre avec l'id %s n'existe pas" % offer_id]}, status_code=400)
    rest.check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    existing_price_categories_by_id = {category.id: category for category in offer.priceCategories}

    with repository.transaction():
        for price_category_to_create in price_categories_to_create:
            offers_api.create_price_category(offer, price_category_to_create.label, price_category_to_create.price)

        for price_category_to_edit in price_categories_to_edit:
            if price_category_to_edit.id not in existing_price_categories_by_id:
                raise api_errors.ApiErrors(
                    {"price_category_id": ["Le tarif avec l'id %s n'existe pas" % price_category_to_edit.id]},
                    status_code=400,
                )
            data = price_category_to_edit.dict(exclude_unset=True)
            offers_api.edit_price_category(
                offer,
                price_category=existing_price_categories_by_id[data["id"]],
                label=data.get("label", offers_api.UNCHANGED),
                price=data.get("price", offers_api.UNCHANGED),
            )

    return offers_serialize.GetIndividualOfferResponseModel.from_orm(offer)


@private_api.route("/offers/<int:offer_id>/price_categories/<int:price_category_id>", methods=["DELETE"])
@login_required
@spectree_serialize(api=blueprint.pro_private_schema, on_success_status=204)
def delete_price_category(offer_id: int, price_category_id: int) -> None:
    offer = models.Offer.query.get_or_404(offer_id)
    rest.check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    price_category = models.PriceCategory.query.get_or_404(price_category_id)
    offers_api.delete_price_category(offer, price_category)
